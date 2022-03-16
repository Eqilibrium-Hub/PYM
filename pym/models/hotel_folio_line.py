# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api, _, fields
import logging

_logger = logging.getLogger(__name__)


class HotelReservation(models.Model):
    _inherit = 'hotel.folio.line'

    @api.model
    def get_rooms_client(self, partner_id):
        _today = fields.Datetime.context_timestamp(self, datetime.now())
        query = """
        select id
            from hotel_folio_line
            where partner_id = {partner}
            and '{today}' between ((checkin_date AT TIME ZONE 'UTC') AT TIME ZONE '{timezone}') and 
            ((checkout_date AT TIME ZONE 'UTC') AT TIME ZONE '{timezone}');
        """.format(partner=partner_id, today=str(_today), timezone=str(self.env.user.tz))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchall()
        list_ids = [item['id'] for item in data]
        if not data:
            return {"success": False, "message": _("This Client has not a room reserved")}
        room_ids = self.browse(list_ids)
        data_json = room_ids.read(['id', 'name', 'product_id', 'folio_id'])
        return {"success": True, "data": data_json}
