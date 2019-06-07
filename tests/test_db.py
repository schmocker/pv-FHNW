import pytest
from pvtool.db import PvModule, Measurement, MeasurementValues, FlasherData, ManufacturerData, db


@pytest.mark.incremental
class TestDBModels(object):
    def test_pv_module_insert(client, init_db):
        """
            GIVEN a database
            WHEN database is initialized
            THEN check if pv_module can be inserted and removed
        """
        test_pv_module = PvModule(model="TEST",
                                 manufacturer="TEST",
                                 cell_type="TEST",
                                 additional_information="TEST",
                                 price_CHF="-999",
                                 length="-999",
                                 width="-999",
                                 shunt_resistance="-999",
                                 )
        db.session.add(test_pv_module)
        db.session.commit()

        query_result = db.session.query(PvModule).filter(PvModule.model == test_pv_module.model).first()
        assert query_result
        db.session.query(PvModule).filter(PvModule.model == test_pv_module.model).delete()
        db.session.commit()

    def test_measurement_insert(client, init_db):
        """
            GIVEN a database
            WHEN database is initialized
            THEN check if pv_module can be inserted and removed
        """
        test_measurement = Measurement(date='TEST',
                                       measurement_series='TEST',
                                       producer='TEST',
                                       pv_module_id=1,
                                        )

        db.session.add(test_measurement)
        db.session.commit()

        query_result = db.session.query(Measurement).filter(Measurement.measurement_series == test_measurement.measurement_series).first()
        assert query_result
        db.session.query(Measurement).filter(Measurement.measurement_series == test_measurement.measurement_series).delete()
        db.session.commit()

    def test_measurement_values_insert(client, init_db):
        """
            GIVEN a database
            WHEN database is initialized
            THEN check if measurement_values can be inserted and removed
        """
        test_measurement_values = MeasurementValues(weather='TEST',
                                                    _U_module=0,
                                                    _U_shunt=0,
                                                    _U_T_amb=0,
                                                    _U_T_pan=0,
                                                    _U_G_hor=0,
                                                    _U_G_pan=0,
                                                    _U_G_ref=0,
                                                    measurement_id=1,
                                                    )

        db.session.add(test_measurement_values)
        db.session.commit()

        query_result = db.session.query(MeasurementValues).\
            filter(MeasurementValues.weather == test_measurement_values.weather).first()
        assert query_result
        db.session.query(MeasurementValues).filter(MeasurementValues.weather == test_measurement_values.weather).delete()
        db.session.commit()


def insert_multiple_pv_modules(client, init_db):
    pass
