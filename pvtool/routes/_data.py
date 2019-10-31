"""Visualization of different measurements and API to return measurements as JSON"""
from flask import Blueprint, render_template, request, send_file, jsonify
from flask_login import login_required
from ._users import requires_access_level
from ..db import Measurement, MeasurementValues, PvModule, FlasherData, ManufacturerData
from ..forms import PlotterForm
data_routes = Blueprint('data', __name__, template_folder='templates')


@data_routes.route('/data', methods=['GET', 'POST'])
@requires_access_level('Admin')
def data():
    """Plot the functions U-I and U-P with buttons to query different measurements"""
    meas_id = request.args.get('id', type=int)
    plot_form = PlotterForm()
    plot_form.pv_modul.choices = [(measurement.pv_module_id,
                                   str(measurement.pv_module.manufacturer) + ' ' + str(measurement.pv_module.model))
                                  for measurement in
                                  Measurement.query.distinct(Measurement.pv_module_id)
                                  .group_by(Measurement.pv_module_id)]
    # chosen_module = Measurement.query.filter(Measurement.pv_module_id==plot_form.pv_modul.data[0]).first().pv_module
    plot_form.datum.choices = [(measurement.id,
                                measurement.date)
                               for measurement in
                               Measurement.query.distinct(Measurement.date)
                               .group_by(Measurement.date)]

    plot_form.mess_reihe.choices = [(measurement.id,
                                     measurement.measurement_series)
                                    for measurement in
                                    Measurement.query.distinct(Measurement.measurement_series)
                                    .group_by(Measurement.measurement_series)]

    data = MeasurementValues.query.filter(MeasurementValues.measurement_id == meas_id)

    if meas_id:
        pv_module = str(Measurement.query.filter(Measurement.id == meas_id).first().pv_module.manufacturer) + ' ' + Measurement.query.filter(Measurement.id == meas_id).first().pv_module.model
        date = Measurement.query.filter(Measurement.id == meas_id).first().date
        measurement_series = Measurement.query.filter(Measurement.id == meas_id).first().measurement_series
    else:
        pv_module = ' '
        date = ' '
        measurement_series = ' '
    # legacy
    data_U_I = [{'x': d.U_module.magnitude, 'y': d.I_module.magnitude} for d in data]
    data_U_P = [{'x': d.U_module.magnitude, 'y': d.P_module.magnitude} for d in data]
    chart_data = {'datasets': [{'label':   'U',
                                'xAxisID': 'ax_U',
                                'yAxisID': 'ax_I',
                                'data':    data_U_I,
                                },
                               {'type': 'line',
                                'label':   'P',
                                'xAxisID': 'ax_U',
                                'yAxisID': 'ax_P',
                                'data':    data_U_P
                                },
                               ],
                  'pv_module': pv_module,
                  'date': date,
                  'measurement_series': measurement_series}
    return render_template('data/data.html', data=data, chart_data=chart_data, form=plot_form)


@data_routes.route('/data/template')
@requires_access_level('Admin')
def template():
    """Send template to user were measurement_values are to be inserted."""
    print("heeeeelllo")
    data = MeasurementValues.get_xlsx_template()
    return send_file(data, attachment_filename="template.xlsx", as_attachment=True)


@data_routes.route('/_query_results')
@requires_access_level('Admin')
def query_results():
    """Returns module which was queried and its u_i and u_p values for plot and flasher, manufacturer
    data of corresponding module"""

    model_id = request.args.get('pv_module_id', type=str)
    date = request.args.get('date', type=str)
    meas_series = request.args.get('measurement_series', type=str)
    stc_temp = request.args.get('stc_temp', type=str)
    stc_rad = request.args.get('stc_rad', type=str)

    query = {}

    if model_id:
        query['pv_module_id'] = model_id
    if date:
        query['date'] = date
    if meas_series:
        query['measurement_series'] = meas_series

    meas = Measurement.query.filter_by(**query).first()

    if meas:
        meas = meas.__dict__
        measurement_values = MeasurementValues.query.filter_by(measurement_id=meas['id']).all()

        flasher_data = FlasherData.query.filter_by(pv_module_id=meas['pv_module_id']).first()
        manufacturer_data = ManufacturerData.query.filter_by(pv_module_id=meas['pv_module_id']).first()

        if stc_temp and stc_rad:
            meas['manufacturer_data'] = manufacturer_data.get_stc_values(stc_rad, stc_temp)
            manufacturer_data = manufacturer_data.__dict__
            manufacturer_data.pop("_sa_instance_state")
            meas['manufacturer_data']['_ff_m'] = manufacturer_data['_ff_m']
            meas['manufacturer_data']['id'] = manufacturer_data['id']
            meas['manufacturer_data']['pv_module_id'] = manufacturer_data['pv_module_id']
        else:
            manufacturer_data = manufacturer_data.__dict__
            manufacturer_data.pop("_sa_instance_state")
            meas['manufacturer_data'] = manufacturer_data

        flasher_data = flasher_data.__dict__
        flasher_data.pop("_sa_instance_state")
        meas['flasher_data'] = flasher_data
        meas['flasher_data_stc'] = {}

        meas['data_u_i'] = [{'x': d.U_module.magnitude, 'y': d.I_module.magnitude} for d in measurement_values]
        meas['data_u_p'] = [{'x': d.U_module.magnitude, 'y': d.P_module.magnitude} for d in measurement_values]

        meas['data_u_i_stc'] = [{'x': d.U_module_stc.magnitude, 'y': d.I_module_stc.magnitude} for d in measurement_values]
        meas['data_u_p_stc'] = [{'x': d.U_module_stc.magnitude, 'y': d.P_module_stc.magnitude} for d in measurement_values]

        meas.pop('_sa_instance_state')

        return jsonify(meas)
    else:
        return jsonify([])


