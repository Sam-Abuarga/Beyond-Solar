from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    contractor_license = fields.Char(string="Contractor's License No.")
    contractor_license_expiry = fields.Date(string="Contractor's License Expiry Date")
    contractor_signature = fields.Binary(string="PDF Signature")
