from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_ids = fields.Many2many(comodel_name='stock.production.lot', string="Serials", compute='_compute_lot_ids')

    def _compute_lot_ids(self):
        for rec in self:
            rec.lot_ids = rec.mapped('move_ids.move_line_ids.lot_id')
