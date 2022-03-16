# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class HotelFolioInvoiceWizard(models.TransientModel):
    _name = 'hotel.folio.invoice.wizard'
    _description = 'Folio Invoice by Room Wizard'

    name = fields.Char('Name')

    folio_id = fields.Many2one('hotel.folio', 'Folio')

    partner_id = fields.Many2one('res.partner', 'Customer')

    partner_filter = fields.Many2many('res.partner', string='Partner Filter')

    room_wizard_lines = fields.One2many('hotel.folio.invoice.line.wizard', 'hotel_wizard_id', 'Wizard Lines')

    @api.onchange('room_wizard_lines')
    def onchange_room_wizard_lines(self):
        if self.room_wizard_lines.ids:
            partners = []
            for line in self.room_wizard_lines:
                partners.append(line.partner_id.id)
            self.update({'partner_filter': [(6, 0, partners)]})

    service_lines = fields.Many2many('hotel.service.line', string='Services Line', store=True,
                                     compute="_compute_service_lines")

    amount_untaxed = fields.Monetary('Untaxed amount', compute='_amount_all', store=True)

    amount_tax = fields.Monetary('Taxes', compute='_amount_all', store=True)

    amount_total = fields.Monetary('Total amount', compute='_amount_all', store=True)

    currency_id = fields.Many2one('res.currency', 'Currency')

    @api.depends('service_lines.price_total')
    def _amount_all(self):
        for wizard in self:
            amount_untaxed = amount_tax = 0.0
            for line in wizard.service_lines:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            wizard.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('room_wizard_lines', 'folio_id')
    def _compute_service_lines(self):
        for hotel in self:
            rooms = hotel.room_wizard_lines.mapped('room_id')
            hotel_services_line = hotel.folio_id.service_line_ids.filtered(lambda li: li.room_id.id in rooms.ids)
            hotel.service_lines = [(6, 0, hotel_services_line.ids)]

    def create_invoices(self):
        invoice_vals = self.folio_id.order_id._prepare_invoice()
        invoice_vals['partner_id'] = self.partner_id.id
        invoice_vals['partner_shipping_id'] = self.partner_id.id
        invoice_lines = []
        for line in self.service_lines:
            invoice_lines.append((0, 0, line.service_line_id._prepare_invoice_line()))
        invoice_vals['invoice_line_ids'] = invoice_lines
        _logger.info("invoice_vals")
        _logger.info(invoice_vals)
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)


class HotelFolioInvoiceWizardLine(models.TransientModel):
    _name = 'hotel.folio.invoice.line.wizard'
    _description = 'Folio Invoice Line by Room Wizard'

    hotel_wizard_id = fields.Many2one('hotel.folio.invoice.wizard', 'Hotel Wizard', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', 'Customer')
    room_id = fields.Many2one('product.product', 'Room')
    name = fields.Char('Room')
    currency_id = fields.Many2one('res.currency', 'Currency')
    amount_total = fields.Monetary('Amount Total')
    wiz = fields.Integer('Wiz Filter')
