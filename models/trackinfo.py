from odoo import models, fields, api
import requests 
import json
import base64
import re

class track_info(models.Model):
    _name = 'shopify.track_info'
    _description = 'shopify.track_info'

    name = fields.Char(string="Carrier Name")
    created_by = fields.Char(string="Created By")
    tracking_number = fields.Char(string="Tracking Number")
    pod = fields.Char(string="POD") 
    provider_site = fields.Char(string="Provider Site")
    provider_telephone = fields.Char(string="Provider Telephone")
    package_state = fields.Char(string="Package State") 
    
    interval_days = fields.Char(string="Interval Days")
    tracking_status = fields.Char(string="Tracking Status")
    
    waybill_number = fields.Char(string="WayBill Number")
    provider_name = fields.Char(string="Provider Name")
    country_code = fields.Char(string="Country Code")
    message = fields.Char(string="Message")
    order_tracking_status = fields.Char(string="Order Tracking Status")
    track_code_description = fields.Char(string="Track Code Description")
    abnormal_reasons_code = fields.Char(string="Abnormal Reasons Code")
    abnormal_reason = fields.Char(string="Abnormal Reason")
    process_location = fields.Char(string="Process Location")
    process_province = fields.Char(string="Process Province")
    process_content = fields.Char(string="Process Content")
    process_date = fields.Char(string="Process Date")
    process_country = fields.Char(string="Process Country")
    process_city = fields.Char(string="Process City")
    process_code = fields.Char(string="Process Code")
    
    order_id = fields.Many2one('shopify.shopify_order', string='Order')
