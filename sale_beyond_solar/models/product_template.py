from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_sale_html = fields.Html(string="Sales Description (HTML)")

    warranty_attachment_id = fields.Many2one(comodel_name='product.attachment', string="Warranty Attachment", domain=[('type', '=', 'warranty')])
    datasheet_attachment_id = fields.Many2one(comodel_name='product.attachment', string="Datasheet Attachment", domain=[('type', '=', 'datasheet')])

    mppt_single = fields.Boolean(string="Condense Multiple Units")
    mppt_ids = fields.One2many(comodel_name='product.mppt', inverse_name='product_tmpl_id', string="MPPTs")
    mppt_count = fields.Integer(string="MPPT count")
    mppt_inputs = fields.Integer(string="Input per MPPT")

    @api.constrains('mppt_count', 'mppt_inputs')
    def _check_mppts(self):
        for rec in self:
            to_delete = rec.mppt_ids

            for x in range(rec.mppt_count):
                for y in range(rec.mppt_inputs):
                    match = to_delete.filtered(lambda m: m.mppt_number == x and m.input_number == y)
                    if match:
                        to_delete -= match
                    else:
                        self.env['product.mppt'].create({
                            'product_tmpl_id': rec.id,
                            'mppt_number': x,
                            'input_number': y,
                        })
            to_delete.unlink()
