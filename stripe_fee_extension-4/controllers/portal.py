# -*- coding: utf-8 -*-

import hashlib
import hmac

from datetime import date
from odoo import api, fields, models, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, get_records_pager
from odoo.addons.payment.controllers.portal import WebsitePayment
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.osv import expression
from odoo.tools.float_utils import float_repr


class CustomerPortal(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public",
                website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None,
                          message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id,
                                                     access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type,
                                     report_ref='sale.action_report_saleorder',
                                     download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get(
                'view_quote_%s' % order_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _(
                    'Quotation viewed by customer %s') % order_sudo.partner_id.name
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values = {
            'sale_order': order_sudo,
            'message': message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
        }
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id

        if order_sudo.has_to_be_paid():
            domain = expression.AND([
                ['&', ('state', 'in', ['enabled', 'test']),
                 ('company_id', '=', order_sudo.company_id.id)],
                ['|', ('country_ids', '=', False),
                 ('country_ids', 'in', [order_sudo.partner_id.country_id.id])]
            ])
            acquirers = request.env['payment.acquirer'].sudo().search(domain)

            values['acquirers'] = acquirers.filtered(lambda acq: (acq.payment_flow == 'form' and acq.view_template_id) or
                                                                 (acq.payment_flow == 's2s' and acq.registration_view_template_id))
            values['pms'] = request.env['payment.token'].search(
                [('partner_id', '=', order_sudo.partner_id.id)])
            values['acq_extra_fees'] = acquirers.with_context(from_so=True).get_acquirer_extra_fees(
                order_sudo.amount_total, order_sudo.currency_id,
                order_sudo.partner_id.country_id.id)
        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_quotations_history', [])
        else:
            history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order_sudo))

        return request.render('sale.sale_order_portal_template', values)


class WebsitePayment(WebsitePayment):

    @http.route(['/website_payment/pay'], type='http', auth='public',
                website=True, sitemap=False)
    def pay(self, reference='', order_id=None, amount=False, currency_id=None,
            acquirer_id=None, partner_id=False, access_token=None, **kw):
        env = request.env
        acquirers = None
        user = env.user.sudo()
        if kw.get('company_id'):
            try:
                cid = int(kw.get('company_id'))
            except:
                cid = user.company_id.id
        else:
            cid = user.company_id.id
        acquirer_domain = ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', cid)]
        res = super(WebsitePayment, self).pay(
            reference=reference, order_id=order_id, amount=amount,
            currency_id=currency_id, acquirer_id=acquirer_id,
            partner_id=partner_id, access_token=access_token, **kw)

        if partner_id and currency_id and not order_id:
            if acquirer_id:
                acquirers = env['payment.acquirer'].browse(int(acquirer_id))
            if not acquirers:
                acquirers = env['payment.acquirer'].search(acquirer_domain)
            partner = request.env['res.partner'].sudo().browse(int(partner_id))
            currency = request.env['res.currency'].sudo().browse(int(currency_id))
            acq_extra_fees = acquirers.get_acquirer_extra_fees(
                    float(amount), currency, partner.country_id.id)
            res.qcontext.update({
                'acq_extra_fees': acq_extra_fees
            })
        return res

    @http.route(['/website_payment/transaction/<string:reference>/<string:amount>/<string:currency_id>',
                 '/website_payment/transaction/v2/<string:amount>/<string:currency_id>/<path:reference>',
                 '/website_payment/transaction/v2/<string:amount>/<string:currency_id>/<path:reference>/<int:partner_id>'],
                type='json', auth='public')
    def transaction(self, acquirer_id, reference, amount, currency_id,
                    partner_id=False, **kwargs):
        acquirer = request.env['payment.acquirer'].browse(acquirer_id)
        order_id = kwargs.get('order_id')

        reference_values = order_id and {
            'sale_order_ids': [(4, order_id)]} or {}
        reference = request.env['payment.transaction']._compute_reference(
            values=reference_values, prefix=reference)

        values = {
            'acquirer_id': int(acquirer_id),
            'reference': reference,
            'amount': float(amount),
            'currency_id': int(currency_id),
            'partner_id': partner_id,
            'type': 'form_save' if acquirer.save_token != 'none' and partner_id else 'form',
        }

        if order_id:
            values['sale_order_ids'] = [(6, 0, [order_id])]

        reference_values = order_id and {
            'sale_order_ids': [(4, order_id)]} or {}
        reference_values.update(acquirer_id=int(acquirer_id))
        values['reference'] = request.env[
            'payment.transaction']._compute_reference(values=reference_values,
                                                      prefix=reference)
        tx = request.env['payment.transaction'].sudo().with_context(
            lang=None).create(values)
        secret = request.env['ir.config_parameter'].sudo().get_param(
            'database.secret')
        token_str = '%s%s%s' % (tx.id, tx.reference, float_repr(
            tx.amount, precision_digits=tx.currency_id.decimal_places))
        token = hmac.new(secret.encode('utf-8'), token_str.encode('utf-8'),
                         hashlib.sha256).hexdigest()
        tx.return_url = '/website_payment/confirm?tx_id=%d&access_token=%s' % (
            tx.id, token)

        PaymentProcessing.add_payment_transaction(tx)

        render_values = {
            'partner_id': partner_id,
        }
        if not order_id:
            acquirer = acquirer.with_context(stripe_fees=True)
        return acquirer.sudo().render(tx.reference, float(amount),
                                      int(currency_id), values=render_values)
