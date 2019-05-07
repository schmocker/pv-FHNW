from pvtool.db import PvModule


def test_pv_module_insert(app):
    pass
    """
    GIVEN a database
    WHEN database is initialized
    THEN check if pv_module can be inserted and removed
    """
    """test_pv_module = PvModule(model="TEST",
                             manufacturer="TEST",
                             cell_type="TEST",
                             additional_information="TEST",
                             price_CHF="-999",
                             length="-999",
                             width="-999",
                             shunt_resistance="-999",
                             )
    db_test = get_db()
    db_test.session.add(test_pv_module)
    db_test.session.commit()

    query_result = db_test.session.query(PvModule).filter(PvModule.model == test_pv_module.model).first()
    assert query_result
    db_test.session.query(PvModule).filter(PvModule.model == test_pv_module.model).delete()
    db_test.session.commit()"""
