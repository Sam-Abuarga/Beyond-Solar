from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_serials(self):
        self.ensure_one()
        serials = []
        for move in self.move_ids:
            for line in move.move_line_ids:
                if line.lot_id or line.lot_name:
                    serials.append(line.lot_id.name or line.lot_name)
        serials = ", ".join(serials)
        return serials
