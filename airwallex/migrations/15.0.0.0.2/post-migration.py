import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Update cron value")
    env.ref('airwallex.account_ir_cron').write({
        'code': "model.action_get_list_transactions(fetchall=True)"
    })