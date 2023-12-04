# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import base64
import re


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    active = fields.Boolean("Active",default=True)

class shopify_order(models.Model):
    _name = 'shopify.shopify_order'
    _description = 'shopify.shopify_order'

    order_name = fields.Char(string="Order Name")
    shopify_order_id  = fields.Char(string="Order ID")
    order_status = fields.Char(string="Order Name")
    order_create = fields.Boolean(string="Order Created" , default=False)
    track_ids = fields.One2many('shopify.track_info', 'order_id', string='Track Info')

    def run_campagin(self):
        customer_number = "C06901"
        api_secret = "3VniAsdO6mU="
        key_data = customer_number + "&" + api_secret
        encoded_data = base64.b64encode(key_data.encode()).decode()
        track_url = "http://omsapi.uat.yunexpress.com/api/WayBill/GetOrder"

        header ={
            'Authorization' : f'Basic {encoded_data}',
            'Content-Type': 'application/json',
        }
        # params = {
        #     "OrderNumber" : self.shopify_order_id
        # }
        params = {
            "OrderNumber" : "PKR19931240"
        }
        response = requests.get(
            track_url,
            headers=header,
            params=params,
        )
        data = response.json()
        email = data['Item']['Receiver']['Email']
        first_name = data['Item']['Receiver']['FirstName']
        last_name = data['Item']['Receiver']['LastName']
        
        campaign_object = self.env['shopify.klaviyo_campaign_template'].search([('template_type', '=', "delivery_followup")])
        print(campaign_object)
        campaign_name = "Outreach Campaign Template"
        label = "Outreach Campaign Template"
        subject = "Outreach Campaign Template"
        preview_text = "Outreach Campaign Template"
        template_id = campaign_object.template_id

        # campaign_name = campaign_object.campaign_name 
        # label = campaign_object.message_label
        # subject = campaign_object.message_subject
        # preview_text = campaign_object.preview_text

        # print("Name",campaign_name)
        # print("Label",label)
        # print("Subject",subject)
        # print("Preview Text",preview_text)
        # print("Campaign Type",campaign_object['campaign_type'])

        profile_url = "https://a.klaviyo.com/api/profiles/"
        audiance_payload = {
                "data": {
                    "type": "profile",
                    "attributes": {
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "organization": "XYZ"
                    }
                }}
        klaviyo_headers = {
            "accept": "application/json",
            "revision": "2023-02-22",
            "content-type": "application/json",
            "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
        }

        response = requests.post(profile_url, json=audiance_payload, headers=klaviyo_headers)
        res = json.loads(response.text)
        if 'errors' in res:
            id = res['errors'][0]['meta']['duplicate_profile_id']
            klaviyo_profile_id = id 
            print("Already Record Found")
        else:
            data = res['data']
            klaviyo_profile_id = data['id']
        print("Klaviyo ID", klaviyo_profile_id)

        list_url = "https://a.klaviyo.com/api/lists/"
        compaign_list_name =  campaign_name +"_List"
        print(compaign_list_name)
        list_payload = {
            "data": {
                "type": "list",
                "attributes": {"name": compaign_list_name}
            }
            }
        headers = {
            "accept": "application/json",
            "revision": "2023-02-22",
            "content-type": "application/json",
            "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
        }

        response = requests.post(list_url, json=list_payload, headers=headers)
        list_res = json.loads(response.text)
        list_data = list_res['data']
        list_id = list_data['id']
        add_audiance_url = f"https://a.klaviyo.com/api/lists/{list_id}/relationships/profiles/"
       
        add_payload = {
            "data": [
                        {
                            "type": "profile",
                            "id": klaviyo_profile_id
                    } ]
            }
        headers = {
            "accept": "application/json",
            "revision": "2023-02-22",
            "content-type": "application/json",
            "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
        }

        response = requests.post(add_audiance_url, json=add_payload, headers=headers)
        
        url = "https://a.klaviyo.com/api/campaigns/"
        message_url = "https://a.klaviyo.com/api/campaign-message-assign-template/"

        headers = {
            "accept": "application/json",
            "revision": "2023-02-22",
            "content-type": "application/json",
            "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
        }

        payload = {
            "data": {
                "type": "campaign",
                "attributes": {
                    "name": campaign_name,
                    "channel": "email",
                    "audiences": {
                        "included": list_id
                    },
                    "send_options": {"use_smart_sending": False},
                    "send_strategy": {
                        "method": "immediate",
                        # "options_static": {"datetime": "2022-11-08T00:00:00"}
                    }
                }
            }}


        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        res = json.loads(response.text)
        data = res['data']
        compaign_id = data['id']
        message_id = data['attributes']['message']

        message_payload = {
            "data": {
                "type": "campaign-message",
                "attributes": {
                    "id": message_id,
                    "template_id": template_id
                }
            }
        }

        message_update_payload = {
            "data": {
                "type": "campaign-message",
                "id": message_id,
                "attributes": {
                        "label": label,
                    "content": {
                        "subject":subject,
                        "preview_text": preview_text,
                    }
                    }
                }
            }

        message_response = requests.post(message_url, json=message_payload, headers=headers)
        print(message_response.text)
        update_url = f"https://a.klaviyo.com/api/campaign-messages/{message_id}/"
        update_response = requests.patch(update_url, json=message_update_payload, headers=headers)
        print(update_response.text)

        sent_count = campaign_object.sent_count + 1
        campaign_object.write({'sent_count': sent_count})
        run_url = "https://a.klaviyo.com/api/campaign-send-jobs/"
        run_payload = {"data": {
                "type": "campaign-send-job",
                "attributes": {
                    "id": compaign_id
                    }
            }}
        headers = {
            "accept": "application/json",
            "revision": "2023-02-22",
            "content-type": "application/json",
            "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
        }

        response = requests.post(run_url, json=run_payload, headers=headers)
        print(response.text)
        res = json.loads(response.text)
        data = res['data']
        status = data['attributes']['status']
        print("Campaign",status) 
        
    # def get_shopify_track_info(self):
    #     headers = {
    #         'X-Shopify-Access-Token': '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',
    #         'Content-Type': 'application/json',
    #     }

    #     response = requests.get(
    #         'https://328ccd.myshopify.com/admin/api/2023-04/orders/5345553940753.json',
    #         headers=headers,
    #     )
    #     if response.status_code == 200:
    #         order_data = response.json()['order']
    #         fulfillments = order_data['fulfillments']
    #         if fulfillments:
    #             for fulfillment in fulfillments:
    #                 tracking_number = fulfillment['tracking_number']
    #                 tracking_company = fulfillment['tracking_company']
                    
    #                 if tracking_number is not None:
    #                     print("Tracking Number is : ", tracking_number)
    #                     # customer_number = "C06901"
    #                     # api_secret = "3VniAsdO6mU="
    #                     # key_data = customer_number + "&" + api_secret
    #                     # encoded_data = base64.b64encode(key_data.encode()).decode()
    #                     # track_url = "http://omsapi.uat.yunexpress.com/api/Tracking/GetTrackAllInfo"

    #                     # header ={
    #                     #     'Authorization' : f'Basic {encoded_data}',
    #                     #     'Content-Type': 'application/json',
    #                     # }

    #                     # params = {
    #                     #     "OrderNumber" : self.shopify_order_id
    #                     # }
    #                     # response = requests.get(track_url,headers=header,params=params)
    #                     # byte_data = response.content 
    #                     # string_data = byte_data.decode('utf-8')
    #                     # res = json.loads(string_data)
    #                     # name = res['Item']['CarrierName']
    #                     # created_by = res['Item']['CreatedBy']
    #                     # tracking_number = res['Item']['TrackingNumber']
    #                     # pod = res['Item']['POD']
    #                     # provider_site = res['Item']['ProviderSite']
    #                     # provider_telephone = res['Item']['ProviderTelephone']
    #                     # package_state = res['Item']['PackageState']
    #                     # interval_days = res['Item']['IntervalDays']
    #                     # tracking_status = res['Item']['TrackingStatus']
    #                     # # origin_country_code = res['Item']['OriginCountryCode']
    #                     # waybill_number = res['Item']['WayBillNumber']
    #                     # provider_name = res['Item']['ProviderName']
    #                     # country_code = res['Item']['CountryCode']
    #                     # message = res['Message']
    #                     # order_tracking_status = res['Item']['OrderTrackingDetails'][0]['TrackingStatus']
    #                     # track_code_description  = res['Item']['OrderTrackingDetails'][0]['TrackCodeDescription']
    #                     # # abnormal_reasons_code = res['Item']['OrderTrackingDetails'][0]['AbnormalReasons'][0]['AbnormalReasonCode']
    #                     # # abnormal_reason = res['Item']['OrderTrackingDetails'][0]['AbnormalReasons'][0]['AbnormalReason']
    #                     # process_location = res['Item']['OrderTrackingDetails'][0]['ProcessLocation']
    #                     # process_province = res['Item']['OrderTrackingDetails'][0]['ProcessProvince']
    #                     # process_content  = res['Item']['OrderTrackingDetails'][0]['ProcessContent']
    #                     # process_date = res['Item']['OrderTrackingDetails'][0]['ProcessDate']
    #                     # process_country = res['Item']['OrderTrackingDetails'][0]['ProcessCountry']
    #                     # process_city = res['Item']['OrderTrackingDetails'][0]['TrackNodeCode']
    #                     # process_code = res['Item']['OrderTrackingDetails'][0]['ProcessCity']
                        
    #                     # vals = {'name':name,'created_by':created_by,'tracking_number':tracking_number,
    #                     #             'pod':pod,'provider_site':provider_site,'provider_telephone':provider_telephone,
    #                     #             'package_state':package_state,'interval_days':interval_days,
    #                     #             'tracking_status':tracking_status,
    #                     #             'waybill_number':waybill_number,'provider_name':provider_name,
    #                     #             'country_code':country_code, 'message':message,
    #                     #             'order_tracking_status':order_tracking_status,'track_code_description':track_code_description,
    #                     #             'process_location':process_location,  'process_province':process_province,
    #                     #             'process_content':process_content,'process_date':process_date,
    #                     #             'process_country':process_country,'process_city':process_city,
    #                     #             'process_code':process_code, 'order_id' : self.id
    #                     #             }
    #                     # print(vals)
    #                     # order_track_id = self.env['shopify.track_info'].create(vals)
    #                     # print(order_track_id)
                        
                        
                        
    #                 else:
    #                     print("Tracking_number is None")


    def get_track_info(self):
        customer_number = "C06901"
        api_secret = "3VniAsdO6mU="
        key_data = customer_number + "&" + api_secret
        encoded_data = base64.b64encode(key_data.encode()).decode()
        track_url = "http://omsapi.uat.yunexpress.com/api/Tracking/GetTrackAllInfo"

        header ={
            'Authorization' : f'Basic {encoded_data}',
            'Content-Type': 'application/json',
        }

        params = {
            "OrderNumber" : "PKR19931235"
        }
        response = requests.get(track_url,headers=header,params=params)
        byte_data = response.content 
        string_data = byte_data.decode('utf-8')
        res = json.loads(string_data)
        print(res)
        name = res['Item']['CarrierName']
        created_by = res['Item']['CreatedBy']
        tracking_number = res['Item']['TrackingNumber']
        pod = res['Item']['POD']
        provider_site = res['Item']['ProviderSite']
        provider_telephone = res['Item']['ProviderTelephone']
        package_state = res['Item']['PackageState']
        interval_days = res['Item']['IntervalDays']
        tracking_status = res['Item']['TrackingStatus']
        # origin_country_code = res['Item']['OriginCountryCode']
        waybill_number = res['Item']['WayBillNumber']
        provider_name = res['Item']['ProviderName']
        country_code = res['Item']['CountryCode']
        message = res['Message']
        order_tracking_status = res['Item']['OrderTrackingDetails'][0]['TrackingStatus']
        track_code_description  = res['Item']['OrderTrackingDetails'][0]['TrackCodeDescription']
        # abnormal_reasons_code = res['Item']['OrderTrackingDetails'][0]['AbnormalReasons'][0]['AbnormalReasonCode']
        # abnormal_reason = res['Item']['OrderTrackingDetails'][0]['AbnormalReasons'][0]['AbnormalReason']
        process_location = res['Item']['OrderTrackingDetails'][0]['ProcessLocation']
        process_province = res['Item']['OrderTrackingDetails'][0]['ProcessProvince']
        process_content  = res['Item']['OrderTrackingDetails'][0]['ProcessContent']
        process_date = res['Item']['OrderTrackingDetails'][0]['ProcessDate']
        process_country = res['Item']['OrderTrackingDetails'][0]['ProcessCountry']
        process_city = res['Item']['OrderTrackingDetails'][0]['TrackNodeCode']
        process_code = res['Item']['OrderTrackingDetails'][0]['ProcessCity']
        
        vals = {'name':name,'created_by':created_by,'tracking_number':tracking_number,
                    'pod':pod,'provider_site':provider_site,'provider_telephone':provider_telephone,
                    'package_state':package_state,'interval_days':interval_days,
                    'tracking_status':tracking_status,
                    'waybill_number':waybill_number,'provider_name':provider_name,
                    'country_code':country_code, 'message':message,
                    'order_tracking_status':order_tracking_status,'track_code_description':track_code_description,
                    'process_location':process_location,  'process_province':process_province,
                    'process_content':process_content,'process_date':process_date,
                    'process_country':process_country,'process_city':process_city,
                    'process_code':process_code, 'order_id' : self.id
                    }
        print(vals)
        order_track_id = self.env['shopify.track_info'].create(vals)
        print(order_track_id)
        

    def add_order(self):
        headers = {
                'X-Shopify-Access-Token': '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',
                'Content-Type': 'application/json',
            }
        json_data = {
            'order': {
                'line_items': [
                    {
                        'variant_id': 45239640457496,
                        'quantity': 1,
                    },
                ],
                'customer': {
                    'id': 6954217832728,
                },
            },
        }
        response = requests.post('https://2373fc.myshopify.com/admin/api/2023-04/orders.json',headers=headers,json=json_data)
        res = json.loads(response.text)
        shopify_order_id  = res['order']['id']
        status = res['order']['financial_status']
        self.write({"shopify_order_id " : shopify_order_id  ,"order_status" : status })

    
    
    def get_product(self):
        headers = {
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': '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',
            }

        regex = re.compile(r'<[^>]+>')
        response = requests.get('https://64c2fc-2.myshopify.com/admin/api/2023-04/products.json', headers=headers)
        def remove_html(string):
            return regex.sub('', string)
        res = json.loads(response.text)
        for res in res['products']:
            shopify_product_id =  res['id']
            shopify_product_title = res['title']
            shopify_desc = remove_html(res['body_html']).strip()
            shopify_product_price = res['variants'][0]['price']
            shopify_variant_id = res['variants'][0]['id']
            img_url = res['image']['src']
            response_img = requests.get(img_url)
            if response.status_code:
                fp = open(f'{shopify_product_title}.jpg', 'wb')
                fp.write(response_img.content)
                fp.close()
            with open(f"{shopify_product_title}.jpg", "rb") as img_file:
                my_string = base64.b64encode(img_file.read())
                my_image = my_string
            print(shopify_desc)
            shopify_product = self.env['product.template'].search([('shopify_product_id','=',shopify_product_id)])
            if shopify_product:
                print("Product already exist")
            else:
                vals = {'shopify_product_id':shopify_product_id,'name':shopify_product_title,'list_price':shopify_product_price,'image_1920': my_image,'description': shopify_desc,'shopify_variant_id' : shopify_variant_id}
                product_id = self.env['product.template'].create(vals)
                print(product_id)
