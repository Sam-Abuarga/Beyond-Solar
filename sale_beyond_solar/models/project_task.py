from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    has_battery = fields.Boolean(string="Has Battery", related='sale_order_id.has_battery')
    has_micro_inverter = fields.Boolean(string="Has Micro Inverter", related='sale_order_id.has_micro_inverter')
    has_inverter = fields.Boolean(string="Has Inverter", related='sale_order_id.has_inverter')
    has_panel = fields.Boolean(string="Has Panel", related='sale_order_id.has_panel')
