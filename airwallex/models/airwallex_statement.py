from odoo import models, fields

class AirwallexStatement(models.Model):
    _name = "airwallex.statement"
    _description = "Airwallex Statement"
    _order = "id desc"

    airwallex_account_id = fields.Many2one("airwallex.account", string="Airwallex account")
    api_response = fields.Char(string="API response")
    bank_statement_ids = fields.Many2many('account.bank.statement', string="Bank statements")
    bank_statement_line_ids = fields.One2many(
        comodel_name='account.bank.statement.line', inverse_name="airwallex_statement_id",
        string="Bank statement lines")
