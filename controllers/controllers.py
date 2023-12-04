# -*- coding: utf-8 -*-
from odoo import http
from odoo import http
from odoo.http import request

class Shopify(http.Controller):
    @http.route(['/your/registration'], type='http', auth="public", website=True)
    def user_data(self):
       countries = request.env['res.country'].sudo().search([])
       states = request.env['res.country.state'].sudo().search([])
       product = request.env['product.template'].sudo().search([])
       website_product_ids = request.env['product.template'].sudo().search([])
       for res in website_product_ids:
            print("Name:", res.name)
            print("Name:", res.shopify_product_id)
            print("Name:", res.shopify_variant_id)
            # print("Name:", res.image_1920)
       return request.render("shopify.form_template" ,{
           'website_product_ids': website_product_ids,
            'countries': countries,
            'states': states})
    
    @http.route('/user_data/submit/', auth='public',  method=["POST"],csrf=False , website=True )
    def index(self, **kw):
        name = kw['name']
        number = kw['number']
        streat = kw['streat']
        city = kw['city']
        country = kw['country']
        product_id = kw['selected_products']
        
        print(product_id)
        vals={'name':name,'user_number':number, 'user_streat': streat,'user_city':city,'user_country':country,'shopify_product_id': product_id}
        user_data=request.env['shopify.user_data'].sudo().create(vals)
        user_data_id=user_data.id
        print("User Data ID",user_data_id)
        print(name,number,streat,city,country)
        return request.render("shopify.success_template")

    @http.route(['/slider'], type='http', auth='public', website=True)
    def sliders(self, **kwargs):
        website_product_ids = request.env['product.template'].sudo().search([])
        return request.render('shopify.product', {'website_product_ids': website_product_ids})
