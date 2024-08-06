from odoo import models, fields

class EmailValidationLog(models.Model):
    _name = 'email.validation.log'
    _description = 'Email Validation Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    email = fields.Char(string='Email', required=True, tracking=True)
    message = fields.Char(string='Validation Message', tracking=True)
    validation_date = fields.Datetime(string='Validation Date', default=fields.Datetime.now, required=True, tracking=True)
    verified = fields.Boolean(string='Verified', default=False)
