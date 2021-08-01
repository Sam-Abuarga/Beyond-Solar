from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools import float_compare, format_datetime, format_time
from datetime import timedelta

import logging
import pprint

_logger = logging.getLogger(__name__)


class TransferPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _brighte_green_form_get_tx_from_data(self, data):
        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
        tx = self.search([('reference', '=', reference)])

        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx

    def _brighte_green_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if float_compare(float(data.get('amount') or '0.0'), self.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))

        return invalid_parameters

    def _brighte_green_form_validate(self, data):
        _logger.info('Validated Brighte Green payment for tx %s: set as done' % (self.reference))
        self._set_transaction_pending()
        for so in self.sale_order_ids:
            activity_type = self.env.ref('payment_brighte_green.activity_type_brighte_green')
            self.env['mail.activity'].create({
                'res_id': so.id,
                'res_model_id': self.env['ir.model']._get('sale.order').id,
                'activity_type_id': activity_type.id,
                'user_id': activity_type.default_user_id.id,
                'date_deadline': fields.Date.context_today(self) + timedelta(days=activity_type.delay_count),
            })
        return True
