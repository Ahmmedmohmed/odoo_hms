from odoo import  models , fields


class PatientLogWizard(models.TransientModel):
    _name = 'patient.log.wizard'
    _description = 'Patient Log Wizard'

    patient_id = fields.Many2one('hms.patient', string='Patient', required=True)
    description = fields.Text(string='Description', required=True)
    history = fields.Text(string='History')

    def action_create_log(self):
        self.env['hms.patient.log'].create({
            'patient_id': self.patient_id.id,
            'description': self.description,
        })

    def action_add_history(self):

            if self.history:
                self.patient_id.write({
                    'history': (self.patient_id.history or '') + self.history
                })
            return {'type': 'ir.actions.act_window_close'}
