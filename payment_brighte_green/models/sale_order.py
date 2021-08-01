from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    brighte_price = fields.Float(string="Brighte $/Week")
