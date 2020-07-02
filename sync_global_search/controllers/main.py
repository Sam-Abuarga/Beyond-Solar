# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
import threading
import queue


class GlobalSearch(http.Controller):


    @http.route('/globalsearch/model_fields', type='json', auth="user")
    def search_model_fields(self, **kwargs):
        '''This function prepares values for autocomplete 'Search for <model:name>:'
        it returns Models whose template is assigned to current login user.
        '''
        GS = request.env['global.search.config'].with_user(user=request.env.user.id).search([('user_id', '=', request.env.user.id)])
        result = dict([(gs.model_id.name, gs.model_id.model) for gs in GS if len(gs.field_ids) > 0])
        return result

    @http.route('/globalsearch/search_data', type='json', auth="user")
    def search_data(self, **kwargs):
        '''This function returns data for partucular model's search expand.'''
        que = queue.Queue()
        globalSearchConfig = request.env['global.search.config']
        search_string = kwargs['search_string']
        try:
            search_datas = []
            for model in kwargs['models']:
                GS = globalSearchConfig.with_user(user=request.env.user.id).search([('user_id', '=', request.env.user.id), ('model_id.model', '=', model)], limit=1)
                if len(GS.field_ids) > 0:
                    fields = dict([(field.name, (field.field_description, field.relation)) for field in GS.field_ids])
                    dom = ['|' for l in range(len(fields)-1)]
                    dom.extend([(f, 'ilike', kwargs['search_string']) for f in fields.keys()])
                    kwargs['fields'] = fields
                    kwargs['dom'] = dom
                    kwargs['model'] = model
                    thread_process = threading.Thread(target=lambda q, arg: q.put(globalSearchConfig._process_global_search_data(arg)), args=(que, kwargs))
                    thread_process.start()
                    thread_process.join()
                    datas = que.get()
                    search_datas.append({'model': model, 'datas': datas[0], 'options': datas[1]})
            return search_datas #or [{'label': '(no result)'}]
            # return [{'label': '(no result)'}]
        except KeyError as e:
            raise UserError(
                _("Incorrect configuration, please check it.\n\n%s not found") % (e))
