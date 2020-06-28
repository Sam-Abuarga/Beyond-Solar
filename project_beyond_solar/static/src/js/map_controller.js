odoo.define('project_beyond_solar.MapController', function (require) {
    "use strict";
    var MapController = require('web_map.MapController');

    MapController.include({
        _onOpenClicked: function (ev) {
            if (this.modelName !== 'project.task') {
                return this._super.apply(this, arguments);
            }

            var self = this;
            this._rpc({
                model: 'project.task',
                method: 'get_formview_id',
                args: [[ev.data.id]],
                context: ev.context || self.context,
            }).then(function (viewId) {
                self.do_action({
                    type:'ir.actions.act_window',
                    res_id: ev.data.id,
                    res_model: 'project.task',
                    views: [[viewId || false, 'form']],
                    target: 'new',
                    context: ev.context || self.context,
                });
            });
        }
    })
});
