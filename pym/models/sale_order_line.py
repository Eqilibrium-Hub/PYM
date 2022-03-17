# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api, _, fields
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_room = fields.Boolean('Room', compute='_compute_is_room', store=True)

    @api.depends('product_id')
    def _compute_is_room(self):
        for line in self:
            room = self.env['hotel.room'].search([('product_id', '=', line.product_id.id)], limit=1)
            line.is_room = True if room.id else False
