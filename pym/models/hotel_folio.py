# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    def action_confirm(self):
        room_no_partners = self.room_line_ids.filtered(lambda rl: not rl.partner_id.id)
        if room_no_partners.ids:
            names = room_no_partners.mapped('product_id.name')
            raise UserError(_('No Guest Found in Room %s', ', '.join(names)))
        super(HotelFolio, self).action_confirm()

    def create_hotel_folio_wizard(self):
        list_wizard = []
        dict_services = {}
        WIZARD_ENV = self.env['hotel.folio.invoice.wizard']
        WIZARD_LINES_ENV = self.env['hotel.folio.invoice.line.wizard']
        for service in self.service_line_ids.filtered(lambda s: s.invoice_status not in ['invoiced', 'no']):
            if not service.room_id in dict_services:
                dict_services[service.room_id] = []
            dict_services.get(service.room_id, []).append(service)
        wiz = WIZARD_ENV.create({'name': self.name, 'folio_id': self.id, 'currency_id': self.currency_id.id,
                                 'partner_id': self.partner_id.id})
        for room, services in dict_services.items():
            amount_total = 0.00
            for service in services:
                amount_total += service.price_subtotal
            vals_wizards = {
                'name': room.name,
                'currency_id': self.currency_id.id,
                'amount_total': amount_total,
                'wiz': wiz.id,
                'room_id': room.id
            }
            rooms = self.room_line_ids.filtered(lambda r: r.product_id.id == room.id)
            if rooms.ids:
                if rooms[0].partner_id.id:
                    vals_wizards['partner_id'] = rooms[0].partner_id.id
            list_wizard.append(vals_wizards)
        WIZARD_LINES_ENV.create(list_wizard)
        return wiz

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or
                                                   self.env['account.move'].default_get(
                                                       ['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.name,
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    def open_wizard_folio_wizard(self):
        wizard_id = self.create_hotel_folio_wizard()
        view_id = self.env.ref('pym.hotel_folio_invoice_wizard').id
        return {
            'context': self._context,
            'res_model': 'hotel.folio.invoice.wizard',
            'target': 'new',
            'name': _('Create Invoice by Room'),
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'views': [[view_id, 'form']],
        }
