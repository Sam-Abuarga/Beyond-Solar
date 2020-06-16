odoo.define('project_beyond_solar.CalendarPopover', function (require) {
    "use strict";

    var CalendarPopover = require('web.CalendarPopover');
    var CalendarRenderer = require('web.CalendarRenderer');

    CalendarRenderer.include({
        custom_events: _.extend({}, CalendarRenderer.prototype.custom_events, {
            close_event: '_onCloseEvent',
        }),

        _onCloseEvent: function () {
            this._unselectEvent();
        },
    });

    CalendarPopover.include({
        events: _.extend({}, CalendarPopover.prototype.events, {
            'click .o_cw_popover_copy_date': '_onCopyDatesClick',
        }),

        _onCopyDatesClick: function () {
            this._rpc({
                model: 'project.task',
                method: 'action_copy_proposed',
                args: [this.event.id],
            });
            this.trigger_up('close_event');
        },
    })
});
