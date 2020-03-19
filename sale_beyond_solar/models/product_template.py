from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_sale_html = fields.Html(string="Sales Description (HTML)")
