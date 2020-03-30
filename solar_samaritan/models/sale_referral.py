from odoo import api, fields, models


class SaleReferral(models.Model):
    _name = 'sale.referral'
    _description = "Referral"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", compute='_compute_name', store=True)
    partner_id = fields.Many2one(comodel_name='res.partner', required=True, string="Referrer")
    lead_id = fields.Many2one(comodel_name='crm.lead', required=True, string="Lead/Opportunity")
    sale_id = fields.Many2one(comodel_name='sale.order', string="Sale Order")
    fulfill_date = fields.Datetime(sting="Fulfill Date")

    state = fields.Selection(string="State", required=True, default='new', group_expand='_expand_states', selection=[
        ('draft', "New"),
        ('qualified', "Qualified"),
        ('entitled', "Entitled"),
        ('done', "Fulfilled"),
        ('cancel', "Cancelled"),
    ])

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('partner_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.partner_id.name:
                rec.name = "Referral from " + rec.partner_id.name
            else:
                rec.name = "New Referral"

    def set_sale_created(self, sale):
        for rec in self:
            if rec.state in ['draft', 'cancel']:
                rec.state = 'qualified'
                rec.sale_id = sale

    def mark_done(self):
        for rec in self:
            rec.fulfill_date = fields.Datetime.now()
            rec.state = 'done'

    def mark_paid(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'entitled'
