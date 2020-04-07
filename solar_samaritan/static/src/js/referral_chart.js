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
        "click .o_referral_redirect": "_onReferralRedirect"
    },

    _render: function () {
        var data = JSON.parse(this.value);
        return this.$el.html(QWeb.render("referral_chart", data));
    },

    _onReferralRedirect: function (event) {
        var self = this;
        event.preventDefault();
        var partner_id = parseInt($(event.currentTarget).data('partner-id'));
        return this._rpc({
            model: 'res.partner',
            method: 'get_referral_view',
            args: [partner_id],
        }).then(function(action) {
            return self.do_action(action);
        });
    },
});

field_registry.add('referral_chart', FieldOrgChart);

return FieldOrgChart;

});
