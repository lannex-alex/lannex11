from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    airwallex_balance_ids = fields.One2many(related="journal_id.airwallex_balance_ids")
    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        if not self.env.context.get('airwallex_creation') and res.airwallex_balance_ids:
            raise ValidationError(_("You are trying to create a bank statement on Airwallex associated journal. You are not allowed to perform such action"))

        return res
