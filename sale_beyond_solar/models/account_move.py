from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def generate_payment_link(self):
        self.ensure_one()
        return self.env['payment.link.wizard'].create({
            'res_model': 'account.move',
            'res_id': self.id,
            'amount': self.amount_residual,
            'amount_max': self.amount_residual,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'description': self.name,
        }).link
