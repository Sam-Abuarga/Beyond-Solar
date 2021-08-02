from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if args and len(args) == 2:
            model = False
            id = False

            for tup in args:
                if len(tup) == 3:
                    if tup[0] == 'res_model' and tup[2] == 'project.task':
                        model = tup[2]
                    if tup[0] == 'res_id':
                        id = tup[2]

            if model and id:
                if model == 'project.task':
                    task = self.env['project.task'].browse(id)
                    args = ['|', '&', ('res_model', '=', 'sale.order'), ('res_id', '=', task.sale_order_id.id), '&'] + args

        return super(IrAttachment, self).search(args, offset, limit, order, count)
