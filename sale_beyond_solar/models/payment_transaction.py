from odoo import api, fields, models, _


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def create(self, vals):
        if 'sale_order_ids' in vals and 'amount' in vals:
            vals['amount'] = round(vals['amount'] * 0.1, 2)
        return super(PaymentTransaction, self).create(vals)

    def render_sale_button(self, order, submit_txt=None, render_values=None):
        values = {
            'partner_id': order.partner_shipping_id.id or order.partner_invoice_id.id,
            'billing_partner_id': order.partner_invoice_id.id,
        }
        if render_values:
            values.update(render_values)
        # Not very elegant to do that here but no choice regarding the design.
        self._log_payment_transaction_sent()
        return self.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=submit_txt or _('Pay Now')).sudo().render(
            self.reference,
            round(order.amount_total * 0.1, 2),
            order.pricelist_id.currency_id.id,
            values=values,
        )
