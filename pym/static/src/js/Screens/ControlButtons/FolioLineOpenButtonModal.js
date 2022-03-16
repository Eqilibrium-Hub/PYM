odoo.define('pym.FolioLineOpenButtonModal', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class CreateFolioLine extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }

        async onClick() {
            let self = this;
            let order = self.env.pos.get_order();
            let partner_id = false
            if (order.get_client() != null)
                partner_id = order.get_client().id;

            if (!partner_id) {
                return self.showPopup('ErrorPopup', {
                    title: self.env._t('Unknown customer'),
                    body: self.env._t('You cannot Create Folio Line. Select customer first.'),
                });
            }
            self.rpc({
                model: 'hotel.folio.line',
                method: 'get_rooms_client',
                args: [partner_id],
            }).then(function (output) {
                if (output.success) {
                    self.showPopup('RoomsDialogShow', output);
                } else {
                    self.showPopup('ConfirmPopup', {
                        title: self.env._t('Rooms'),
                        body: output.message
                    });
                }
            });


        }
    }

    CreateFolioLine.template = 'CreateFolioLine';

    ProductScreen.addControlButton({
        component: CreateFolioLine,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(CreateFolioLine);

    return CreateFolioLine;
});
