from odoo import models, fields, _
from odoo.exceptions import UserError

from datetime import datetime, timedelta



class AirwallexEditJournalWizard(models.TransientModel):
    _name = "airwallex.edit.journal.wizard"
    _description = "Airwallex Edit Journal Wizard"

    balance_id = fields.Many2one('airwallex.balance')
    currency_id = fields.Many2one(related="balance_id.currency_id", comodel_name='res.currency')
    journal_id = fields.Many2one('account.journal')
    init_journal = fields.Selection([
        ('import_historic_data', 'Import Historic Data'),
        ('initial_balance', 'Set Initial Balance'),
        ('none', 'None'),
    ], default='initial_balance')
    threshold_date = fields.Datetime(string="Threshold Date", default=lambda r: datetime.now() - timedelta(days=90))

    def process(self):
        self.ensure_one()
        balance = self.balance_id.sudo().with_context(airwallex_creation=True)
        balance.write({
            'journal_id': self.journal_id.id,
        })
        self.journal_id.sudo().write({
            'currency_id': self.currency_id.id
        })
        if self.journal_id:
            if self.init_journal == 'initial_balance':
                return balance.init_journal()
            if self.init_journal == 'import_historic_data':
                date = self.threshold_date or self.balance_id.airwallex_account_id.airwallex_account_created_at
                if not date:
                    raise UserError(_("You need to provide a Threshold Date"))
                return balance.import_historic_data(date)
