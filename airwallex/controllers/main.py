import logging
import pprint
from werkzeug.utils import redirect

from odoo import http
from odoo.http import Controller, request
_logger = logging.getLogger(__name__)

OAUTH2_CALLBACK_ROUTE = '/callback/token/airwallex'


class AirwallexAuthentication(Controller):

    @http.route([OAUTH2_CALLBACK_ROUTE], type='http', auth='public', csrf=False)
    def log_request(self, **post):
        _logger.info(
            "Airwallex: logging request: %s",
            pprint.pformat(post)
        )  # debug

        if post.get('state'):
            account = request.env['airwallex.account'].sudo().search([('oauth2_state', '=', post['state'])])
            if account:
                account.generate_oauth2_token(post)
                return redirect(f'/web#id={account.id}&model=airwallex.account&view_type=form')

        return redirect('/web')
