from odoo import models, fields, _
from datetime import datetime, timedelta


class AirwallexBalance(models.Model):
    _name = "airwallex.balance"
    _description = "Airwallex Wallet"

    _sql_constraints = [
        (
           'account_currency_id_unique',
           'UNIQUE(airwallex_account_id, currency_id)',
           'Airwallex Account cannot have 2 balance for the same currency!'
        )
    ]

    airwallex_account_id = fields.Many2one('airwallex.account')
    currency_id = fields.Many2one('res.currency')
    available_amount = fields.Monetary()
    pending_amount = fields.Monetary()
    reserved_amount = fields.Monetary()
    total_amount = fields.Monetary()
    journal_id = fields.Many2one('account.journal', readonly=True)
    last_sync_datetime = fields.Datetime()
    active = fields.Boolean(default=True)

    def action_update_balance(self):
        self.ensure_one()
        if self.journal_id:
            self.airwallex_account_id.fetch_transactions(
                                            date_from=self.last_sync_datetime, currency=self.currency_id.name)

    def action_open_edit_journal_wizard(self):
        self.ensure_one()
        context = self.env.context.copy()
        context.update({
            "default_balance_id": self.id,
        })
        return {
            'name': 'Edit Journal',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'airwallex.edit.journal.wizard',
            'view_id': self.env.ref('airwallex.airwallex_edit_journal_wizard_form').id,
            'target': 'new',
            'context': context,
        }

    def init_journal(self):
        self.ensure_one()
        statement = self.env['account.bank.statement'].create({
            'journal_id': self.journal_id.id,
            'balance_end_real': self.available_amount,
        })
        self.env['account.bank.statement.line'].create({
            'statement_id': statement.id,
            'payment_ref': 'Init Journal amount from Airwallex',
            'amount': self.available_amount - statement.balance_start,
        })

        statement.button_post()

    def import_historic_data(self, threshold_date):
        self.ensure_one()
        self.airwallex_account_id.get_airwallex_balance(currency=self.currency_id.name)
        date_from = self.last_sync_datetime
        statement = self.env['account.bank.statement'].create({
            'journal_id': self.journal_id.id,
        })
        while date_from > threshold_date:
            date_to = date_from
            date_from = max(date_to - timedelta(days=7), threshold_date)
            self.airwallex_account_id.fetch_transactions(page_num=0,
                                                        date_from=date_from,
                                                        date_to=date_to,
                                                        currency=self.currency_id.name, get_balance=False)

        first_statment = self.env['account.bank.statement.line'] \
                                .search([('airwallex_datetime', '!=', False)], order="airwallex_datetime ASC", limit=1)
        initial_amount = 0
        if first_statment:
            initial_amount = first_statment.airwallex_balance - first_statment.amount

        statement.write({
            "balance_start": initial_amount,
            "balance_end_real": initial_amount + statement.balance_end_real
        })

        return True

    def name_get(self):
        names = []
        for rec in self:
            names.append(
                (rec.id, f"Wallet {rec.airwallex_account_id.name} - {rec.currency_id.name}")
            )

        return names

    def toggle_active(self):
        return super(AirwallexBalance, self.sudo()).toggle_active()

    def process_items(self, items, airwallex_statement):
        """
        - Search for a bank statement with the journal on balance and that is in state open - if none found create one
        - for each item add a bank statement line - make sure to check if the line was not created already
        """
        self.ensure_one()
        bank_statement = self.env['account.bank.statement'].search(
                                [("journal_id", '=', self.journal_id.id), ('state', '=', 'open')], limit=1)
        if not bank_statement:
            today_date = fields.Date.context_today(self)
            bank_statement = self.env['account.bank.statement'].create({
                'name': _("Automatic Airwallex bank statement %s", today_date),
                'journal_id': self.journal_id.id,
                'date': today_date
            })

        prepare_items = self.env['account.bank.statement.line'].prepare_statement_values(items, bank_statement)
        existing_tokens = self.env['account.bank.statement.line'].search(
                    [('airwalex_payment_token','in', list(prepare_items.keys()))]).mapped("airwalex_payment_token")

        # Remove existing items
        for token in existing_tokens:
            del prepare_items[token]

        # Insert the new items
        bank_statement_lines = self.env['account.bank.statement.line'].create(list(prepare_items.values()))
        airwallex_statement.write({
            'bank_statement_ids': [(4, statement.id) for statement in bank_statement],
            'bank_statement_line_ids': [(4, line.id) for line in bank_statement_lines]
        })

        # Update Balance and Bank statment
        if prepare_items:
            latest_posted_date = max([item.get("airwallex_datetime") for __, item in prepare_items.items()])
            if self.last_sync_datetime:
                latest_posted_date = max(latest_posted_date, self.last_sync_datetime)
            self.write({
                'last_sync_datetime': latest_posted_date
            })
            bank_statement.write({
                'balance_end_real': bank_statement.balance_end
            })

    def button_bank_statements(self):
        self = self.sudo()
        tree_view_id = self.env.ref('account.view_bank_statement_tree')
        form_view_id = self.env.ref('account.view_bank_statement_form')

        return {
            'name': _('Bank statements'),
            'view_mode': 'tree,form',
            'res_model': 'account.bank.statement',
            'views': [[tree_view_id.id, 'tree'], [form_view_id.id, 'form']],
            'type': 'ir.actions.act_window',
            'domain': [],
            'context': {
                'search_default_journal_id': self.journal_id.id,
                'search_default_draft': True
            }
        }

    def action_open_form(self):
        return {
            'name': _('Airwallex balance form'),
            'view_mode': 'form',
            'res_model': 'airwallex.balance',
            'view_id': self.env.ref('airwallex.view_airwallex_balance_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
        }
