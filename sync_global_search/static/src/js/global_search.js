odoo.define('sync_global_search.globalsearch_events', function (require) {
    "use strict";

    $(document).ready(function (require) {
        $("body").on('click', function (e) {

            // Remove Global Search Results on offset
           if (e.offsetX < $('.o_global_search_systray_dropdown')[0].offsetWidth) {
                // pass
            } else {
                $('.o_global_search_systray_dropdown').removeClass('oe_open');
            }

            // Remove Global Search Results on click of body elements except it's own
            if (e.target.classList.contains('o_global_search_systray_item')) {
                return;
            } else if ($(e.target).parents('.o_global_search_systray_item').length) {
                return;
            } else if (e.target.classList.contains('o_global_search_systray_dropdown')) {
                return;
            } else if ($(e.target).parents('.o_global_search_systray_dropdown').length) {
                return;
            }  else {
                $('.o_global_search_systray_dropdown').removeClass('oe_open');
            };

        });
    });

});

odoo.define('sync_global_search.global_search', function (require) {
"use strict";

var Widget = require('web.Widget');
var GlobalSearchAutoComplete = require('sync_global_search.GlobalSearchAutoComplete');

var GlobalSearchWidget = Widget.extend({
    template:'GlobalSearch',
    events: {
        'mousedown .global-search-a': function(e) {
            e.preventDefault();
            this.$('.o_global_search_systray_dropdown').toggleClass('oe_open');
            // Remove Allure menu dropdown
            $('body').removeClass('ad_open_childmenu').removeClass('nav-sm');
        },
        'click .cu_back': function (e) {
            this.$('.o_global_search_systray_dropdown').removeClass('oe_open');
        },
        'input input.global-search': function(e) {
            clearTimeout(this.timer);
            var self = this;
            this.timer = setTimeout(this.get_data_auto.bind(this), 200);
            if (!this.$('input.global-search').val()) {
                this.$('.cu_close').css('display', 'none');
                this.$('.cu_search').css('display', 'block');
            } else {
                if (this.$('.cu_close').css('display') == 'none') {
                    this.$('.cu_close').css('display', 'block');
                    this.$('.cu_search').css('display', 'none');
                }
            }
        },
        'click input.global-search': function(e) {
            this.autocomplete.remove_focus_element();
        },
        'click .fa-times': function(e){
            this.$('.cu_close').css('display', 'none');
            this.$('.cu_search').css('display', 'block');
            this.$el.find('.global-search').val('');
        },
    },
    init: function (parent) {
        this._super(parent);
        this.models = null;
        this.autocomplete = null;
        this.timer = 0;
    },
    get_data_auto: function() {
        var self = this;
        if (!self.$('input.global-search').val()) {
            self.autocomplete.close();
            return;
        }
        self.autocomplete.search_string = self.$('input.global-search').val();
        return self._rpc({
            route: '/globalsearch/model_fields',
            params: {}
        }).then(function (r) {
            return self.autocomplete.search(self.$('input.global-search').val(), r);
        });
    },
    start: function() {
        var self = this;
        self._super.apply(this, arguments);
        self.values = [];
        self.autocomplete = new GlobalSearchAutoComplete(this, {
            get_search_element: function () {
                return self.$('input.global-search');
            },
            get_search_string: function () {
                return self.$('input.global-search').val();
            },
        });
        self.timer = 0;
        self.autocomplete.appendTo(self.$('.global-search-results'));
    },
});

return GlobalSearchWidget;

});

odoo.define('sync_global_search.GlobalSearchSystrayMenu', function (require) {
    "use strict";

    var GlobalSearchWidget = require('sync_global_search.global_search');
    var SystrayMenu = require('web.SystrayMenu');
    SystrayMenu.Items.push(GlobalSearchWidget);

});
