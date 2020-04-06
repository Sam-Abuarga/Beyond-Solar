from odoo import api, fields, models
from odoo.tools import pycompat

import base64
import io
import json


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

    # Related fields to show contact details
    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    zip = fields.Char(related='partner_id.zip')
    state_id = fields.Many2one(comodel_name='res.country.state', related='partner_id.state_id')
    country_id = fields.Many2one(comodel_name='res.country', related='partner_id.country_id')
    phone = fields.Char(related='partner_id.phone')
    mobile = fields.Char(related='partner_id.mobile')
    email = fields.Char(related='partner_id.email')

    referral_ids = fields.Many2many(comodel_name='sale.referral', compute='_compute_referral_ids')
    referral_chart = fields.Text(compute='_compute_referral_chart')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('partner_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.partner_id.name:
                rec.name = "Referral from " + rec.partner_id.name
            else:
                rec.name = "New Referral"

    @api.depends('partner_id')
    def _compute_referral_ids(self):
        for rec in self:
            rec.referral_ids = rec.partner_id.referral_ids

    @staticmethod
    def _prepare_partner_data(partner):
        return dict(
            id=partner.id,
            name=partner.name,
            link='/mail/view?model=%s&res_id=%s' % ('res.partner', partner.id,),
            direct=len(partner.referral_ids),
            indirect=len(partner.indirect_referral_ids),
        )

    def _compute_referral_chart(self):
        for rec in self:
            main_partner = rec.sale_id.partner_id or rec.lead_id.partner_id
            referrals = [rec._prepare_partner_data(referral.sale_id.partner_id or referral.lead_id.partner_id) for referral in main_partner.referral_ids]

            referred_by = []
            partner = main_partner
            while partner.referred_by_id:
                referred_by.append(self._prepare_partner_data(partner.referred_by_id.partner_id))
                partner = partner.referred_by_id.partner_id
            referred_by.reverse()

            rec.referral_chart = json.dumps({
                'main_partner': rec._prepare_partner_data(main_partner),
                'referred_by': referred_by,
                'referrals': referrals,
            })

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

    def action_csv(self):
        output = io.BytesIO()
        writer = pycompat.csv_writer(output, quoting=1)

        writer.writerow(['Company', 'FirstName', 'LastName', 'Email', 'Phone', 'Quantity', 'CardValue', 'ToName', 'CarrierMessage', 'FromName'])
        for rec in self:
            writer.writerow([
                rec.partner_id.parent_id.name or '',
                rec.partner_id.name.split(' ')[0],
                rec.partner_id.name.split(' ', 1)[1] if len(rec.partner_id.name.split(' ')) > 1 else '',
                rec.partner_id.email or '',
                rec.partner_id.phone or '',
                '1',
                '100',
                rec.partner_id.name,
                'Thank you for your referral and thank you for being part of the SolarSamritan movement.\n\nBest Wishes from the Team at Beyond Solar.',
                'BeyondSolar'
            ])

        attachment = self.env['ir.attachment'].create({
            'name': "DigitalCorporateOrderUpload.csv",
            'datas': base64.b64encode(output.getvalue()),
            'type': 'binary',
            'mimetype': 'text/csv',
        })

        return {
            'name': "Referral Upload",
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}/DigitalCorporateOrderUpload.csv',
            'target': 'new'
        }
