from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    @api.constrains('invoice_payment_state')
    def _check_paid_referral(self):
        for rec in self:
            if rec.invoice_payment_state == 'paid':
                rec.mapped('invoice_line_ids.sale_line_ids').filtered(lambda l: not l.is_downpayment).mapped('order_id.referral_id').sudo().mark_paid()
