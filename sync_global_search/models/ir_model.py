# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class IrModel(models.Model):
    _inherit = 'ir.model'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('global_search_config', False):
            args += [('id', 'in', self.search([('transient', '=', False)]).filtered(lambda model: not self.env[model.model]._abstract).ids)]
        return super(IrModel, self).name_search(name=name, args=args, operator=operator, limit=limit)


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('global_search_config', False):
            args += [
                ('store', '=', True),
                ('ttype', 'not in', ('boolean', 'binary', 'html')),
            ]
        return super(IrModelFields, self).name_search(name=name, args=args, operator=operator, limit=limit)
