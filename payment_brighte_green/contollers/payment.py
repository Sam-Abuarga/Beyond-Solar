from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

import pprint
import werkzeug

import logging
_logger = logging.getLogger(__name__)


class PaymentController(http.Controller):
    _accept_url = '/payment/brighte_green/feedback'

    @http.route('/payment/brighte_green/feedback', type='http', auth='none', csrf=False)
    def transfer_form_feedback(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'brighte_green')
        return werkzeug.utils.redirect('/payment/process')
