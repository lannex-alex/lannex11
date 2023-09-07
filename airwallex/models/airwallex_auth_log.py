from odoo import models, fields, api

class AirwallexAuthLog(models.Model):
    _name = "airwallex.auth.log"
    _description = "Airwallex Auth Log"
    _order = "id desc"
    _rec_name = 'time'

    time = fields.Datetime(default=lambda r: fields.Datetime.now())
    post = fields.Text()
    code_verifier = fields.Char()
