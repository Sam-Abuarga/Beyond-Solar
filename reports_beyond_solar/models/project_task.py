from odoo import api, fields, models
from odoo.modules.module import get_module_resource

import base64
import io
from PyPDF2 import PdfFileReader, PdfFileWriter


class ProjectTask(models.Model):
    _inherit = 'project.task'

    welcome_pack = fields.Binary(string="Welcome Pack")

    def action_create_welcome_pack(self):
        streams = [io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack').render_qweb_pdf(self.sale_line_id.order_id.id)[0])]

        streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "Array Mounting Certificate"})[0]))
        path = get_module_resource('reports_beyond_solar', 'static/src/pdf', 'engineering-certificate.pdf')
        with open(path, 'rb') as file:
            streams.append(io.BytesIO(file.read()))

        streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "Test & Commission"})[0]))
        streams.append(io.BytesIO(self.env.ref('project_beyond_solar.action_report_project_task_installation').render_qweb_pdf(self.id)[0]))

        if self.x_studio_ccew:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "Certificate of Electrical Safety"})[0]))
            streams.append(io.BytesIO(base64.b64decode(self.x_studio_ccew)))

        if self.x_studio_permission_to_connect_ptc_letter:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "Permission to Connect"})[0]))
            streams.append(io.BytesIO(base64.b64decode(self.x_studio_permission_to_connect_ptc_letter)))

        if self.x_studio_stc:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "Small Technology Certificate Form"})[0]))
            streams.append(io.BytesIO(base64.b64decode(self.x_studio_stc)))

        if self.x_studio_der_receipt:
            streams.append(io.BytesIO(self.env.ref('reports_beyond_solar.action_report_welcome_pack_heading').render_qweb_pdf(1, {'title': "DER Receipt"})[0]))
            streams.append(io.BytesIO(base64.b64decode(self.x_studio_der_receipt)))

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
