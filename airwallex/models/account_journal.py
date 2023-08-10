from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    airwallex_balance_ids = fields.One2many('airwallex.balance', 'journal_id', readonly=True)
