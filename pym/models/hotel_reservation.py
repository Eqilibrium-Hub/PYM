# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

    @api.model
    def get_rooms_client(self, partner_id):
        _today = datetime.now()
        query = """
        select id
            from hotel_reservation
            where partner_id = {partner}
            and '{today}' between ((checkin AT TIME ZONE 'UTC') AT TIME ZONE '{timezone}') and 
            ((checkout AT TIME ZONE 'UTC') AT TIME ZONE '{timezone}');
        """.format(partner=partner_id, today=str(_today), timezone=str(self.env.user.tz))
        self.env.cr.execute(query)
        data = self.env.cr.dictfetchone()
        if not data:
            return {"success": False, "message": _("This Client has not a room reserved")}
        room_ids = self.browse(data.get('id'))
        data_json = room_ids.mapped('folio_id').mapped('room_line_ids').read(['id', 'name', 'product_id', 'folio_id'])
        return {"success": True, "data": data_json, "reservation_id": data.get('id')}
