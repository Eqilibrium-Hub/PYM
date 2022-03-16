# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'
