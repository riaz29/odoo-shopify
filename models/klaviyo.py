# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json

class klaviyo_campaign_template(models.Model):
    _name = 'shopify.klaviyo_campaign_template'
    _description = 'shopify.klaviyo_campaign_template'

    TYPE_SELECTION = [
        ('outreach', 'Outreach'),
        ('delivery_followup', 'Delivery Followup'),
        ('register', 'Register' )
    ]

    # campaign_name = fields.Char(string="Compaign Name")
    # compaign_id = fields.Char(string="Compaign ID")
    # compaign_status = fields.Char(string="Compaign Status" , default="Created")
    # message_label = fields.Char(string="Message Label",help="Text to be shown in Email Client List View.")
    # message_subject = fields.Char(string="Subject")
    # preview_text = fields.Text(string="Preview Text")
    template_name = fields.Char(string="Template Name")
    template_id = fields.Char(string="Template ID")
    sent_count = fields.Integer(string="Sent Count") 
    template_type = fields.Selection(TYPE_SELECTION, string='Template Type',default='outreach')

    def import_template(self):

        url = "https://a.klaviyo.com/api/templates/"
        headers = {
            "accept": "application/json",
            "revision": "2023-02-22",
            "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
        }
        response = requests.get(url, headers=headers)

        # print(response.text)

        data = json.loads(response.text)
        print(data['data'][1])
        for res in data['data']:
            template_id = res['id']
            template_name = res['attributes']['name']
            vals = {'template_id': template_id , 'template_name' :template_name, 'sent_count' :0}
            campaign_template = self.env['shopify.klaviyo_campaign_template'].create(vals)
            print(campaign_template.id)
            print("ID :", res['id'],",","Editor_Type :", res['attributes']['name'])

        #     # print(res[1])

    def import_campaign(self):
        campaign_url = "https://a.klaviyo.com/api/campaigns/"
        message_url = "https://a.klaviyo.com/api/campaign-messages/id/"
        headers = {
            "accept": "application/json",
            "revision": "2023-02-22",
            "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
        }
        response = requests.get(campaign_url, headers=headers)
        res = json.loads(response.text)
        for res in res['data']:
            campaign_obj = self.env['shopify.klaviyo_campaign_template'].search([('compaign_id','=',res['id'])])
            if campaign_obj:
                print("Record already exists")
            else:    
                campaign_id = res['id'] 
                campaign_name = res['attributes']['name']
                campaign_status = res['attributes']['status']
                message_id = res['attributes']['message']
                message_url = f"https://a.klaviyo.com/api/campaign-messages/{message_id}/"
                message_response = requests.get(message_url, headers=headers)
                message_res = json.loads(message_response.text)
                # print(message_res['data'])
                message_label = message_res['data']['attributes']['label']
                message_subject = message_res['data']['attributes']['content']['subject']
                preview_text = message_res['data']['attributes']['content']['preview_text']
                # print(campaign_id,campaign_name,message_label,message_subject)
                vals = {'compaign_id':campaign_id,'campaign_name':campaign_name,'compaign_status':campaign_status,'message_label': message_label,'message_subject': message_subject,'preview_text':preview_text}
                campaign = self.env['shopify.klaviyo_campaign_template'].create(vals)
                print(campaign.id)




class klaviyo_keys(models.Model):
    _name = 'shopify.klaviyo_keys'
    _description = 'shopify.klaviyo_keys'

    account_name = fields.Char(string="Account Name")
    public_key = fields.Char(string="Account Public Key")
    private_key = fields.Char(string="Account Private Key")

class klaviyo_campaign(models.Model):
    _name = 'shopify.klaviyo_campaign'
    _description = 'shopify.klaviyo_campaign'

    name = fields.Char(string="Compaign Name")
    audiance_list_id = fields.Many2many('shopify.google_sheet',string="Audience Emails")
    method = fields.Char(string="Method")
    message_id = fields.Char(string="Message ID")
    compaign_id = fields.Char(string="Compaign ID")
    compaign_status = fields.Char(string="Compaign Status" , default="Created")
    message_label = fields.Char(string="Preview",help="Text to be shown in Email Client List View.")
    message_subject = fields.Char(string="Subject")
    message_text = fields.Text(string="Message")



    @api.model
    def create(self, vals_list):
        klaviyo_profile_id = []
        audiance_email = []
        audiance_ids = vals_list['audiance_list_id'][0][2]
        # print(ids)
        for id in audiance_ids:
            data = self.env['shopify.google_sheet'].search([('id', '=', id )])
            audiance_email.append(data['name'])

        profile_url = "https://a.klaviyo.com/api/profiles/"

        for email_record in audiance_email:
            name  = email_record.rsplit('@', 1)
            first_name   = name[0]
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
            else:
                data = res['data']
                klaviyo_profile_id.append(data['id'])

        list_url = "https://a.klaviyo.com/api/lists/"
        compaign_list_name = vals_list['name'] + "_List"
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


        # print(vals_list['audiance_list_id'])
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
                    "name": vals_list['name'],
                    "channel": "email",
                    "audiences": {
                        "included": list_id
                    },
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
                    "template_id": "RswAUi"
                }
            }
        }

        message_update_payload = {
            "data": {
                "type": "campaign-message",
                "id": message_id,
                "attributes": {
                        "label": vals_list['message_label'],
                    "content": {
                        "subject": vals_list['message_subject'],
                        "preview_text": vals_list['message_text'],
                    }
                    }
                }
            }

        message_response = requests.post(message_url, json=message_payload, headers=headers)
        print(message_response.text)
        update_url = f"https://a.klaviyo.com/api/campaign-messages/{message_id}/"
        update_response = requests.patch(update_url, json=message_update_payload, headers=headers)
        print(update_response.text)

        vals_list['compaign_id'] = compaign_id
        vals_list['message_id'] = message_id
        compaign_data = super().create(vals_list)

        return compaign_data

    def compaignStart(self):
        url = "https://a.klaviyo.com/api/campaign-send-jobs/"

        payload = {"data": {
                "type": "campaign-send-job",
                "attributes": {
                    "id": self.compaign_id
                    }
            }}
        headers = {
            "accept": "application/json",
            "revision": "2023-02-22",
            "content-type": "application/json",
            "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
        }

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        res = json.loads(response.text)
        data = res['data']
        status = data['attributes']['status']
        self.write({"compaign_status" : status})

    def updateStatus(self):
        compaign_id = self.compaign_id
        url = f"https://a.klaviyo.com/api/campaign-send-jobs/{compaign_id}/"

        headers = {
                "accept": "application/json",
                "revision": "2023-02-22",
                "Authorization": "Klaviyo-API-Key pk_53824b9fd492daec7659f12175c0930464"
            }
        response = requests.get(url, headers=headers)
        res = json.loads(response.text)
        data = res['data']
        status = data['attributes']['status']
        self.write({"compaign_status" : status})
