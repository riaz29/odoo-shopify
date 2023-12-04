# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json


class google_sheet(models.Model):
    _name = 'shopify.google_sheet'
    _description = 'shopify.google_sheet'

    sheet_record_id = fields.Char(string="Sheet Record ID")
    klaviyo_id = fields.Char(string="Klaviyo ID")
    channel_name = fields.Char(string="Channel Name")
    channel_url = fields.Char(string="Channel URl")
    follower_count = fields.Char(string="Follower Count")
    name = fields.Char(string="Account Email")
    searching_keyword = fields.Char(string="Searching Keyword")
    category = fields.Char(string="Category")
    yes_no = fields.Char(string="Y/N")
    outreach_sent = fields.Boolean(string="Outreach Sent" , default=False)

    def custom_profile_fields(self):
        sheet_record = self.env['shopify.google_sheet'].search([('outreach_sent', '=', False)])
        for rec in sheet_record:
            print("Klaviyo ID", rec.klaviyo_id)

            url = f"https://a.klaviyo.com/api/profiles/{rec.klaviyo_id}/"
            payload = {
                "data": {
                    "type": "profile",
                    "id": rec.klaviyo_id,
                    "attributes": {
                        "properties": {
                            "coupon": "ZXCqwe",
                            "affiliate_url": "https://abc.com.pk",
                            }
                    }
                }}
            headers = {
                "accept": "application/json",
                "revision": "2023-02-22",
                "content-type": "application/json",
                "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
            }

            response = requests.patch(url, json=payload, headers=headers)

            print(response.text)


    def compaign_send_outreach(self):
        klaviyo_profile_id = []
        audiance_list = []
        sheet_record = self.env['shopify.google_sheet'].search([('outreach_sent', '=', False)])
        for rec in sheet_record:
            # print("Email ID is ", rec['name'])
            audiance_list.append(rec['name'])
        print(audiance_list)    

        campaign_object = self.env['shopify.klaviyo_campaign_template'].search([('template_type', '=', "outreach")],  order='id desc' , limit=1)
        # print(campaign_object)

        campaign_name = "Outreach Campaign Template"
        label = "Outreach Campaign Template"
        subject = "Outreach Campaign Template"
        preview_text = "Outreach Campaign Template"
        template_id = campaign_object.template_id
        print(template_id)
        # # print("Name",campaign_name, type(campaign_object['campaign_name']))
        # # print("Label",label)
        # # print("Subject",subject)
        # # print("Preview Text",preview_text)
        # # print("Campaign Type",campaign_object['campaign_type'])

        profile_url = "https://a.klaviyo.com/api/profiles/"

        for email_record in audiance_list:
            username  = email_record.rsplit('@', 1)
            first_name   = username[0]
            payload = {
                "data": {
                    "type": "profile",
                    "attributes": {
                        "email": email_record,
                        "first_name": first_name,
                        "organization": "XYZ"
                    }
                }}
            headers = {
                "accept": "application/json",
                "revision": "2023-02-22",
                "content-type": "application/json",
                "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
            }

            response = requests.post(profile_url, json=payload, headers=headers)
            res = json.loads(response.text)
            if 'errors' in res:
                id = res['errors'][0]['meta']['duplicate_profile_id']
                klaviyo_profile_id.append(id)
                google_sheet = self.env['shopify.google_sheet'].search([('name', '=', email_record)])
                google_sheet.write({"klaviyo_id" : id})
            else:
                data = res['data']
                klaviyo_profile_id.append(data['id'])
                google_sheet = self.env['shopify.google_sheet'].search([('name', '=', email_record)])
                google_sheet.write({"klaviyo_id" : data['id']})
                
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
        for klaviyo_profile in klaviyo_profile_id:
            add_payload = {
                "data": [
                            {
                                "type": "profile",
                                "id": klaviyo_profile
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
        compaign_id = compaign_id
        print(compaign_id)
        # print(campaign_object)
        run_payload = {"data": {
                "type": "campaign-send-job",
                "attributes": {
                    "id": compaign_id
                    }
            }}
        run_headers = {
            "accept": "application/json",
            "revision": "2023-02-22",
            "content-type": "application/json",
            "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
        }

        response = requests.post(run_url, json=run_payload, headers=run_headers)
        print(response.text)
        res = json.loads(response.text)
        data = res['data']
        status = data['attributes']['status']
        print("Campaign",status) 
        for audiance_list in audiance_list:
            google_sheet = self.env['shopify.google_sheet'].search([('name', '=', audiance_list)])
            google_sheet.write({"outreach_sent" : True})


    # def compaign_send_outreach(self):
    #     klaviyo_profile_id = []
    #     audiance_list = []
    #     sheet_record = self.env['shopify.google_sheet'].search([('outreach_sent', '=', False)])
    #     for rec in sheet_record:
    #         # print("Email ID is ", rec['name'])
    #         audiance_list.append(rec['name'])
    #     print(audiance_list)    

    #     campaign_object = self.env['shopify.klaviyo_campaign_template'].search([('campaign_type', '=', "outreach")])
    #     print(campaign_object)

    #     campaign_name = campaign_object.campaign_name 
    #     label = campaign_object.message_label
    #     subject = campaign_object.message_subject
    #     preview_text = campaign_object.preview_text

    #     print("Name",campaign_name, type(campaign_object['campaign_name']))
    #     print("Label",label)
    #     print("Subject",subject)
    #     print("Preview Text",preview_text)
    #     print("Campaign Type",campaign_object['campaign_type'])

    #     profile_url = "https://a.klaviyo.com/api/profiles/"

    #     for email_record in audiance_list:
    #         username  = email_record.rsplit('@', 1)
    #         first_name   = username[0]
    #         payload = {
    #             "data": {
    #                 "type": "profile",
    #                 "attributes": {
    #                     "email": email_record,
    #                     "first_name": first_name,
    #                     "organization": "XYZ"
    #                 }
    #             }}
    #         headers = {
    #             "accept": "application/json",
    #             "revision": "2023-02-22",
    #             "content-type": "application/json",
    #             "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
    #         }

    #         response = requests.post(profile_url, json=payload, headers=headers)
    #         res = json.loads(response.text)
    #         if 'errors' in res:
    #             id = res['errors'][0]['meta']['duplicate_profile_id']
    #             klaviyo_profile_id.append(id)
    #         else:
    #             data = res['data']
    #             klaviyo_profile_id.append(data['id'])
            
    #     list_url = "https://a.klaviyo.com/api/lists/"
    #     compaign_list_name =  campaign_name +"_List"
    #     print(compaign_list_name)
    #     list_payload = {
    #         "data": {
    #             "type": "list",
    #             "attributes": {"name": compaign_list_name}
    #         }
    #         }
    #     headers = {
    #         "accept": "application/json",
    #         "revision": "2023-02-22",
    #         "content-type": "application/json",
    #         "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
    #     }

    #     response = requests.post(list_url, json=list_payload, headers=headers)
    #     list_res = json.loads(response.text)
    #     list_data = list_res['data']
    #     list_id = list_data['id']
    #     add_audiance_url = f"https://a.klaviyo.com/api/lists/{list_id}/relationships/profiles/"
    #     for klaviyo_profile in klaviyo_profile_id:
    #         add_payload = {
    #             "data": [
    #                         {
    #                             "type": "profile",
    #                             "id": klaviyo_profile
    #                     } ]
    #             }
    #         headers = {
    #             "accept": "application/json",
    #             "revision": "2023-02-22",
    #             "content-type": "application/json",
    #             "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
    #         }

    #         response = requests.post(add_audiance_url, json=add_payload, headers=headers)
        
    #     url = "https://a.klaviyo.com/api/campaigns/"
    #     message_url = "https://a.klaviyo.com/api/campaign-message-assign-template/"

    #     headers = {
    #         "accept": "application/json",
    #         "revision": "2023-02-22",
    #         "content-type": "application/json",
    #         "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
    #     }

    #     payload = {
    #         "data": {
    #             "type": "campaign",
    #             "attributes": {
    #                 "name": campaign_name,
    #                 "channel": "email",
    #                 "audiences": {
    #                     "included": list_id
    #                 },
    #                 "send_options": {"use_smart_sending": False},
    #                 "send_strategy": {
    #                     "method": "immediate",
    #                     # "options_static": {"datetime": "2022-11-08T00:00:00"}
    #                 }
    #             }
    #         }}


    #     response = requests.post(url, json=payload, headers=headers)
    #     print(response.text)
    #     res = json.loads(response.text)
    #     data = res['data']
    #     compaign_id = data['id']
    #     message_id = data['attributes']['message']

    #     message_payload = {
    #         "data": {
    #             "type": "campaign-message",
    #             "attributes": {
    #                 "id": message_id,
    #                 "template_id": "RswAUi"
    #             }
    #         }
    #     }

    #     message_update_payload = {
    #         "data": {
    #             "type": "campaign-message",
    #             "id": message_id,
    #             "attributes": {
    #                     "label": label,
    #                 "content": {
    #                     "subject":subject,
    #                     "preview_text": preview_text,
    #                 }
    #                 }
    #             }
    #         }

    #     message_response = requests.post(message_url, json=message_payload, headers=headers)
    #     print(message_response.text)
    #     update_url = f"https://a.klaviyo.com/api/campaign-messages/{message_id}/"
    #     update_response = requests.patch(update_url, json=message_update_payload, headers=headers)
    #     print(update_response.text)

    #     campaign_object.write({'compaign_id': compaign_id})
        
        
    #     for audiance_list in audiance_list:
    #         google_sheet = self.env['shopify.google_sheet'].search([('name', '=', audiance_list)])
    #         google_sheet.write({"outreach_sent" : True})



    # def compaignStart(self):
    #     campaign_object = self.env['shopify.klaviyo_campaign_template'].search([('campaign_type', '=', "outreach")])
    #     url = "https://a.klaviyo.com/api/campaign-send-jobs/"
    #     compaign_id = campaign_object.compaign_id
    #     print(compaign_id)
    #     # print(campaign_object)
    #     payload = {"data": {
    #             "type": "campaign-send-job",
    #             "attributes": {
    #                 "id": compaign_id
    #                 }
    #         }}
    #     headers = {
    #         "accept": "application/json",
    #         "revision": "2023-02-22",
    #         "content-type": "application/json",
    #         "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
    #     }

    #     response = requests.post(url, json=payload, headers=headers)
    #     print(response.text)
    #     res = json.loads(response.text)
    #     data = res['data']
    #     status = data['attributes']['status']
    #     campaign_object.write({"compaign_status" : status})
        



        
    def import_sheet(self):
        base_url = "https://sheets.googleapis.com/v4/spreadsheets"
        sheet_id = "1wN9PNO-cX3NVAhYNLqu5psr0GeUj6n0aNdTdwWBLO84"
        range = "A1:H3"

        headers = {"Content-Type": "application/json; charset=utf-8"}

        params = {
            "key" : "AIzaSyAq4FMO_oGh8GqOc90wXcS8KU-cMBCwf64"
        }

        response = requests.get(url=f"{base_url}/{sheet_id}/values/{range}" , params=params, headers=headers)

        # print(response.text)
        res = json.loads(response.text)
        data = res['values'][1:]

        for res in data:
            sheet_record_id = res[0]
            channel_name = res[1]
            channel_url = res[2]
            follower_count = res[3]
            name = res[4]
            searching_keyword = res[5]
            category = res[6]
            yes_no = res[7]

            vals = {'sheet_record_id':sheet_record_id,'channel_name':channel_name,'channel_url':channel_url,
                    'follower_count':follower_count,'name':name,'searching_keyword':searching_keyword,
                    'category':category,'yes_no':yes_no}
            sheet_id = self.env['shopify.google_sheet'].create(vals)
            print(sheet_id)
