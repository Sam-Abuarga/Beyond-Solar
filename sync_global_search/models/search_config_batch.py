# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, api, fields


class GlobalSearchConfigBatch(models.Model):
    _name = 'global.search.config.batch'
    _rec_name = 'model_id'
    _description = 'Global Search Batch Configuration'

    template_id = fields.Many2one('global.search.config.template', string='Template',
        domian="[('id', in, [])]")
    searches_ids = fields.One2many('global.search.config', 'batch_id', string="User(s)",
        required=False, readonly=True)
    customized = fields.Boolean(string='Customized')
    model_id = fields.Many2one('ir.model', string='Model', required=True)
    field_ids = fields.Many2many('ir.model.fields', string='Fields',
        domain="[('model_id', '=', model_id), ('name', '!=', 'id'), ('ttype', '!=', 'boolean'), ('selectable', '=', True)]",
        required=True)

    _sql_constraints = [('uniq_model', "UNIQUE(model_id)", "The model must be unique!")]

    def write(self, vals):
        '''Override to manage customized boolean'''
        if 'customized' not in vals and ((vals.get('user_id') and len(vals.keys()) > 1) or not vals.get('user_id')):
            vals['customized'] = True
        if 'template_id' in vals and not vals.get('model_id', False):
            vals['model_id'] = self.env['global.search.config.template'].search([('id', '=', vals['template_id'])]).model_id.id
        res = super(GlobalSearchConfigBatch, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        '''Override check the values'''
        if 'template_id' in vals and not vals.get('model_id', False):
            vals['model_id'] = self.env['global.search.config.template'].search([('id', '=', vals['template_id'])]).model_id.id
        return super(GlobalSearchConfigBatch, self).create(vals)

    @api.onchange('template_id')
    def _onchange_template_id(self):
        '''To set fields as per template selection.'''
        self.field_ids = [(6, 0, self.template_id.field_ids.ids or [])]
        self.model_id = self.template_id.model_id.id or False
        self.customized = False

    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.template_id:
            self._onchange_template_id()
        else:
            self.field_ids = [(6, 0, [])]

    def apply_changes_in_searches(self):
        """ Its calling for effects on searches."""
        for rec in self.searches_ids.filtered(lambda s: not s.customized):
            rec.set_values_template_batch(rec.batch_id)
        return True
