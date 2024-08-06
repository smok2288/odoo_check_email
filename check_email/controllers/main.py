from odoo import http
from odoo.http import request
from datetime import datetime

class EmailVerificationController(http.Controller):

    @http.route('/verify_email', type='http', auth='public', website=True)
    def verify_email(self, token=None, **kwargs):
        if not token:
            return request.render('check_email.views.invalid_token_template')

        partner = request.env['res.partner'].sudo().search([('verification_token', '=', token)], limit=1)
        if not partner:
            return request.render('check_email.views.invalid_token_template')

        if datetime.now() > partner.token_expiration:
            return request.render('check_email.views.token_expired_template')

        partner.sudo().write({
            'email_verified': True,
            'verification_token': False,
            'token_expiration': False,
        })
        log = request.env['email.validation.log'].sudo().search([('partner_id', '=', partner.id)], order='date desc',
                                                                limit=1)
        if log:
            log.write({
                'message': 'Email verified successfully.',
                'verified': True,
            })

        return request.render('check_email.views.email_verified_template', {'partner': partner})