from odoo import api, fields, models, http
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):
    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        return super(CustomerPortal, self).portal_order_page(order_id, report_type, access_token, message, download, **kw)
