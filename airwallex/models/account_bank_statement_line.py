from odoo import models, fields, api


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    _sql_constraints = [
       ('airwalex_payment_token_unique', 'UNIQUE(airwalex_payment_token)', 'Airwallex payment token should be unique!')
    ]

    airwallex_statement_id = fields.Many2one(comodel_name="airwallex.statement")
    airwalex_payment_token = fields.Char(string="Airwallex payment token", index=True, readonly=True)
    airwalex_raw_info = fields.Char(string="Airwallex raw info", readonly=True)
    airwallex_datetime = fields.Datetime(readonly=True)
    airwallex_balance = fields.Monetary()

    @api.model
    def prepare_statement_values(self, items, bank_statement):
        res = {}
        for item in items:
            token = f'{item.get("source_type")}__{item.get("source")}'
            res[token] = {
                'airwalex_payment_token': token,
                'transaction_type': item.get("source_type"),
                'amount': item.get("amount"),
                'payment_ref': item.get("description"),
                'statement_id': bank_statement.id,
                'airwallex_datetime': self.env['airwallex.account']._format_date_from_airwallex(item.get("posted_at")),
                'airwallex_balance': item.get("balance"),
            }

        return res
