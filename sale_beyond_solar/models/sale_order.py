from odoo import api, fields, models
from odoo.addons.sale_management.models.sale_order import SaleOrder as SaleOrderEmail

from itertools import groupby


def action_confirm(self):
    res = super(SaleOrderEmail, self).action_confirm()
    for order in self:
        if order.sale_order_template_id and order.sale_order_template_id.mail_template_id:
            self.sale_order_template_id.mail_template_id.send_mail(order.id, email_values={'subtype_id': 1})
    return res

SaleOrderEmail.action_confirm = action_confirm


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_battery = fields.Boolean(string="Has Battery", compute='_compute_line_categories', store=True)
    has_micro_inverter = fields.Boolean(string="Has Micro Inverter", compute='_compute_line_categories', store=True)
    has_inverter = fields.Boolean(string="Has Inverter", compute='_compute_line_categories', store=True)
    has_panel = fields.Boolean(string="Has Panel", compute='_compute_line_categories', store=True)

    panel_count = fields.Integer(string="Panel Count", compute='_compute_panel_count')

    filtered_sale_order_option_ids = fields.One2many(comodel_name='sale.order.option', inverse_name='order_id', domain=[('is_present', '=', True)],
                                                     string='Optional Products Lines', copy=True, readonly=False)

    mppt_ids = fields.One2many(comodel_name='sale.mppt', inverse_name='sale_id', string="MPPTs")
    mppt_panel_count = fields.Integer(string="MPPT Panel Count", compute='_compute_panel_count')
    panel_count_match = fields.Boolean(string="Panel Count Match", compute='_compute_panel_count')

    brighte_price = fields.Float(string="Brighte $/Week")

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res.check_mppts()
        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        self.check_mppts()
        return res

    @api.depends('order_line.product_id')
    def _compute_line_categories(self):
        battery_cat = self.env['product.category'].search([('name', '=', "Storage")], limit=1)
        micro_cat = self.env['product.category'].search([('name', '=', "Micro Inverters")], limit=1)
        inverter_cat = self.env['product.category'].search([('name', '=', "Inverters")], limit=1)
        panel_cat = self.env['product.category'].search([('name', '=', "Solar Panels")], limit=1)

        battery_cat_ids = self.env['product.category'].search([('id', 'child_of', battery_cat.id)]).ids
        micro_cat_ids = self.env['product.category'].search([('id', 'child_of', micro_cat.id)]).ids
        inverter_cat_ids = self.env['product.category'].search([('id', 'child_of', inverter_cat.id)]).ids
        panel_cat_ids = self.env['product.category'].search([('id', 'child_of', panel_cat.id)]).ids

        for rec in self:
            battery = False
            micro = False
            inverter = False
            panel = False

            for line in rec.order_line:
                id = line.product_id.categ_id.id
                if id in battery_cat_ids:
                    battery = True
                if id in micro_cat_ids:
                    micro = True
                if id in inverter_cat_ids:
                    inverter = True
                if id in panel_cat_ids:
                    panel = True

            rec.has_battery = battery
            rec.has_micro_inverter = micro
            rec.has_inverter = inverter
            rec.has_panel = panel

    @api.depends('order_line.product_id', 'order_line.product_uom_qty')
    def _compute_panel_count(self):
        panel_cat = self.env['product.category'].search([('name', '=', "Solar Panels")], limit=1)
        panel_cat_ids = self.env['product.category'].search([('id', 'child_of', panel_cat.id)]).ids

        for rec in self:
            rec.panel_count = sum(rec.order_line.filtered(lambda l: l.product_id.categ_id.id in panel_cat_ids).mapped('product_uom_qty'))
            rec.mppt_panel_count = sum(rec.mppt_ids.filtered(lambda mppt: mppt.mppt_id).mapped('panel_count'))
            rec.panel_count_match = rec.panel_count == rec.mppt_panel_count

    def check_mppts(self):
        MPPT = self.env['sale.mppt']

        for rec in self:
            to_delete = rec.mppt_ids

            for line in rec.order_line.filtered(lambda sol: sol.product_uom_qty > 0 and sol.product_id.product_tmpl_id.mppt_ids):
                for i in range(1 if line.product_id.mppt_single else int(line.product_uom_qty)):
                    matches = rec.mppt_ids.filtered(lambda m: m.sale_line_id == line and m.sale_line_index == i)

                    # Header Lines
                    if matches:
                        to_delete -= matches.filtered(lambda m: not m.mppt_id)
                        matches.filtered(lambda l: not l.mppt_id).write({'name': line.product_id.name + (f' ({i + 1})' if i > 0 else '')})
                    else:
                        MPPT.create({
                            'sale_line_id': line.id,
                            'sale_id': rec.id,
                            'sale_line_index': i,
                            'name': line.product_id.name + (f' ({i + 1})' if i > 0 else ''),
                        })

                    # Strings
                    for mppt in line.product_id.product_tmpl_id.mppt_ids.filtered(lambda m: m.enabled):
                        match = matches.filtered(lambda m: m.mppt_id == mppt)
                        if match:
                            to_delete -= match
                        else:
                            MPPT.create({
                                'sale_line_id': line.id,
                                'sale_id': rec.id,
                                'sale_line_index': i,
                                'name': mppt.name,
                                'mppt_id': mppt.id
                            })

            to_delete.unlink()

    def get_customer_mppts(self):
        result = []

        for combination, mppts_g in groupby(self.mppt_ids, key=lambda l: (l.sale_line_id, l.sale_line_index)):
            mppts = self.env['sale.mppt']
            for m in mppts_g:
                mppts += m

            inverter = {
                'name': mppts.filtered(lambda m: not m.mppt_id)[:1].name,
                'lines': []
            }

            mppts = mppts.filtered(lambda m: m.mppt_id)

            # If all mppts match, condense
            if all([m.azimuth_angle == mppts[0].azimuth_angle and m.tilt_angle == mppts[0].tilt_angle for m in mppts]):
                inverter['lines'].append([
                    "A",
                    sum([mppt.panel_count for mppt in mppts]),
                    f'{mppts[0].azimuth_angle:g}',
                    f'{mppts[0].tilt_angle:g}',
                ])
                result.append(inverter)
                continue

            # Check if any threads can be condensed
            inverters = sorted(set(mppts.mapped('mppt_id.mppt_number')))
            for i in inverters:
                mppts_i = mppts.filtered(lambda m: m.mppt_id.mppt_number == i)
                if not mppts_i:
                    continue
                azim = mppts_i[0].azimuth_angle
                tilt = mppts_i[0].tilt_angle
                if all([m.azimuth_angle == azim and m.tilt_angle == tilt for m in mppts_i]):
                    inverter['lines'].append([
                        f"{chr(i + 65)}",
                        sum([mppt.panel_count for mppt in mppts_i]),
                        f'{azim:g}',
                        f'{tilt:g}',
                    ])
                else:
                    for mppt in mppts_i.filtered(lambda m: m.panel_count):
                        inverter['lines'].append([
                            mppt.name,
                            mppt.panel_count,
                            f'{mppt.azimuth_angle:g}',
                            f'{mppt.tilt_angle:g}',
                        ])
            result.append(inverter)
        return result

    def action_done(self):
        return super(SaleOrder, self.sudo()).action_done()

    def action_unlock(self):
        return super(SaleOrder, self.sudo()).action_unlock()
