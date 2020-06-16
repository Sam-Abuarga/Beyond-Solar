from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    has_battery = fields.Boolean(string="Has Battery", related='sale_order_id.has_battery')
    has_inverter = fields.Boolean(string="Has Inverter", compute='sale_order_id.has_battery')
    has_panel = fields.Boolean(string="Has Panel", compute='sale_order_id.has_battery')
