from odoo import api, fields, models
from odoo.http import request

import werkzeug


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls):
        url = request.httprequest.url
        return werkzeug.utils.redirect(url.replace('https://beyondsolar.odoo.com', 'https://odoo.beyondsolar.com.au'), code=302, Response=None)
