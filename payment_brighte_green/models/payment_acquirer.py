from odoo import api, fields, models
from odoo.http import request


class TransferPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('brighte_green', 'Brighte Green')])

    def brighte_green_get_form_action_url(self):
        return '/payment/brighte_green/feedback'

    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super(TransferPaymentAcquirer, self).search(args, offset, limit, order, count)
        if request.endpoint_arguments and 'order_id' in request.endpoint_arguments:
            so = self.env['sale.order'].browse(request.endpoint_arguments.get('order_id'))
            if not so.brighte_price:
                res -= self.env.ref('payment_brighte_green.payment_acquirer_brighte_green')
        return res
