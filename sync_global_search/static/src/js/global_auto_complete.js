odoo.define('sync_global_search.GlobalSearchAutoComplete', function (require) {
"use strict";

    var Widget = require('web.Widget');
    var rpc = require('web.rpc');

    var GlobalSearchAutoComplete = Widget.extend({
        template: "GlobalSearch.AutoComplete",
        // Parameters for autocomplete constructor:
        //
        // parent: this is used to detect keyboard events
        //
        // options.select: function (ev, {item: {facet:facet}}).  Autocomplete widget will call
        //      that function when a selection is made by the user
        // options.get_search_string: function ().  This function will be called by autocomplete
        //      to obtain the current search string.
        init: function (parent, options) {
            this._super(parent);
            this.$input = parent.$el;
            this.get_search_string = options.get_search_string;
            this.current_result = null;
            this.current_results = {};
            this.searching = true;
            this.search_string = '';
            this.activeModels = {};
            this.get_search_element = options.get_search_element;
            this.current_element = null;
            this.current_elements = {};
            this.offset = 0;
            this.limit = 10;
            this.search_more_options = {};
            this.last_search_more_element = null;
            this.selected_data = '';
            this.focus_data = '';
            // this.current_search = null;
        },
        start: function () {
            var self = this;
            self.$el.parents().find('.oe_application_menu_placeholder a').on('click', function() {
                self.$el.parents().find('.o_sub_menu').css('display', 'none');
            });
            this.$input.on('focusout', function () {
                self.close();
            });
            this.$input.on('keyup', function (ev) {
                if (ev.which === $.ui.keyCode.RIGHT) {
                    self.searching = true;
                    ev.preventDefault();
                    return;
                }
                var search_string = self.get_search_string();
                if (self.search_string !== search_string) {
                    if (search_string.length) {
                        self.search_string = search_string;
                    } else {
                        self.close();
                    }
                }
            });
            this.$input.on('keypress', function (ev) {
                self.search_string = self.search_string + String.fromCharCode(ev.which);
                if (self.search_string.length) {
                    self.searching = true;
                    var search_string = self.search_string;
                } else {
                    self.close();
                }
            });
            this.$input.on('keydown', function (ev) {
                switch (ev.which) {
                    case $.ui.keyCode.ENTER:
                    // TAB and direction keys are handled at KeyDown because KeyUp
                    // is not guaranteed to fire.
                    // See e.g. https://github.com/aef-/jquery.masterblaster/issues/13
                    case $.ui.keyCode.TAB:
                        self.searching = false;
                        var current = self.current_result;
                        // var $li = self.$('li.oe-selection-focus')
                        // self.current_element = $li.data('result')
                        if (current && current.expand) {
                            ev.preventDefault();
                            ev.stopPropagation();
                            if (current.expanded) {
                                self.fold();
                            } else {
                                self.expand_show();
                                self.searching = true;
                            }
                        } else{
                            if (self.search_string.length) {
                                self.select_item(ev);
                            }
                            if (self.current_element && self.current_element.hasClass('oe-search-more')) {
                                // oe-search-more oe-model-product_product
                                self.current_element.css("color", "white");
                                self.search_more(self.current_element, self.current_element.data().result.model[1]);
                            }
                        }
                        ev.preventDefault();
                        break;
                    case $.ui.keyCode.DOWN:
                        if(self.search_string){
                        self.move('down');
                        self.searching = false;
                        ev.preventDefault();}
                        break;
                    case $.ui.keyCode.UP:
                        if(self.search_string){
                        self.move('up');
                        self.searching = false;
                        ev.preventDefault();}
                        break;
                    case $.ui.keyCode.RIGHT:
                        self.searching = false;
                        var current = self.current_result;
                        if (current && current.expand && !current.expanded) {
                            self.expand();
                            self.searching = true;
                        }
                        ev.preventDefault();
                        break;
                    case $.ui.keyCode.ESCAPE:
                        self.close();
                        self.searching = false;
                        break;
                }
            });
        },

        add_loader: function() {
            this.$('ul').append($('<li class="global-search-loder"><i class="fa fa-circle-o-notch fa-spin"></i> Loading...</li>'));
        },

        remove_loader: function() {
            this.$('ul').find('li.global-search-loder').remove();
        },

        search: function (query, models) {
            var self = this;
            self.current_search = query;
            self.activeModels = models;
            self.render_search_results(models);
        },
        render_search_results: function (results) {
            var self = this;
            var $list = self.$('ul');
            $list.empty();
            self.add_loader();
            var render_separator = false;
            var has_list = false
            if (!_.isEmpty(results)) {
                self.expand(true, results);
            } else {
                self.add_no_results_message();
            }
            this.show();
        },
        make_list_item: function (result) {
            var self = this;
            var $li = $('<li>')
                .hover(function () {
                    self.$('li').removeClass('oe-selection-focus');
                    $li.addClass('oe-selection-focus');
                })
                .mousedown(function (ev) {
                    self.focus_element($li);
                    self.searching = false;
                    var current = self.current_result;

                    if (current && current.expand) {
                        ev.preventDefault();
                        ev.stopPropagation();
                        if (current.expanded){
                            self.fold();}
                        else {
                            // self.expand();
                            self.expand_show();
                        }
                    }
                    else{
                        if (self.search_string.length) {
                        self.select_item(ev);
                    }}
                    ev.preventDefault();
                })
                .data('result', result);
            if (result.expand) {
                var $expand = $('<span class="oe-expand">').text('▶').appendTo($li);
                result.expanded = false;
                $li.append($('<span>').html('Search <em>'+result.model[0] +'</em> for: <strong>'+self.search_string+'</strong>'));
            }
            if (result.indent){
                if(result.label){$li.append($('<span>').html(' '+result.label));}
                else{
                    var regex = RegExp(this.search_string, 'gi');
                    var replacement = '<strong>$&</strong>';
                    $li.append($('<strong>').html(' '+result['display_name']));
                    for(var key in result){
                        if ($.inArray(key, ['display_model', 'display_name', 'id', 'indent', 'model']) >= 0){continue;}
                        $li.append($('<em>').html(' | '+ key));
                        $li.append($('<span>').html(': '+String(result[key]).replace(regex, replacement)));
                    }
                }
            $li.addClass('oe-indent');
            }
            return $li;
        },

        make_no_results_message_li: function() {
            var self = this;
            var $li = $("<li>No Results Found!</li>").addClass('oe-no-results')
                .mousedown(function (ev) {
                    ev.preventDefault();
                });
            return $li;
        },

        add_no_results_message: function() {
            var self = this;
            self.remove_loader();
            if (!self.$('ul').find('li.oe-no-results').length) {
                var $li = self.make_no_results_message_li();
                $li.appendTo(self.$('ul'));
            }
        },

        search_more: function($li, model) {
            var self = this;
            self.current_result =  _.extend($li.data('result'),
                {'search_more': true});
            self.last_search_more_element = $li;
            self.expand();
        },

        make_search_more_option: function(model) {
            var self = this;
            var $li = $("<li>Search More...</li>").addClass('oe-indent oe-search-more oe-model-' + model.replace('.', '_'))
                .hover(function () {self.focus_element($li);})
                .mousedown(function (ev) {
                    self.searching = false;
                    var current = self.current_results[model];
                    if (self.search_string.length) {
                        self.search_more($li, model);
                    }
                    ev.preventDefault();
                })
                .data('result', {'model': _.pairs(_.invert(_.pick(_.invert(self.activeModels), model)))[0]});
            return $li;
        },

        add_search_more_option: function(initExpand, result) {
            var self = this;
            if (result.options && result.options.remaining) {
                var $searchMoreLi = self.make_search_more_option(result.model[1]);

                self.search_more_options[result.model[1]] = result.options;
                if (initExpand) {
                    self.current_elements[result.model[1]].after($searchMoreLi);
                } else {
                    self.current_element.after($searchMoreLi);
                }
            }
        },

        make_object_category: function(initExpand, result) {
            var self = this;
            result.expand = true;
            result['model'] = _.pairs(_.invert(_.pick(_.invert(self.activeModels), result.model)))[0];

            if (initExpand && !_.isEmpty(result.datas)) {
                var $item = self.make_list_item(result).appendTo(self.$('ul'));
                self.current_elements[result.model[1]] = $item;
                self.current_results[result.model[1]] = $item.data('result');
            }

            self.add_search_more_option(initExpand, result);
            _.each(result.datas, function(data) {
                data.display_model = initExpand ? self.current_results[result.model[1]]['model'][0] : self.current_result['model'][0];
                data.model = result.model[1];
                data.indent = true;
                var $li = self.make_list_item(data);
                if (initExpand) {
                    self.current_elements[result.model[1]].after($li);
                } else {
                    self.current_element.after($li);
                }
            });

            if (result.options.remaining === 0) {
                self.$('ul li.oe-model-' + result.model[1].replace('.', '_')).remove();
            }

            if (self.last_search_more_element) {
                self.last_search_more_element.remove();
            }

            if (_.has(self.current_results, result.model[1]))  {
                if (initExpand) {
                    self.current_results[result.model[1]].expanded = true;
                    self.current_elements[result.model[1]].find('span.oe-expand').html('▼');
                } else {
                    self.current_result.expanded = true;
                    self.current_element.find('span.oe-expand').html('▼');
                }
            }
        },

        expand: function (initExpand, models) {
            var self = this;
            var current_result = this.current_result;

            if (initExpand && _.isEmpty(models)) {
                self.add_no_results_message();
                return false;
            };

            return this._rpc({
                route:'/globalsearch/search_data',
                params: {
                    models: initExpand ? _.values(models) : [current_result.model[1]],
                    search_string: self.get_search_string(),
                    search_more_options: initExpand ? {'offset': self.offset, 'limit': self.limit} : self.search_more_options[current_result.model[1]],
                }
            }).then(function (results) {
                if (_.isEmpty(_.flatten(_.map(results, 'datas')))) {
                    self.add_no_results_message();
                    return false;
                }

                (results).reverse().forEach(function (result) {
                    self.remove_loader();
                    self.make_object_category(initExpand, result);
                });
            });
        },

        fold: function () {
            this.current_element.nextUntil(':not(.oe-indent)').hide();
            this.current_result.expanded = false;
            this.current_element.find('span.oe-expand').html('▶');
        },

        expand_show: function() {
            var self = this;
            self.current_element.nextUntil(':not(.oe-indent)').show();
            self.current_result.expanded = true;
            self.current_element.find('span.oe-expand').html('▼');
        },

        focus_element: function ($li) {
            this.$('li').removeClass('oe-selection-focus');
            $li.addClass('oe-selection-focus');
            this.current_result = $li.data('result');
            this.current_element = $li
            this.focus_data = $li.text();
        },

        remove_focus_element: function () {
            this.$('li').removeClass('oe-selection-focus');
            this.focus_data = '';
        },

        select_item: function (ev) {
            var self = this;
            if(self.current_result){
                if (self.current_result.label == '(no result)') { return true; };
                if (self.current_result.expand) { this.expand(); };
                if(self.current_result.indent) {
                    var $li = self.$('li.oe-selection-focus');
                    self.selected_data = $li.data('result');
                    if(!_.isEmpty(self.selected_data)) {
                        self.$input.find('.global-search').val(self.selected_data['display_model']+ ':  '+$.trim(this.focus_data.split('|')[0]));
                        self.close();
                        ev.preventDefault();
                        return self.do_action({
                            'type': 'ir.actions.act_window',
                            'res_id': this.current_result['id'],
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': this.current_result['model'],
                            'target': 'current',
                            'views':[[false, 'form']],
                        }).then(function(result){
                            self.$el.parents().find('.o_sub_menu').css('display', 'none');
                            return rpc.query({
                                model: 'ir.model.data',
                                method: 'xmlid_to_res_id',
                                args: ['sync_global_search.menu_global_search']
                            }).then(function(result){
                                self.$el.parents().find('.o_global_search_systray_dropdown').removeClass('oe_open');
                                self.$el.parents().find('.oe_application_menu_placeholder a').parents().removeClass('active')
                                self.$el.parents().find('a[data-menu="' + String(result) + '"]').parent().addClass('active')
                            });
                        });
                    }
                }
            }
        },
        show: function () {
            this.$el.show();
        },
        close: function () {
            this.current_search = null;
            this.search_string = '';
            this.searching = true;
            this.last_search_more_element = null;
            this.$el.hide();
        },
        move: function (direction) {
            var $next;
            if (direction === 'down') {
                $next = this.$('li.oe-selection-focus').nextAll(':not(.oe-separator)').first();
                if (!$next.length) $next = this.$('li:first-child');
            } else {
                $next = this.$('li.oe-selection-focus').prevAll(':not(.oe-separator)').first();
                if (!$next.length) $next = this.$('li:not(.oe-separator)').last();
            }
            this.focus_element($next);
            $(".oe-global-autocomplete").scrollTop(0);//set to top
            if ($('li.oe-selection-focus').offset()){
                $(".oe-global-autocomplete").scrollTop($('li.oe-selection-focus').offset().top-$(".oe-global-autocomplete").height());
            }
        },
        is_expandable: function () {
            return !!this.$('.oe-selection-focus .oe-expand').length;
        },
    });

    return GlobalSearchAutoComplete;

});