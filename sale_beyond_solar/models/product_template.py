from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_sale_html = fields.Html(string="Sales Description (HTML)")

    warranty_attachment_id = fields.Many2one(comodel_name='product.attachment', string="Warranty Attachment", domain=[('type', '=', 'warranty')])
    datasheet_attachment_id = fields.Many2one(comodel_name='product.attachment', string="Datasheet Attachment", domain=[('type', '=', 'datasheet')])
