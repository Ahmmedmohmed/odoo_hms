from odoo import models, fields

class Doctor(models.Model):
    _name = 'hms.doctor'
    _description = 'Doctor'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    image = fields.Binary(string='Doctor Image')
    department_id = fields.Many2one('hms.department', string='Department')
    patient_ids = fields.Many2many('hms.patient', string='Patients')
