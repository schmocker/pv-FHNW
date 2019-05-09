from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, StringField, validators, SelectField, SubmitField, FloatField, IntegerField,\
    PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


class BaseForm(FlaskForm):
    username = StringField('Username', [validators.length(min=3, max=25)])
    accept_rules = BooleanField('Ich habe dieses Formular gewissenhaft ausgefüllt.', [validators.InputRequired()])
    submit = SubmitField('PV-Modul hinzufügen')


class RegisterForm(FlaskForm):
    user_name = StringField('Benutzer', validators=[DataRequired(), Length(min=4, max=40)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8, max=20)])
    password_repeat = PasswordField('Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')


class LoginForm(FlaskForm):
    user_name = StringField('Benutzer', validators=[DataRequired(), Length(min=4, max=40)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField('Anmelden')


class GenerateUser(FlaskForm):
    jahr = StringField('Jahr')
    anzahl_benutzer = IntegerField('Anzahl Benutzer')
    student1 = StringField('1.Student')
    student2 = StringField('2.Student')
    student3 = StringField('3.Student')
    submit = SubmitField('Benutzer generieren')


class PvModuleForm(BaseForm):
    modellnummer = StringField('Modellnummer', [validators.length(min=5, max=40), validators.data_required])
    hersteller = StringField('Hersteller', [validators.length(min=5, max=40)])
    zelltyp = StringField('Zelltyp', [validators.length(min=5, max=40)])
    bemerkung = StringField('Bemerkung', [validators.length(min=5, max=40)])
    neupreis = FloatField('Neupreis[CHF]', [validators.length(min=5, max=40)])
    laenge = FloatField('Länge[m]', [validators.length(min=5, max=40)])
    breite = FloatField('Breite[m]', [validators.length(min=5, max=40)])
    widerstand = FloatField('Widerstand[Ohm]', [validators.data_required])
    pv_modul_file = FileField('PV Module')


class ManufacturerDataForm(BaseForm):
    u_mpp_m = FloatField('Spannung MPP [V]')
    i_mpp_m = FloatField('Strom MPP [A]')
    u_ll_m = FloatField('Leerlaufspannung [V]')
    i_ks_m = FloatField('Kurzschlussstrom [A]')
    ff_m = FloatField('Formfaktor')
    u_temp_koeff_m = FloatField('Spannungstemperaturkoeffizient [%/°C]')
    i_temp_koeff_m = FloatField('Stromtemperaturkoeffizient [%/°C]')


class FlasherDataForm(BaseForm):
    einstrahlung_fl = FloatField('Einstrahlung[W/m^2]')
    modultemperatur_fl = FloatField('Modultemperatur[°C]')
    u_mpp_fl = FloatField('Spannung MPP [V]')
    i_mpp_fl = FloatField('Strom MPP [A]')
    u_ll_fl = FloatField('Leerlaufspannung [V]')
    i_ks_fl = FloatField('Kurzschlussstrom [A]')
    ff_fl = FloatField('Formfaktor')


class MeasurementForm(BaseForm):
    mess_datum = StringField('Messdatum')
    mess_reihe = StringField('Messreihe')
    wetter = StringField('Wetter')
    erfasser = StringField('Erfasser')
    pv_modul = SelectField('PV Modul')
    messungen = FileField(validators=[FileRequired()])


class PlotterForm(BaseForm):
    pv_modul = SelectField('PV Modul')
    datum = SelectField('Datum')
    mess_reihe = SelectField('Messreihe')
    stc_temperatur = FloatField('STC-Temperatur[°C]')
    stc_einstrahlung = FloatField('STC-Einstrahlung[W/m^2]')
