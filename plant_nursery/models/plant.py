# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug


class Category(models.Model):
    _name = 'plant.category'
    _description = 'Plant Category'
    _order = 'name'
    _inherit = ['mail.alias.mixin']

    name = fields.Char('Name', required=True)

    def get_alias_model_name(self, vals):
        return 'plant.order'

    def get_alias_values(self):
        values = super(Category, self).get_alias_values()
        # values['alias_defaults'] = {'plant_ids: location_id': self.id}
        return values


class Tag(models.Model):
    _name = 'plant.tag'
    _description = 'Plant Tag'
    _order = 'name'

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color Index', default=10)


class Plants(models.Model):
    _name = 'plant.plant'
    _description = 'Plant'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.seo.metadata', 'website.published.mixin']

    name = fields.Char('Plant Name', required=True, track_visibility='always')
    # description
    description_short = fields.Html('Short description')
    description = fields.Html('Description')
    category_id = fields.Many2one('plant.category', string='Category')
    image = fields.Binary('Photo', attachment=True)
    tag_ids = fields.Many2many('plant.tag', string='Tags')
    # sell
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        index=True, required=True,
        default=lambda self: self.env.user)
    stock = fields.Integer('Stock')
    price = fields.Float('Price', track_visibility='onchange')

    @api.depends('name')
    def _compute_website_url(self):
        super(Plants, self)._compute_website_url()
        for location in self:
            if location.id:
                location.website_url = '/plant/%s' % slug(location)

    promo = fields.Boolean('Is in Promotion')

    @api.constrains('stock')
    def _check_stock(self):
        if self.stock < 0:
            raise exceptions.ValidationError(
                _('Stock cannot be negative.')
            )

    def _track_subtype(self, init_values):
        if 'price' in init_values:
            return 'plant_nursery.plant_price'
        return super(Plants, self)._track_subtype(init_values)

    def _track_template(self, tracking):
        res = super(Plants, self)._track_template(tracking)
        plant = self[0]
        changes, dummy = tracking[plant.id]
        if 'price' in changes:
            res['price'] = (self.env.ref('plant_nursery.mail_template_plant_price_updated'), {'composition_mode': 'mass_mail'})
        return res
