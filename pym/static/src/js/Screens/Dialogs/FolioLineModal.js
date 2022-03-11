odoo.define('pym.FolioLineModal.js', function (require) {
    'use strict';

    const Popup = require('point_of_sale.ConfirmPopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');

    class RoomsDialogShow extends AbstractAwaitablePopup {

        constructor() {
            super(...arguments);
            this.room = false;
        }

        create_service_room() {
            var self = this;

            if (!self.room) {
                return self.showPopup('ErrorPopup', {
                    title: self.env._t('Unselected Room'),
                    body: self.env._t('You have not selected a room.'),
                });
            }
            var order = this.env.pos.get_order();
            let orderlines = order.get_orderlines();
            let pos_product_list = [];
            orderlines.forEach(function (ol) {
                let product_items = {
                    'product_id': ol.product.id,
                    'room_id': self.room['product_id'][0],
                    'product_uom_qty': ol.quantity,
                    'folio_id': self.room['folio_id'][0],
                    'price_unit': ol.price
                };
                pos_product_list.push(product_items);
            });
            self.rpc({
                model: 'hotel.service.line',
                method: 'create_service_line_ui',
                args: [pos_product_list],
            }).then(function (output) {
                if (output.success) {
                    if (orderlines.length > 0) {
                        for (var line in orderlines) {
                            order.remove_orderline(order.get_orderlines());
                        }
                    }
                    order.set_client(false)
                    self.showPopup('ConfirmPopup', {
                        title: self.env._t('Room Order'),
                        body: self.env._t(
                            'Order Assigned Successfully'
                        ),
                    });
                }

            });
        }

        asign_room_service(room) {
            var self = this;
            self.active_line(room['id']);
            self.room = room;
        }

        active_line(id) {
            $(".room_line_active").removeClass('room_line_active');
            $("#line_" + id).addClass('room_line_active');
        }
    };

    RoomsDialogShow.template = 'RoomsDialogShow';

    Registries.Component.add(RoomsDialogShow);

    return RoomsDialogShow;

});