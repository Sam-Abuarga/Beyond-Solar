odoo.define('project_beyond_solar.MapRenderer', function (require) {
    "use strict";
    var MapRenderer = require('web_map.MapRenderer');
    var FieldUtils = require('web.field_utils');
    var core = require('web.core');
    var qweb = core.qweb;

    MapRenderer.include({
        events: _.extend({}, MapRenderer.prototype.events, {
            'click .copy_dates': '_onCopyDatesClick',
        }),

        _onCopyDatesClick: function (ev) {
            this._rpc({
                model: 'project.task',
                method: 'action_copy_proposed',
                args: [parseInt(ev.currentTarget.dataset.id)],
            });
            $(".leaflet-popup-close-button")[0].click();
        },

        _addMakers: function (records) {
            var self = this;
            this._removeMakers();
            records.forEach(function (record) {
                if (record.partner && record.partner.partner_latitude && record.partner.partner_longitude) {
                    var popup = {};
                    popup.records = self._getMarkerPopupFields(record, self.fieldsMarkerPopup);
                    popup.url = 'https://www.google.com/maps/dir/?api=1&destination=' + record.partner.partner_latitude + ',' + record.partner.partner_longitude;
                    var $popup = $(qweb.render('map-popup', { records: popup, rec_id: record.id }));
                    var openButton = $popup.find('button.btn.btn-primary.edit')[0];
                    if (self.hasFormView) {
                        openButton.onclick = function () {
                            self.trigger_up('open_clicked',
                                { id: record.id });
                        };
                    } else {
                        openButton.remove();
                    }

                    var marker;
                    var offset;
                    if (self.numbering) {
                        var number = L.divIcon({
                            className: 'o_numbered_marker',
                            html: '<p class ="o_number_icon">' + (self.state.records.indexOf(record) + 1) + '</p>'
                        });
                        marker = L.marker([record.partner.partner_latitude, record.partner.partner_longitude], { icon: number });
                        offset = new L.Point(0, -35);

                    } else {
                        marker = L.marker([record.partner.partner_latitude, record.partner.partner_longitude]);
                        offset = new L.Point(0, 0);
                    }
                    marker
                        .addTo(self.leafletMap)
                        .bindPopup(function () {
                            var divPopup = document.createElement('div');
                            $popup.each(function (i, element) {
                                divPopup.appendChild(element);
                            });
                            return divPopup;
                        }, { offset: offset });
                    self.markers.push(marker);
                }
            });
        },

        _getMarkerPopupFields: function (record, fields) {
            var fieldsView = [];
            fields.forEach(function (field) {
                if (record[field['fieldName']] || field.widget) {
                    var value = record[field['fieldName']];
                    if (value instanceof Array) {
                        value = value[1];
                    }
                    if (field.widget) {
                        if (field.widget === 'boolean') {
                            value = value ? 'Yes' : 'No';
                        }
                        else if (field.widget.startsWith('default|')) {
                            if (!value) {
                                value = field.widget.substring(8);
                            }
                        }
                        else if (field.widget.startsWith('invisible|')) {
                            if (record[field.widget.split('|')[1]]) {
                                value = false;
                            }
                            else {
                                value = FieldUtils.format[field.widget.split('|')[2]](FieldUtils.parse[field.widget.split('|')[2]](value, {}), {}, {'forceString': true});
                            }
                        }
                        else if (value) {
                            value = FieldUtils.format[field.widget](FieldUtils.parse[field.widget](value, {}), {}, {'forceString': true});
                        }
                    }
                    if (value) {
                        fieldsView.push({ field: value, string: field['string'] });
                    }
                }
            });
            return fieldsView;
        },
    })
});
