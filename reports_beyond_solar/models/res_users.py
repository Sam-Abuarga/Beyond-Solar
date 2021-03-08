from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    compliance_declaration_attachment = fields.Binary(string="Compliance Declaration PDF Attachment", attachment=True)
