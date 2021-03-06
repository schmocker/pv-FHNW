from flask_sqlalchemy import SQLAlchemy
from flask import g, current_app
import sqlite3
import numpy as np
import pint
from pint.converters import ScaleConverter
from pint.unit import UnitDefinition
import sqlalchemy
import xlsxwriter
from io import BytesIO
from sqlalchemy.orm.attributes import QueryableAttribute

db = SQLAlchemy()

ureg = pint.UnitRegistry()
ureg.define(UnitDefinition('percent', 'pct', (), ScaleConverter(1 / 100.0)))


def get_db():
    """ probably needed to give context to cli command for creating admin user"""
    print(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if 'db' not in g:
        g.db = sqlite3.connect(
           current_app.config['SQLALCHEMY_DATABASE_URI']
        )
        g.db.row_factory = sqlite3.Row
    return g.db


class Base:
    """Base class to access values with units"""
    def get_value_with_unit(self, col_name: str):
        """returns value including pint unit"""
        try:
            return self.get_value(col_name) * self.get_column_unit(col_name)
        except Exception as e:
            raise Exception(f'could not get value with unit for column "{col_name}"\n-> {e}')

    def get_value(self, col_name: str):
        """get the value of the column only, i.e. the data as it is stored"""
        try:
            return getattr(self, col_name)
        except AttributeError as e:
            raise AttributeError(f'database table class "{self.__class__}" has no column attribute "{col_name}"')

    @classmethod
    def get_column_unit(cls, col_name: str):
        """Return the unit of the column in which data is stored"""
        info = cls.get_column_info(col_name)
        try:
            unit = info['unit']
            unit = unit.replace('%', 'pct')
            unit = unit.replace('°C', 'degC')
            unit = unit.replace('-', '1')
            unit = unit.replace('Ohm', 'ohm')
            return ureg.Unit(unit)
        except KeyError as e:
            if not hasattr(cls, col_name):
                KeyError(f'class "{cls}" has not attribute "{col_name}"')
            raise KeyError(f'unit for db column "{col_name}" is not defined')
        except pint.errors.UndefinedUnitError:
            raise pint.errors.UndefinedUnitError(f'could not convert')

    @classmethod
    def get_column_info(cls, col_name):
        """return the info part of the column"""
        col = cls.get_column(col_name)
        try:
            return col.info
        except KeyError as e:
            raise KeyError(f'database column "{col}" has no attribute "info"')

    @classmethod
    def get_column(cls, col_name):
        """returns the called column"""
        try:
            col = getattr(cls, col_name)
            if type(col) is not sqlalchemy.orm.attributes.InstrumentedAttribute:
                raise TypeError(f'attribute "{col_name}" of database table class "{cls}" is not a column')
            return col
        except KeyError as e:
            KeyError(f'database table class "{cls}" has not attribute "{col_name}" as a column')

    @classmethod
    def get_column_names(cls):
        """returns column names of the corresponding table as a list"""
        return [i for i in cls.__dict__.keys() if
                type(getattr(cls, i)) is sqlalchemy.orm.attributes.InstrumentedAttribute]


class Measurement(db.Model, Base):
    """Stores a single measurement
        date:                   the date when the measurement was taken
        measurement_series:     name of the measurement as given by course
        weather:                description of the current weather as string
        producer:               Students who took the measurements

        pv_module_id:           many-to-one relationship to PvModule
        measurement_values:     one-to-may relationship to MeasurementValues
    """
    __tablename__ = 'measurement'

    id = db.Column(db.Integer, primary_key=True, info={'label': '#'})

    # TODO: confusion with different names measurement_series and measurement_values
    date = db.Column(db.String, nullable=False, info={'label': 'Datum', 'format': 'YY-MM-DD'})
    measurement_series = db.Column(db.String(80), nullable=False, info={'label': 'Messreihe'})
    producer = db.Column(db.String(80), nullable=False, info={'label': 'Erfasser'})

    pv_module_id = db.Column(db.Integer, db.ForeignKey('pv_module.id'), nullable=False)

    measurement_values = db.relationship('MeasurementValues', backref='measurement')


class MeasurementValues(db.Model, Base):
    """Values of one measureement, many-to-one relationship to Measurement"""
    __tablename__ = 'measurement_values'

    id = db.Column(db.Integer, primary_key=True)

    weather = db.Column('Wetter', db.String(80), nullable=True, info={'label': 'Wetter'})

    _U_module = db.Column('U_module[V]', db.Float, nullable=False,
                          info={'label': 'Spannung des Modules', 'unit': 'V'})
    _U_shunt = db.Column('U_shunt[V]', db.Float, nullable=False,
                         info={'label': 'Spannung über Shunt-Widerstand', 'unit': 'V'})
    _U_T_amb = db.Column('U_T_amb[V]', db.Float, nullable=False,
                         info={'label': 'Spannung des Temperatursensors für die Umgebungstemperatur', 'unit': 'V'})
    _U_T_pan = db.Column('U_T_pan[V]', db.Float, nullable=False,
                         info={'label': 'Spannung des Temperatursensors für die Modultemperatur', 'unit': 'V'})
    _U_G_hor = db.Column('U_G_hor[V]', db.Float, nullable=False,
                         info={'label': 'Spannung des Pyranometers für die horizontale Strahlung', 'unit': 'V'})
    _U_G_pan = db.Column('U_G_pan[V]', db.Float, nullable=False,
                         info={'label': 'Spannung des Pyranometers für die Strahlung mit Modulneigung', 'unit': 'V'})
    _U_G_ref = db.Column('U_G_ref[V]', db.Float, nullable=False,
                         info={'label': 'Spannung der Referenzzelle', 'unit': 'V'})

    measurement_id = db.Column(db.Integer, db.ForeignKey('measurement.id'), nullable=False)

    @classmethod
    def get_xlsx_template(cls):
        print('hello')
        columns = [cls.weather, cls._U_module, cls._U_shunt, cls._U_T_amb, cls._U_G_hor,   cls._U_G_pan, cls._U_G_ref,
                   cls._U_T_pan]

        output = BytesIO()
        book = xlsxwriter.Workbook(output)
        bold = book.add_format({'bold': True})

        sheet_data = book.add_worksheet('data')
        for i, cn in enumerate(columns):
            print(cn.name)
            sheet_data.write(0, i, cn.name, bold)
            for j in range(10):
                sheet_data.write(j + 1, i, 0)
            sheet_data.set_column(i, i, 15)

        sheet_info = book.add_worksheet('info')
        sheet_info.write(0, 0, 'Spalte', bold)
        sheet_info.write(0, 1, 'Beschreibung', bold)
        sheet_info.write(0, 2, 'Einheit', bold)
        for i, cn in enumerate(columns):
            sheet_info.write(i + 1, 0, cn.name)
            sheet_info.write(i + 1, 1, cn.info['label'])
        sheet_info.set_column(0, 0, 15)
        sheet_info.set_column(1, 1, 60)
        sheet_info.set_column(2, 2, 8)

        book.close()
        output.seek(0)
        return output

    @property
    def Wetter(self):
        return self.weather

    @property
    def U_module(self):
        return self.get_value_with_unit('_U_module')

    @property
    def U_shunt(self):
        return self.get_value_with_unit('_U_shunt')

    @property
    def T_amb(self):
        return self._U_T_amb * 100

    @property
    def T_pan(self):
        return self._U_T_pan * 100

    @property
    def G_hor(self):
        return (self._U_G_hor - 2) * 200

    @property
    def G_pan(self):
        return (self._U_G_pan - 2) * 200

    @property
    def G_ref(self):
        return self._U_G_ref * 130

    @property
    def I_module(self):
        return ((self._U_shunt * ureg.V) / self.measurement.pv_module.R_shunt).to(ureg.A)

    @property
    def U_module_stc(self):
        return self.U_2_U_stc(U_messured=self.U_module,
                              G_pan=self.G_pan, G_stc=1000,
                              T_pan=self.T_pan, T_stc=25,
                              a_U_oc=self.measurement.pv_module.manufacturer_data.a_U_oc)

    @property
    def I_module_stc(self):
        return self.I_2_I_stc(I_messured=self.I_module,
                              G_pan=self.G_pan, G_stc=1000,
                              T_pan=self.T_pan, T_stc=25,
                              a_I_sc=self.measurement.pv_module.manufacturer_data.a_I_sc)

    @property
    def P_module(self):
        return self.U_module * self.I_module

    @property
    def P_module_stc(self):
        return self.U_module_stc * self.I_module_stc

    @staticmethod
    def U_2_U_stc(U_messured, G_pan, G_stc, T_pan, T_stc, a_U_oc):
        return U_messured / (np.log(G_pan) / np.log(G_stc) * (1 + a_U_oc * (T_pan - T_stc)*ureg.K))

    @staticmethod
    def I_2_I_stc(I_messured, G_pan, G_stc, T_pan, T_stc, a_I_sc):
        return I_messured / (G_pan / G_stc * (1 + a_I_sc * (T_pan - T_stc)*ureg.K))


class PvModule(db.Model, Base):
    """PV Module used for measurement
        model:                  modelnumber of the cell, does not have to be an int
        manufacturer:           name of the manufacturer
        cell_type:              specifies type of cell(e.g. organic)

        manufacturer_data:      one-to-one relationship, STC values of manufacturer
        flasher_data:           one-to-one relationship as obtained by Flasher measurement

        measurement:            one-to-many relationship to measurements made with the PV module
    """
    __tablename__ = 'pv_module'

    id = db.Column(db.Integer, primary_key=True, info={'label': '#'})

    model = db.Column(db.String(80), info={'label': 'Modell'})
    manufacturer = db.Column(db.String(120), info={'label': 'Hersteller'})
    cell_type = db.Column(db.String(80), info={'label': 'Zell-Typ'})
    additional_information = db.Column(db.String(80), info={'label': 'Infos'})
    price_CHF = db.Column(db.Float, info={'label': 'Preis', 'unit': 'CHF'})
    length = db.Column(db.Float, info={'label': 'Länge', 'unit': 'm'})
    width = db.Column(db.Float, info={'label': 'Breite', 'unit': 'm'})
    shunt_resistance = db.Column(db.Float, info={'label': 'Shunt-Widerstand', 'unit': 'Ohm'})

    manufacturer_data = db.relationship('ManufacturerData', uselist=False, backref='pv_module', lazy=True)
    flasher_data = db.relationship('FlasherData', uselist=False, backref='pv_module', lazy=True)

    measurements = db.relationship('Measurement', backref='pv_module', lazy=True)

    @property
    def R_shunt(self):
        return self.get_value_with_unit('shunt_resistance')

    # def __repr__(self):
    #     return "<Modell:'%s':'%s'> " % self.manufacturer, self.model


class ManufacturerData(db.Model, Base):
    """STC as measured by manufacturer"""
    __tablename__ = 'manufacturer_data'

    # manufacturer data
    id = db.Column(db.Integer, primary_key=True)

    _U_mpp_m = db.Column(db.Float, info={'label': 'Spannung bei MPP', 'unit': 'V', 'origin': 'Hersteller'})
    _I_mpp_m = db.Column(db.Float, info={'label': 'Strom bei MPP', 'unit': 'A', 'origin': 'Hersteller'})
    _U_oc_m = db.Column(db.Float, info={'label': 'Leerlaufspannung', 'unit': 'V', 'origin': 'Hersteller'})
    _I_sc_m = db.Column(db.Float, info={'label': 'Kurzschlussstrom', 'unit': 'A', 'origin': 'Hersteller'})
    _ff_m = db.Column(db.Float, info={'label': 'Form-Faktor', 'unit': '-', 'origin': 'Hersteller'})
    _a_U_oc = db.Column(db.Float, info={'label': 'Spannungs-Temperatur-Koeffizient', 'unit': '% / K', 'origin': 'Hersteller'})
    _a_I_sc = db.Column(db.Float, info={'label': 'Strom-Temperatur-Koeffizient', 'unit': '% / K', 'origin': 'Hersteller'})

    pv_module_id = db.Column(db.Integer, db.ForeignKey('pv_module.id'))

    @property
    def U_mpp_m(self):
        return self.get_value_with_unit('_U_mpp_m')

    @property
    def I_mpp_m(self):
        return self.get_value_with_unit('_I_mpp_m')

    @property
    def U_oc_m(self):
        return self.get_value_with_unit('_U_oc_m')

    @property
    def I_sc_m(self):
        return self.get_value_with_unit('_I_sc_m')

    @property
    def ff_m(self):
        return self.get_value_with_unit('_ff_m')

    @property
    def a_I_sc(self):
        return self.get_value_with_unit('_a_I_sc')

    @property
    def a_U_oc(self):
        return self.get_value_with_unit('_a_U_oc')

    @staticmethod
    def U_2_U_stc(U_messured, G_pan, G_stc, T_pan, T_stc, a_U_oc):
        return U_messured * (np.log(G_stc) / (np.log(G_pan) * (1 + a_U_oc * (T_pan - T_stc))))

    @staticmethod
    def I_2_I_stc(I_messured, G_pan, G_stc, T_pan, T_stc, a_I_sc):
        return I_messured * (G_stc / (G_pan * (1 + a_I_sc * (T_pan - T_stc))))

    def get_stc_values(self, stc_temp, stc_rad):
        stc_temp = float(stc_temp)
        stc_rad = float(stc_rad)
        return {
            '_U_mpp_m' : self.U_2_U_stc(self._U_mpp_m*ureg.V, stc_rad,
                                        1000, stc_temp*ureg.kelvin, 25*ureg.kelvin, self.a_U_oc).magnitude,
            '_I_mpp_m' : self.I_2_I_stc(self._I_mpp_m*ureg.A, stc_rad,
                                        1000, stc_temp*ureg.kelvin, 25*ureg.kelvin, self.a_I_sc).magnitude,
            '_U_oc_m' : self.U_2_U_stc(self._U_oc_m*ureg.V, stc_rad,
                                       1000, stc_temp*ureg.kelvin, 25*ureg.kelvin, self.a_U_oc).magnitude,
            '_I_sc_m' : self.I_2_I_stc(self._I_sc_m*ureg.A, stc_rad,
                                       1000, stc_temp*ureg.kelvin, 25*ureg.kelvin, self.a_I_sc).magnitude,
            '_a_U_oc' : self.U_2_U_stc(self._a_U_oc, stc_rad,
                                       1000, stc_temp*ureg.kelvin, 25*ureg.kelvin, self.a_U_oc).magnitude,
            '_a_I_sc' : self.U_2_U_stc(self._a_I_sc, stc_rad,
                                       1000, stc_temp*ureg.kelvin, 25*ureg.kelvin, self.a_I_sc).magnitude,
        }


class FlasherData(db.Model, Base):
    """data for PvModule from flasher measurement"""
    __tablename__ = 'flasher_data'

    # flasher data
    id = db.Column(db.Integer, primary_key=True)

    _G_f = db.Column(db.Float, info={'label': 'Einstrahlung', 'unit': 'W / m2', 'origin': 'Flasher-Messung'})
    _T_module_f = db.Column(db.Float, info={'label': 'Modul-Temperatur', 'unit': '°C', 'origin': 'Flasher-Messung'})
    _U_mpp_f = db.Column(db.Float, info={'label': 'Spannung bei MPP', 'unit': 'V', 'origin': 'Flasher-Messung'})
    _I_mpp_f = db.Column(db.Float, info={'label': 'Strom bei MPP', 'unit': 'A', 'origin': 'Flasher-Messung'})
    _U_oc_f = db.Column(db.Float, info={'label': 'Leerlaufspannung', 'unit': 'V', 'origin': 'Flasher-Messung'})
    _I_sc_f = db.Column(db.Float, info={'label': 'Kurzschlussstrom', 'unit': 'A', 'origin': 'Flasher-Messung'})
    _ff_f = db.Column(db.Float, info={'label': 'Form-Faktor', 'unit': '-', 'origin': 'Flasher-Messung'})

    pv_module_id = db.Column(db.Integer, db.ForeignKey('pv_module.id'))

    @property
    def G_f(self):
        return self.get_value_with_unit('_G_f')

    @property
    def T_module_f(self):
        return self.get_value_with_unit('_T_module_f')

    @property
    def U_mpp_f(self):
        return self.get_value_with_unit('_U_mpp_f')

    @property
    def I_mpp_f(self):
        return self.get_value_with_unit('_I_mpp_f')

    @property
    def U_oc_f(self):
        return self.get_value_with_unit('_U_oc_f')

    @property
    def I_sc_f(self):
        return self.get_value_with_unit('_I_sc_f')

    @property
    def ff_f(self):
        return self.get_value_with_unit('_ff_f')

