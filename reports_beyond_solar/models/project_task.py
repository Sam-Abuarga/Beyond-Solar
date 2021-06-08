from odoo import api, fields, models
from odoo.modules.module import get_module_resource

import base64
import io
import pikepdf
from PyPDF2 import PdfFileReader, PdfFileWriter


class ProjectTask(models.Model):
    _inherit = 'project.task'

    welcome_pack = fields.Binary(string="Welcome Pack", attachment=True)

    def _cron_send_welcome_packs(self):
        tasks = self.search([('x_studio_send_customer_documentation', '=', False), ('x_studio_stc', '!=', False), ('x_studio_ccew', '!=', False), ('x_studio_permission_to_connect_ptc_letter', '!=', False)])
        for task in tasks:
            sale = task.sale_order_id
            if sale.invoice_status != 'invoiced':
                continue
            if any([invoice.state == 'draft' and invoice.type == 'out_invoice' for invoice in sale.invoice_ids]):
                continue
            if any([invoice.amount_residual > 0 and invoice.type == 'out_invoice' for invoice in sale.invoice_ids]):
                continue

            if sale.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel')):
                continue

            task.x_studio_send_customer_documentation = True
            task.action_create_welcome_pack()
            attachment = self.env['ir.attachment'].search([('res_model', '=', 'project.task'), ('res_id', '=', task.id), ('res_field', '=', 'welcome_pack')], limit=1)
            attachment.write({'name': 'Welcome Pack.pdf'})

            mail_template = self.env['mail.template'].browse(48)  # Welcome Pack
            email_values = {
                'attachment_ids': attachment.ids
            }
            mail_template.send_mail(task.id, force_send=True, email_values=email_values)

            if not task.x_studio_send_ccew:
                task.action_email_ccew()

            self.env.cr.commit()

    def action_create_welcome_pack(self):
        def clean_pdf(decoded_data):
            in_stream = io.BytesIO(decoded_data)
            out_stream = io.BytesIO()
            pdf = pikepdf.Pdf.open(in_stream)
            pdf.save(out_stream)
            res = out_stream.getvalue()
            in_stream.close()
            out_stream.close()
            return res

        streams = []

        annex_attachments = self.env['product.attachment']
        for line in self.sale_order_id.order_line:
            if line.product_id.datasheet_attachment_id:
                annex_attachments |= line.product_id.datasheet_attachment_id
            if line.product_id.warranty_attachment_id:
                annex_attachments |= line.product_id.warranty_attachment_id

        streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack').render_qweb_pdf(self.sale_line_id.order_id.id, {'doc_part': 1})[0]))

        if self.connection_diagram_id.pdf_attachment:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "8. Connection Diagram"})[0]))
            streams.append(io.BytesIO(base64.b64decode(self.connection_diagram_id.pdf_attachment)))

        streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack').render_qweb_pdf(self.sale_line_id.order_id.id, {'doc_part': 2})[0]))

        streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "14. Engineering Certificate for the PV Mounting Frame System"})[0]))
        path = get_module_resource('reports_beyond_solar', 'static/src/pdf', 'engineering-certificate.pdf')
        with open(path, 'rb') as file:
            streams.append(io.BytesIO(file.read()))

        streams.append(io.BytesIO(self.env.ref('project_beyond_solar.action_report_project_task_installation').render_qweb_pdf(self.id, {'title_number': True})[0]))

        if self.x_studio_ccew:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "16. Certificate of Electrical Safety"})[0]))
            streams.append(io.BytesIO(clean_pdf(base64.b64decode(self.x_studio_ccew))))

        if self.user_id.compliance_declaration_attachment:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "17. Declaration of Compliance"})[0]))
            streams.append(io.BytesIO(base64.b64decode(self.user_id.compliance_declaration_attachment)))

        if self.x_studio_permission_to_connect_ptc_letter:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "18. Permission to Connect"})[0]))
            streams.append(io.BytesIO(base64.b64decode(self.x_studio_permission_to_connect_ptc_letter)))

        if self.x_studio_stc:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "19. Small Technology Certificate Form"})[0]))
            streams.append(io.BytesIO(clean_pdf(base64.b64decode(self.x_studio_stc))))

        if self.x_studio_der_receipt:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "20. DER Receipt"})[0]))
            streams.append(io.BytesIO(clean_pdf(base64.b64decode(self.x_studio_der_receipt))))

        if annex_attachments:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "21. Annexures"})[0]))

        for att in annex_attachments:
            streams.append(io.BytesIO(base64.b64decode(att.file)))

        writer = PdfFileWriter()
        for stream in streams:
            reader = PdfFileReader(stream, strict=False)
            writer.appendPagesFromReader(reader)
        result_stream = io.BytesIO()
        writer.write(result_stream)

        data = result_stream.getvalue()
        result_stream.close()
        self.welcome_pack = base64.b64encode(data)
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/project.task/{}/welcome_pack/{}'.format(self.id, "Welcome Pack.pdf")
        }
