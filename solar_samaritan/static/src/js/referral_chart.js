odoo.define('solar_samaritan.OrgChart', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var concurrency = require('web.concurrency');
var core = require('web.core');
var field_registry = require('web.field_registry');
var session = require('web.session');

var QWeb = core.qweb;

var FieldOrgChart = AbstractField.extend({

    events: {
        "click .o_employee_redirect": "_onEmployeeRedirect",
        "click .o_employee_sub_redirect": "_onEmployeeSubRedirect",
        "click .o_employee_more_managers": "_onEmployeeMoreManager"
    },

    _render: function () {
        var data = JSON.parse(this.value);
        return this.$el.html(QWeb.render("referral_chart", data));
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    _onEmployeeMoreManager: function(event) {
        event.preventDefault();
        this.employee = parseInt($(event.currentTarget).data('employee-id'));
        this._render();
    },
    /**
     * Redirect to the employee form view.
     *
     * @private
     * @param {MouseEvent} event
     * @returns {Promise} action loaded
     */
    _onEmployeeRedirect: function (event) {
        var self = this;
        event.preventDefault();
        var employee_id = parseInt($(event.currentTarget).data('employee-id'));
        return this._rpc({
            model: 'hr.employee',
            method: 'get_formview_action',
            args: [employee_id],
        }).then(function(action) {
            return self.do_action(action);
        });
    },
    /**
     * Redirect to the sub employee form view.
     *
     * @private
     * @param {MouseEvent} event
     * @returns {Promise} action loaded
     */
    _onEmployeeSubRedirect: function (event) {
        event.preventDefault();
        var employee_id = parseInt($(event.currentTarget).data('employee-id'));
        var employee_name = $(event.currentTarget).data('employee-name');
        var type = $(event.currentTarget).data('type') || 'direct';
        var self = this;
        if (employee_id) {
            this._getSubordinatesData(employee_id, type).then(function(data) {
                var domain = [['id', 'in', data]];
                return self._rpc({
                    model: 'hr.employee',
                    method: 'get_formview_action',
                    args: [employee_id],
                }).then(function(action) {
                    action = _.extend(action, {
                        'view_mode': 'kanban,list,form',
                        'views':  [[false, 'kanban'], [false, 'list'], [false, 'form']],
                        'domain': domain,
                    });
                    return self.do_action(action);
                });
            });
        }
    },
});

field_registry.add('referral_chart', FieldOrgChart);

return FieldOrgChart;

});
