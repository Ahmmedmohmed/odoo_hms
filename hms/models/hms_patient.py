from odoo import api, models, fields, exceptions


class Patient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    history = fields.Html(string='History')
    cr_ratio = fields.Float(string='CR Ratio')
    email = fields.Char(string='Email', required=True)

    blood_type = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], string='Blood Type')

    pcr = fields.Boolean(string='PCR')
    image = fields.Image(string='Image')
    address = fields.Text(string='Address')
    description = fields.Text(string='Description', required=True)

    department_id = fields.Many2one('hms.department', string='Department', required=True,
                                    domain="[('is_opened', '=', True)]")
    doctor_ids = fields.Many2many('hms.doctor', string='Doctors', readonly=True)
    department_capacity = fields.Integer(related='department_id.capacity', string='Department Capacity', readonly=True)

    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious')
    ], string='Condition State', default='undetermined', tracking=True)

    log_ids = fields.One2many('hms.patient.log', 'patient_id', string='Log History')

    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = fields.Date.today()
                birthdate = fields.Date.from_string(rec.birth_date)
                rec.age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            else:
                rec.age = 0

    def _create_log(self, description):
        self.env['hms.patient.log'].create({
            'patient_id': self.id,
            'description': description,
        })

    def action_set_good(self):
        self.write({'state': 'good'})
        self._create_log('State changed to Good')

    def action_set_fair(self):
        self.write({'state': 'fair'})
        self._create_log('State changed to Fair')

    def action_set_serious(self):
        self.write({'state': 'serious'})
        self._create_log('State changed to Serious')

    def action_set_undetermined(self):
        self.write({'state': 'undetermined'})
        self._create_log('State changed to Undetermined')

    def action_add_history_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'patient.log.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_patient_id': self.id},
        }

    @api.onchange('age')
    def _onchange_age(self):
        if self.age < 50:
            self.history = False
        if self.age < 30:
            self.pcr = True
            return {
                'warning': {
                    'title': 'PCR Automatically Checked',
                    'message': 'PCR has been automatically checked because the patient age is below 30.'
                }
            }

    @api.onchange('pcr')
    def _onchange_pcr(self):
        if self.pcr:
            self.cr_ratio = None
        else:
            self.cr_ratio = False

    @api.constrains('email')
    def _check_email_unique(self):
        for record in self:
            if self.search_count([('email', '=', record.email)]) > 1:
                raise exceptions.ValidationError("Email must be unique.")


class PatientLog(models.Model):
    _name = 'hms.patient.log'
    _description = 'Patient Log History'

    patient_id = fields.Many2one('hms.patient', string='Patient', required=True)
    description = fields.Text(string='Description', required=True)
    active = fields.Boolean(default=True)

    def unlink(self):
        for record in self:
            record.active = False
        return True
