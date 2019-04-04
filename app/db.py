from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Measurement(db.Model):
    __tablename__ = __qualname__

    id = db.Column(db.Integer, primary_key=True)
    fk_pv_module = db.Column(db.Integer, db.ForeignKey('PvModule.id'), nullable=False)
    pv_module = db.relationship('PvModule',
                                      backref=db.backref('measurements', lazy=True))

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class PvModule(db.Model):
    __tablename__ = __qualname__

    id = db.Column(db.Integer, primary_key=True, info={'label': '#'})

    model = db.Column(db.String(80), nullable=False, info={'label': 'Modell'})
    manufacturer = db.Column(db.String(120), nullable=False, info={'label': 'Hersteller'})
    cell_type = db.Column(db.String(80), nullable=False, info={'label': 'Zell-Typ'})
    additional_information = db.Column(db.String(80), nullable=False, info={'label': 'Infos'})
    price_CHF = db.Column(db.Float, nullable=False, info={'label': 'Preis', 'unit': 'CHF'})
    length = db.Column(db.Float, nullable=False, info={'label': 'Länge', 'unit': 'm'})
    width = db.Column(db.Float, nullable=False, info={'label': 'Breite', 'unit': 'm'})
    shunt_resistance_Ohm = db.Column(db.Float, nullable=False, info={'label': 'Shunt-Widerstand', 'unit': 'Ohm'})

    # manufacturer data
    manu_mpp_voltage = db.Column(db.Float, nullable=False,
                                 info={'label': 'Spannung bei MPP', 'unit': 'V', 'origin': 'Hersteller'})
    manu_mpp_current = db.Column(db.Float, nullable=False,
                                 info={'label': 'Strom bei MPP', 'unit': 'A', 'origin': 'Hersteller'})
    manu_oc_voltage = db.Column(db.Float, nullable=False,
                                info={'label': 'Leerlaufspannung', 'unit': 'V', 'origin': 'Hersteller'})
    manu_sc_current = db.Column(db.Float, nullable=False,
                                info={'label': 'Kurzschlussstrom', 'unit': 'A', 'origin': 'Hersteller'})
    manu_form_factor = db.Column(db.Float, nullable=False,
                                 info={'label': 'Form-Faktor', 'unit': '-', 'origin': 'Hersteller'})
    manu_voltage_temperature_coef_UL = db.Column(db.Float, nullable=False,
                                                 info={'label':  'Spannungs-Temperatur-Koeffizient', 'unit': '% / °C',
                                                       'origin': 'Hersteller'})
    manu_current_temperature_coef_UL = db.Column(db.Float, nullable=False,
                                                 info={'label':  'Strom-Temperatur-Koeffizient', 'unit': '% / °C',
                                                       'origin': 'Hersteller'})

    # flasher data
    flasher_radiation = db.Column(db.Float, nullable=False,
                                  info={'label': 'Einstrahlung', 'unit': 'W / m2', 'origin': 'Flasher-Messung'})
    flasher_module_temperature = db.Column(db.Float, nullable=False, info={'label':  'Modul-Temperatur',
                                                                           'unit': '°C', 'origin': 'Flasher-Messung'})
    flasher_mpp_voltage = db.Column(db.Float, nullable=False,
                                    info={'label': 'Spannung bei MPP', 'unit': 'V', 'origin': 'Flasher-Messung'})
    flasher_mpp_current = db.Column(db.Float, nullable=False,
                                    info={'label': 'Strom bei MPP', 'unit': 'A', 'origin': 'Flasher-Messung'})
    flasher_oc_voltage = db.Column(db.Float, nullable=False,
                                   info={'label': 'Leerlaufspannung', 'unit': 'V', 'origin': 'Flasher-Messung'})
    flasher_sc_current = db.Column(db.Float, nullable=False,
                                   info={'label': 'Kurzschlussstrom', 'unit': 'A', 'origin': 'Flasher-Messung'})
    flasher_form_factor = db.Column(db.Float, nullable=False,
                                    info={'label': 'Form-Faktor', 'unit': '-', 'origin': 'Flasher-Messung'})

    def __repr__(self):
        return f'PV-Modul ({self.model})'