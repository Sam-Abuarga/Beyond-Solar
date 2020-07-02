# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from . import models
from . import wizard
from . import controllers

from odoo import api, SUPERUSER_ID, _
from odoo.exceptions import AccessError


def pre_init_check(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    verification_code = env['ir.config_parameter'].get_param('sync_verification.verification_code')
    if verification_code and verification_code == '942686':
        return True
    raise AccessError(_(
        "Verification Confirmation\n\n For installing Global Search, please forward your request for verification confirmation code to 'contact@synconics.com' and attach purchase invoice."))
