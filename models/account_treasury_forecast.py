# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2010 - 2011 Avanzosc <http://www.avanzosc.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

import openerp.addons.decimal_precision as dp
from openerp import models, fields, api, exceptions, _
from openerp.osv import osv
import datetime


#class AccountTreasuryForecastWizardInvoice(models.Model):
class AccountTreasuryForecastWizardInvoice(osv.TransientModel):
    _name = 'account.treasury.forecast.wizard.invoice'
    _description = 'Treasury Forecast Wizard Invoice'

    invoice_id = fields.Many2one("account.invoice", string="Factura")
    date_due = fields.Date(string="Fecha pago")
    partner_id = fields.Many2one("res.partner", string="Empresa")
    total_amount = fields.Float(string="Monto total", digits_compute=dp.get_precision('Account'))
    wizard_id = fields.Many2one('account.treasury.forecast.weekwizard', 'Wizard')


class AccountTreasureForecastWeekWizard(osv.TransientModel):
#class AccountTreasureForecastWeekWizard(models.Model):
    _name = 'account.treasury.forecast.weekwizard'
    name = 'Flujo'
    start_date = fields.Date(string="Fecha inicial")
    forecast_id = fields.Many2one("account.treasury.forecast", string="Forecast")
    comentarios = fields.Char('comentarios')
    in_invoice_s1 = fields.One2many('account.treasury.forecast.wizard.invoice', 'wizard_id', 'Factura Entrante')
    in_invoice_s2 = fields.One2many('account.treasury.forecast.wizard.invoice', 'wizard_id', 'Factura Entrante')
    in_invoice_s3 = fields.One2many('account.treasury.forecast.wizard.invoice', 'wizard_id', 'Factura Entrante')
    in_invoice_s4 = fields.One2many('account.treasury.forecast.wizard.invoice', 'wizard_id', 'Factura Entrante')
    out_invoice_s1 = fields.One2many('account.treasury.forecast.wizard.invoice', 'wizard_id', 'Factura Saliente')
    out_invoice_s2 = fields.One2many('account.treasury.forecast.wizard.invoice', 'wizard_id', 'Factura Saliente')
    out_invoice_s3 = fields.One2many('account.treasury.forecast.wizard.invoice', 'wizard_id', 'Factura Saliente')
    out_invoice_s4 = fields.One2many('account.treasury.forecast.wizard.invoice', 'wizard_id', 'Factura Saliente')


    def default_get(self, cr, uid, fields, context=None):
        print('---------------------------')
        print(context)
        if context is None:
            context = {}
        res = super(AccountTreasureForecastWeekWizard, self).default_get(cr, uid, fields, context)
        if context.get('forecast_id'):
            forecast_id = context['forecast_id']
            res['forecast_id'] = forecast_id            
        res['name']  = 'Flujo de caja'
        return res


    @api.onchange('start_date') # if these fields are changed, call method
    def check_change(self):
        if self.start_date != False:
            self.name = 'Flujo de caja'
            self.do_calculate()
        # no requiere devolver nada

    @api.multi
    def do_calculate_button(self, cr, uid, fields, context=None):
        return self.do_calculate()

    @api.multi
    def do_reset_invoices(self):
        in_invoices_s1 = []
        for invoice in self.in_invoice_s1:
            in_invoices_s1.append((2, invoice.id))

        in_invoices_s2 = []
        for invoice in self.in_invoice_s2:
            in_invoices_s2.append((2, invoice.id))

        in_invoices_s3 = []
        for invoice in self.in_invoice_s3:
            in_invoices_s3.append((2, invoice.id))

        in_invoices_s4 = []
        for invoice in self.in_invoice_s4:
            in_invoices_s4.append((2, invoice.id))

        out_invoices_s1 = []
        for invoice in self.out_invoice_s1:
            out_invoices_s1.append((2, invoice.id))

        out_invoices_s2 = []
        for invoice in self.out_invoice_s2:
            out_invoices_s2.append((2, invoice.id))

        out_invoices_s3 = []
        for invoice in self.out_invoice_s3:
            out_invoices_s3.append((2, invoice.id))

        out_invoices_s4 = []
        for invoice in self.out_invoice_s4:
            out_invoices_s4.append((2, invoice.id))

        self.update({'in_invoice_s1': in_invoices_s1, 'in_invoice_s2': in_invoices_s2, 'in_invoice_s3': in_invoices_s3, 'in_invoice_s4': in_invoices_s4,
            'out_invoice_s1': out_invoices_s1, 'out_invoice_s2': out_invoices_s2, 'out_invoice_s3': out_invoices_s3, 'out_invoice_s4': out_invoices_s4})
        return True        

    @api.multi
    def do_calculate(self):
        self.name = 'Flujo de caja'
        # primero, hay que eliminar los anteriores!
        self.do_reset_invoices()

        # obtengamos el forecast
        forecast_obj = self.env['account.treasury.forecast']
        forecast = forecast_obj.browse(self.forecast_id.id)

        # preparamos las fechas
        date_1 = datetime.datetime.strptime(self.start_date, '%Y-%m-%d').date()
        date_2 = date_1 + datetime.timedelta(days=7)
        date_3 = date_2 + datetime.timedelta(days=7)
        date_4 = date_3 + datetime.timedelta(days=7)

        # procesamos las entrantes
        in_invoices_s1 = []
        in_invoices_s2 = []
        in_invoices_s3 = []
        in_invoices_s4 = []
        self.comentarios = 'Recalculando'
        for invoice in forecast.in_invoice_ids:
            values = {
                'date_due': invoice.date_due,
                'total_amount': invoice.total_amount,
                'invoice_id': invoice.invoice_id,
                'partner_id': invoice.partner_id
            }
            invoice_date_due = datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').date()
            self.comentarios = self.comentarios + '.'
            if invoice_date_due < date_2:
                in_invoices_s1 += [values]
            else:
                if invoice_date_due < date_3:
                    in_invoices_s2 += [values]
                else:
                    if invoice_date_due < date_4:
                        in_invoices_s3 += [values]
                    else:
                        in_invoices_s4 += [values]
        self.comentarios = 'Recalculado'

        # procesamos las salientes
        out_invoices_s1 = []
        out_invoices_s2 = []
        out_invoices_s3 = []
        out_invoices_s4 = []
        for invoice in forecast.out_invoice_ids:
            values = {
                'date_due': invoice.date_due,
                'total_amount': invoice.total_amount,
                'invoice_id': invoice.invoice_id,
                'partner_id': invoice.partner_id
            }
            invoice_date_due = datetime.datetime.strptime(invoice.date_due, '%Y-%m-%d').date()
            if invoice_date_due < date_2:
                out_invoices_s1 += [values]
            else:
                if invoice_date_due < date_3:
                    out_invoices_s2 += [values]
                else:
                    if invoice_date_due < date_4:
                        out_invoices_s3 += [values]
                    else:
                        out_invoices_s4 += [values]                        

        self.update({'in_invoice_s1': in_invoices_s1, 'in_invoice_s2': in_invoices_s2, 'in_invoice_s3': in_invoices_s3, 'in_invoice_s4': in_invoices_s4,
            'out_invoice_s1': out_invoices_s1, 'out_invoice_s2': out_invoices_s2, 'out_invoice_s3': out_invoices_s3, 'out_invoice_s4': out_invoices_s4})
        return True


