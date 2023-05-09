from datetime import datetime, timedelta
from robonomicsinterface import Account, PubSub
import time
import json

from odoo import _, api, fields, models

class FSMOrder(models.Model):
    _name = "fsm.sensors.house"
    _description = "Field Service Sensors-House table"

    sensor_id = fields.Char("Sensor id", required=True)
    location = fields.Many2one("fsm.location", string="Location", index=True, required=True)
    