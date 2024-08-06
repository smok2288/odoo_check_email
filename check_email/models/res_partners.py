from odoo import models, fields, api
import re
import requests
import random
import string
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    verification_token = fields.Char(string='Verification Token')
    token_expiration = fields.Datetime(string='Token Expiration')
    email_verified = fields.Boolean(string='Email Verified', default=False)

    def _generate_verification_token(self):
        """Генерирует случайный токен."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    def send_verification_email(self):
        for partner in self:
            token = self._generate_verification_token()
            expiration = datetime.now() + timedelta(hours=1)
            partner.write({
                'verification_token': token,
                'token_expiration': expiration,
            })

            verification_link = f"{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}/verify_email?token={token}"

            mail_values = {
                'subject': 'Confirm your email',
                'body_html': f"<p>To confirm your email, please go to the following link:</p><a href='{verification_link}'>Confirm email</a>",
                'email_to': partner.email,
                'email_from': self.env.user.email_formatted,
            }
            self.env['mail.mail'].create(mail_values).send()
            self.env['email.validation.log'].create({
                'partner_id': partner.id,
                'email': partner.email,
                'message': f"Verification email sent to {partner.email}",
                'verified': False,
            })

    @api.model
    def verify_email(self, token):
        partner = self.search([('verification_token', '=', token), ('token_expiration', '>=', datetime.now())])
        if partner:
            partner.write({
                'verification_token': False,
                'token_expiration': False,
            })
            return True
        return False

    def action_send_verification_email(self):
        self.ensure_one()
        if not self.email:
            raise ValidationError("Пожалуйста, укажите email для партнера.")
        self.send_verification_email()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Письмо отправлено',
                'message': 'Письмо с проверочной ссылкой было успешно отправлено.',
                'type': 'success',
                'sticky': False,
            }
        }

    def check_email(self, email):
        url = f"https://disify.com/api/email/{email}"
        response = requests.get(url)
        result = response.json()
        return result

    def write(self, vals):
        if vals.get('email') and not re.match(r"[^@]+@[^@]+\.[^@]+", vals.get('email')):
            self.message_post(
                body=f"Incorrect email entered: {vals.get('email')}",
                subject="Error validation email",
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )
        return super(ResPartner, self).write(vals)

    @api.model
    def create(self, vals):
        partners = super(ResPartner, self).create(vals)
        for partner in partners:
            email = vals.get('email')
            if email:
                result = self.check_email(email)
                if result.get('disposable'):
                    partner.message_post(
                        body=f"{email} email is disposable!",
                        subject="Email is disposable",
                        message_type='notification',
                        subtype_xmlid='mail.mt_note'
                    )
                    self.env['email.validation.log'].create({
                        'partner_id': partner.id,
                        'email': email,
                        'message': f"{email} email is disposable!",
                    })

        return partners

"""You can also use the email_validate library, which performs all checks when working with email:

from email_validate import validate_or_fail

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                try:
                    email_validate = validate_or_fail(email_address=record.email)
                except Exception as e:
                    self.env['email.validation.log'].sudo().create({
                        'partner_id': record.id,
                        'email': record.email,
                        'message': e,
                    })
                    record.message_post(
                        body=f"Validation error: {e}",
                        subject="Error validation email",
                        message_type='notification',
                        subtype_xmlid='mail.mt_note'
                    )
"""