class AccountTreasuryForecastInvoice(models.Model):
    _name = 'account.treasury.forecast.invoice'
    _description = 'Treasury Forecast Invoice'

    invoice_id = fields.Many2one("account.invoice", string="Factura")
    date_due = fields.Date(string="Fecha pago")
    partner_id = fields.Many2one("res.partner", string="Empresa")
    journal_id = fields.Many2one("account.journal", string="Diario")
    state = fields.Selection([('draft', 'Draft'), ('proforma', 'Pro-forma'),
                              ('proforma2', 'Pro-forma'), ('open', 'Opened'),
                              ('paid', 'Paid'), ('cancel', 'Canceled')],
                             string="State")
    base_amount = fields.Float(string="Monto base",
                               digits_compute=dp.get_precision('Account'))
    tax_amount = fields.Float(string="Impuestos",
                              digits_compute=dp.get_precision('Account'))
    total_amount = fields.Float(string="Monto total",
                                digits_compute=dp.get_precision('Account'))
    residual_amount = fields.Float(string="Monto residual",
                                   digits_compute=dp.get_precision('Account'))


class AccountTreasuryForecast(models.Model):
    _name = 'account.treasury.forecast'
    _description = 'Treasury Forecast'

    @api.one
    def calc_final_amount(self):
        balance = 0
        for out_invoice in self.out_invoice_ids:
            balance += out_invoice.total_amount
        for in_invoice in self.in_invoice_ids:
            balance -= in_invoice.total_amount
        for recurring_line in self.recurring_line_ids:
            balance -= recurring_line.amount
        for variable_line in self.variable_line_ids:
            balance -= variable_line.amount
        balance += self.start_amount
        self.final_amount = balance

    name = fields.Char(string="Descripción", required=True)
    template_id = fields.Many2one("account.treasury.forecast.template",
                                  string="Plantilla", required=True)
    start_date = fields.Date(string="Fecha Inicial", required=True)
    end_date = fields.Date(string="Fecha Final", required=True)
    start_amount = fields.Float(string="Monto Inicial",
                                digits_compute=dp.get_precision('Account'))
    final_amount = fields.Float(string="Monto Final",
                                compute="calc_final_amount",
                                digits_compute=dp.get_precision('Account'))
    check_draft = fields.Boolean(string="Borrador", default=1)
    check_proforma = fields.Boolean(string="Proforma", default=1)
    check_open = fields.Boolean(string="Abierto", default=1)
    out_invoice_ids = fields.Many2many(
        comodel_name="account.treasury.forecast.invoice",
        relation="account_treasury_forecast_out_invoice_rel",
        column1="treasury_id", column2="out_invoice_id",
        string="Facturas salientes")
    in_invoice_ids = fields.Many2many(
        comodel_name="account.treasury.forecast.invoice",
        relation="account_treasury_forecast_in_invoice_rel",
        column1="treasury_id", column2="in_invoice_id",
        string="Facturas entrantes")
    recurring_line_ids = fields.One2many(
        "account.treasury.forecast.line", "treasury_id",
        string="Recurring Lines", domain=[('line_type', '=', 'recurring')])
    variable_line_ids = fields.One2many(
        "account.treasury.forecast.line", "treasury_id",
        string="Variable Lines", domain=[('line_type', '=', 'variable')])

    @api.one
    @api.constrains('end_date', 'start_date')
    def check_date(self):
        if self.start_date > self.end_date:
            raise exceptions.Warning(
                _('Error!:: End date is lower than start date.'))

    @api.one
    @api.constrains('check_draft', 'check_proforma', 'check_open')
    def check_filter(self):
        if not self.check_draft and not self.check_proforma and \
                not self.check_open:
            raise exceptions.Warning(
                _('Error!:: There is no any filter checked.'))

    @api.one
    def restart(self):
        self.out_invoice_ids.unlink()
        self.in_invoice_ids.unlink()
        self.recurring_line_ids.unlink()
        self.variable_line_ids.unlink()
        return True

    @api.multi
    def button_calculate(self):
        self.restart()
        self.calculate_invoices()
        self.calculate_line()
        return True

    @api.one
    def calculate_invoices(self):
        invoice_obj = self.env['account.invoice']
        treasury_invoice_obj = self.env['account.treasury.forecast.invoice']
        new_invoice_ids = []
        in_invoice_lst = []
        out_invoice_lst = []
        state = []
        if self.check_draft:
            state.append("draft")
        if self.check_proforma:
            state.append("proforma")
        if self.check_open:
            state.append("open")
        invoice_ids = invoice_obj.search([('date_due', '>', self.start_date),
                                          ('date_due', '<', self.end_date),
                                          ('state', 'in', tuple(state))])
        for invoice_o in invoice_ids:
            values = {
                'invoice_id': invoice_o.id,
                'date_due': invoice_o.date_due,
                'partner_id': invoice_o.partner_id.id,
                'journal_id': invoice_o.journal_id.id,
                'state': invoice_o.state,
                'base_amount': invoice_o.amount_untaxed,
                'tax_amount': invoice_o.amount_tax,
                'total_amount': invoice_o.amount_total,
                'residual_amount': invoice_o.residual,
            }
            new_id = treasury_invoice_obj.create(values)
            new_invoice_ids.append(new_id)
            if invoice_o.type in ("out_invoice", "out_refund"):
                out_invoice_lst.append(new_id.id)
            elif invoice_o.type in ("in_invoice", "in_refund"):
                in_invoice_lst.append(new_id.id)
        self.write({'out_invoice_ids': [(6, 0, out_invoice_lst)],
                    'in_invoice_ids': [(6, 0, in_invoice_lst)]})
        return new_invoice_ids

    @api.one
    def calculate_line(self):
        line_obj = self.env['account.treasury.forecast.line']
        temp_line_obj = self.env['account.treasury.forecast.line.template']
        new_line_ids = []
        temp_line_lst = temp_line_obj.search([('treasury_template_id', '=',
                                               self.template_id.id)])
        for line_o in temp_line_lst:
            if ((line_o.date > self.start_date and
                    line_o.date < self.end_date) or
                    not line_o.date) and not line_o.paid:
                values = {
                    'name': line_o.name,
                    'date': line_o.date,
                    'line_type': line_o.line_type,
                    'partner_id': line_o.partner_id.id,
                    'template_line_id': line_o.id,
                    'amount': line_o.amount,
                    'treasury_id': self.id,
                }
                new_line_id = line_obj.create(values)
                new_line_ids.append(new_line_id)
        return new_line_ids


    @api.multi
    def show_week_wizard(self):
        # http://stackoverflow.com/questions/31907694/open-another-module-form-view-with-button
    
        wizard_obj = self.env['account.treasury.forecast.weekwizard']
        # primero buscaremos si ya tenemos uno
        wizard_ids = wizard_obj.search([('forecast_id', '=', self.id),])
        if len(wizard_ids) != 0:
            wizard_id = wizard_ids[0].id
            # deberíamos limpiar los datos
            wizard_ids[0].do_reset_invoices()
        else:
            values = {
                'forecast_id': self.id,
                'comentarios': 'Estos son...',
            }
            new_ids = wizard_obj.create(values)
            wizard_id = new_ids.id
        
        basura ={
            'name': ('Proyeccion'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.treasury.forecast.weekwizard',
            'res_id': wizard_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }          
        return basura   


class AccountTreasuryForecastLine(models.Model):
    _name = 'account.treasury.forecast.line'
    _description = 'Treasury Forecast Line'

    name = fields.Char(string="Description")
    line_type = fields.Selection([('recurring', 'Recurring'),
                                  ('variable', 'Variable')],
                                 string="Treasury Line Type")
    date = fields.Date(string="Date")
    partner_id = fields.Many2one("res.partner", string="Partner")
    amount = fields.Float(string="Amount",
                          digits_compute=dp.get_precision('Account'))
    template_line_id = fields.Many2one(
        "account.treasury.forecast.line.template", string="Template Line")
    treasury_id = fields.Many2one("account.treasury.forecast",
                                  string="Treasury")

