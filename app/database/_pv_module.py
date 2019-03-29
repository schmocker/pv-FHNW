from ..app import db


class PvModule(db.Model):
    __tablename__ = __qualname__

    id = db.Column(db.Integer, primary_key=True)

    model = db.Column(db.String(80), nullable=False)
    manufacturer = db.Column(db.String(120), nullable=False)
    cell_type = db.Column(db.String(80), nullable=False)
    additional_information = db.Column(db.String(80), nullable=False)
    price_CHF = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False) # [m]
    width = db.Column(db.Float, nullable=False) # [m]
    shunt_resistance_Ohm = db.Column(db.Float, nullable=False) # [Ohm]

    # manufacturer data
    manu_mpp_voltage = db.Column(db.Float, nullable=False) # [V]
    manu_mpp_current = db.Column(db.Float, nullable=False) # [A]
    manu_oc_voltage = db.Column(db.Float, nullable=False) # [V]
    manu_sc_current = db.Column(db.Float, nullable=False) # [A]
    manu_form_factor = db.Column(db.Float, nullable=False) # [-]
    manu_voltage_temperature_coef_UL = db.Column(db.Float, nullable=False) # [ % /°C]
    manu_current_temperature_coef_UL = db.Column(db.Float, nullable=False) # [ % /°C]

    # flasher data
    flasher_radiation = db.Column(db.Float, nullable=False) # [W / m2]
    flasher_module_temperature = db.Column(db.Float, nullable=False) # [°C]

    flasher_mpp_voltage = db.Column(db.Float, nullable=False) # [V]
    flasher_mpp_current = db.Column(db.Float, nullable=False) # [A]
    flasher_oc_voltage = db.Column(db.Float, nullable=False) # [V]
    flasher_sc_current = db.Column(db.Float, nullable=False) # [A]
    flasher_form_factor = db.Column(db.Float, nullable=False) # [-]

    def __repr__(self):
        return f'PV-Modul ({self.model})'
