from odoo import api, fields, models


class ConnectionDiagramCriteria(models.Model):
    _name = 'connection.diagram.criteria'
    _description = "Connection Diagram Criteria"

    diagram_id = fields.Many2one(comodel_name='connection.diagram', required=True, string="Diagram")

    site_phase = fields.Selection(string="Site Phase", required=True, selection=[
        ('single', "Single"),
        ('three', "Three"),
    ])
    inverter_count = fields.Selection(string="Inverter Count", required=True, selection=[
        ('single', "Single"),
        ('multiple', "Multiple"),
    ])
    battery = fields.Selection(string="Battery/Meter", required=True, selection=[
        ('battery', "Has Battery"),
        ('meter', "Smart Meter Only"),
        ('none', "None"),
    ])
    connection = fields.Selection(string="Inverter Connection Point", required=True, selection=[
        ('main', "Main Switch"),
        ('distribution', "Distribution Board"),
    ])
    isolator = fields.Boolean(string="AC Isolator")