@data_routes.route('/_query_data')
@requires_access_level('Admin')
def query_data():
    """API function which returns a measurement as queried by id"""
    meas_series = request.args.get('measurement_id', type=str)

    query = {}
    if meas_series is not None:
        query['measurement_id'] = meas_series

    queried_measurements = MeasurementValues.query.filter_by(**query).all()

    results = []
    for meas in queried_measurements:
        meas = meas.__dict__
        meas.pop('_sa_instance_state')
        results.append(meas)

    return jsonify(results)


@data_routes.route('/_query_data_u_i_u_p')
@requires_access_level('Admin')
def query_data_u_i_u_p():
    """get a measurement by id and return its U-I data and U-P data"""
    meas_series = request.args.get('measurement_id', type=str)

    query = {}
    if meas_series is not None:
        query["measurement_id"] = meas_series

    queried_measurements = MeasurementValues.query.filter_by(**query).all()

    data_U_I = [{'x': d.U_module.magnitude, 'y': d.I_module.magnitude} for d in queried_measurements]
    data_U_P = [{'x': d.U_module.magnitude, 'y': d.P_module.magnitude} for d in queried_measurements]

    return jsonify([data_U_I, data_U_P])


@data_routes.route('/_query_modules')
@requires_access_level('Admin')
def query_modules():
    """Query database with model and manufacturer to receive JSON with corresponding modules
       Syntax: ROOT_DOMAIN/_query_modules?model=modelname&manufacturer=manufacturer_name
    """
    model = request.args.get('model', type=str)
    manufacturer = request.args.get('manufacturer', type=str)
    query = {}

    if model is not None:
        query["model"] = model
    if manufacturer is not None:
        query["manufacturer"] = manufacturer

    chosen_module = PvModule.query.filter_by(**query).all()

    results = []
    for meas in chosen_module:
        meas = meas.__dict__
        meas.pop("_sa_instance_state")
        results.append(meas)

    return jsonify(results)


@data_routes.route('/_query_module_data')
@requires_access_level('Admin')
def query_module_data():
    """Query db with module_id to obtain corresponding flasher and manufacturer data
    """
    module_id = request.args.get('pv_module_id', type=str)
    query = {}

    if module_id is not None:
        query["id"] = module_id

    flasher_data = FlasherData.query.filter_by(**query).first()
    manufacturer_data = ManufacturerData.query.filter_by(**query).first()

    flasher_data = flasher_data.__dict__
    flasher_data.pop("_sa_instance_state")

    manufacturer_data = manufacturer_data.__dict__
    manufacturer_data.pop("_sa_instance_state")

    result = {'flasher_data': flasher_data,
              'manufacturer_data': manufacturer_data
              }
    return jsonify(result)


@data_routes.route('/_query_available_measurements')
@requires_access_level('Admin')
def query_available_measurements():
    """Query db with module_id to obtain corresponding flasher and manufacturer data
    """
    module_id = request.args.get('pv_module_id', type=str)
    query = {}

    if module_id is not None:
        query["id"] = module_id

    flasher_data = FlasherData.query.filter_by(**query).first()
    manufacturer_data = ManufacturerData.query.filter_by(**query).first()

    flasher_data = flasher_data.__dict__
    flasher_data.pop("_sa_instance_state")

    manufacturer_data = manufacturer_data.__dict__
    manufacturer_data.pop("_sa_instance_state")

    result = {'flasher_data': flasher_data,
              'manufacturer_data': manufacturer_data
              }
    return jsonify(result)