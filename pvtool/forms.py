from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import Form, BooleanField, StringField, validators, SelectField, SubmitField, FloatField


class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.length(min=3, max=25)])
    accept_rules = BooleanField('Ich habe dieses Formular gewissenhaft ausgefüllt.', [validators.InputRequired()])
    submit = SubmitField('PV-Modul hinzufügen')


class PvModuleForm(RegistrationForm):
    modellnummer = StringField('Modellnummer', [validators.length(min=5, max=40), validators.data_required])
    hersteller = StringField('Hersteller', [validators.length(min=5, max=40)])
    zelltyp = StringField('Zelltyp', [validators.length(min=5, max=40)])
    bemerkung = StringField('Bemerkung', [validators.length(min=5, max=40)])
    neupreis = FloatField('Neupreis[CHF]', [validators.length(min=5, max=40)])
    laenge = FloatField('Länge[m]', [validators.length(min=5, max=40)])
    breite = FloatField('Breite[m]', [validators.length(min=5, max=40)])
    widerstand = FloatField('Widerstand[Ohm]', [validators.data_required])


class MeasurementForm(RegistrationForm):
    mess_datum = StringField('Messdatum')
    mess_reihe = StringField('Messreihe')
    wetter = StringField('Wetter')
    erfasser = StringField('Erfasser')
    modellnummer = SelectField('Modellnummer')
    hersteller = SelectField('Hersteller')
    messungen = FileField(validators=[FileRequired()])



def insert_form_into_database():
    pass

