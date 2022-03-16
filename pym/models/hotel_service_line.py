# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api, _, fields
import logging

_logger = logging.getLogger(__name__)


class HotelServiceLine(models.Model):
    _inherit = 'hotel.service.line'

    room_id = fields.Many2one('product.product', 'Room')

    has_invoice = fields.Boolean('Has Invoice', default=False)

    @api.model
    def create_service_line_ui(self, list_products):
        service_lines = self.create(list_products)
        return {"success": True, "data": service_lines.ids}
