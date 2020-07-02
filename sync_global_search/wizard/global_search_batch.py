# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.exceptions import UserError, AccessError


class GlobalSearchBatchUsers(models.TransientModel):
    _name = 'global.search.batch.users'
    _description = 'Generate Global Search for all selected users'

    user_ids = fields.Many2many('res.users', 'global_search_user_rel', 'global_search_id', 'user_id', string="Users")

    def generate_global_searches(self):
        batch_id = False
        globalSearchConfig = self.env['global.search.config']
        if self.env.context.get('active_id', False):
            batch_id = self.env['global.search.config.batch'].browse(self.env.context.get('active_id'))
        if not self.user_ids:
            raise UserError(_("You must select user(s) to generate global search(s)."))
        access_model = self.env['ir.model.access']
        for user in self.user_ids:
            config_ids = globalSearchConfig.search([
                    ('user_id', '=', user.id),
                    ('model_id', '=', batch_id.model_id.id)
                ])
            if config_ids:
                raise UserError(_('\'%s\' is already exist in Global Searches.') % (user.name))
            if not access_model.with_user(
                        user=self.env.user.id
                    ).check(batch_id.model_id.model, 'read', raise_exception=False):
                raise AccessError(_("'%s' doesn't have access to %s model") % (user.name, batch_id.model_id.name))
            globalSearchConfig.create({
                'template_id': batch_id.template_id.id or False,
                'batch_id': batch_id.id,
                'user_id': user.id,
                'customized': batch_id.customized or False,
                'model_id': batch_id.model_id.id or False,
                'field_ids': [(6, 0, batch_id.field_ids.ids)],
            })
        return {'type': 'ir.actions.act_window_close'}
