# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import base64
import re

class user_data(models.Model):
    _name = 'shopify.user_data'
    _description = 'shopify.user_data'

    name = fields.Char(string="Name")
    user_number = fields.Char(string="Number")
    user_streat = fields.Char(string="Streat")
    # user_city = fields.Char(string="City")
    # user_country = fields.Char(string="Country")
    user_country = fields.Many2one('res.country', string='Country')
    user_city = fields.Many2one('res.country.state', string='State')
    shopify_product_id = fields.Char(string="Shopify Product ID")

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
        response = requests.post('https://64c2fc-2.myshopify.com/admin/api/2023-04/orders.json',headers=headers,json=json_data)
        res = json.loads(response.text)
        shopify_order_id  = res['order']['id']
        status = res['order']['financial_status']
        vals = {'shopify_order_id':shopify_order_id,'order_status' :status}
        self.env['shopify.shopify_order'].create(vals)
        # self.write({"shopify_order_id " : shopify_order_id  ,"order_status" : status })

class shopify_product_template(models.Model):
    _inherit = 'product.template'


    shopify_product_id = fields.Char(string="Shopify Product ID")
    shopify_variant_id = fields.Char(string="shopify_variant_id")




    # def get_product(self):
    #     headers = {
    #             'Content-Type': 'application/json',
    #             'X-Shopify-Access-Token': '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',
    #         }

    #     regex = re.compile(r'<[^>]+>')
    #     response = requests.get('https://0bdd72.myshopify.com/admin/api/2023-04/products.json', headers=headers)
    #     def remove_html(string):
    #         return regex.sub('', string)
    #     res = json.loads(response.text)
    #     for res in res['products']:
    #         shopify_product_id =  res['id']
    #         shopify_product_title = res['title']
    #         shopify_desc = remove_html(res['body_html']).strip()
    #         shopify_product_price = res['variants'][0]['price']
    #         img_url = res['image']['src']
    #         response_img = requests.get(img_url)
    #         if response.status_code:
    #             fp = open(f'{shopify_product_title}.jpg', 'wb')
    #             fp.write(response_img.content)
    #             fp.close()
    #         with open(f"{shopify_product_title}.jpg", "rb") as img_file:
    #             my_string = base64.b64encode(img_file.read())
    #             my_image = my_string
    #         print(shopify_desc)
    #         shopify_product = self.env['product.template'].search([('shopify_product_id','=',shopify_product_id)])
    #         if shopify_product:
    #             print("Product already exist")
    #         else:
    #             vals = {'shopify_product_id':shopify_product_id,'name':shopify_product_title,'list_price':shopify_product_price,'image_1920': my_image,'description': shopify_desc}
    #             product_id = self.env['product.template'].create(vals)
    #             print(product_id)
