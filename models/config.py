# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import base64
import re

class InfluencerConfig(models.Model):
    _name = 'influencer.config'

    name = fields.Char("Name",required=True)
    gsheet_id = fields.Char("Sheet ID",default="1wN9PNO-cX3NVAhYNLqu5psr0GeUj6n0aNdTdwWBLO84",required=True)
    gsheet_key = fields.Char("Sheet Key",default="AIzaSyAq4FMO_oGh8GqOc90wXcS8KU-cMBCwf64",required=True)
    klaviyo_authorization = fields.Char("Klaviyo Auth",default="Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464",required=True)
    shopify_access_token = fields.Char("Shopify Access Token",default="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",required=True)
