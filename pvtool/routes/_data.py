from flask import Blueprint, render_template, request, send_file, jsonify
import numpy as np
import json

from ..db import Measurement, MeasurementValues, PvModule
from ..forms import PlotterForm
data_routes = Blueprint('data', __name__, template_folder='templates')


@data_routes.route('/data', methods=['GET', 'POST'])
def data():
    meas_id = request.args.get('id', type=int)
    plot_form = PlotterForm()
    plot_form.pv_modul.choices = [(measurement.id,
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
                                }
                               ]}
    return render_template('data/data.html', data=data, chart_data=chart_data, form=plot_form)


@data_routes.route('/data/template')
def template():
    data = MeasurementValues.get_xlsx_template()
    return send_file(data, attachment_filename="template.xlsx", as_attachment=True)


@data_routes.route('/_query_results')
def query_results():
    """Returns module which was queried and its u_i and u_p values for plot"""
    model = request.args.get('model', type=str)
    date = request.args.get('date', type=str)
    meas_series = request.args.get('measurement_series', type=str)
    query = {}
    if model is not None:
        query['model'] = model
    if date is not None:
        query['date'] = date
    if meas_series is not None:
        query['measurement_series'] = meas_series

    queried_measurements = Measurement.query.filter_by(**query).all()

    results = []

    for meas in queried_measurements:
        meas = meas.__dict__
        measurement_values = MeasurementValues.query.filter_by(measurement_id=meas['id']).all()

        meas['data_u_i'] = [{'x': d.U_module.magnitude, 'y': d.I_module.magnitude} for d in measurement_values]
        meas['data_u_p'] = [{'x': d.U_module.magnitude, 'y': d.P_module.magnitude} for d in measurement_values]
        meas.pop('pv_module')
        meas.pop('_sa_instance_state')
        results.append(meas)

    return jsonify(results)


@data_routes.route('/_query_data')
def query_data():
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
def query_data_u_i_u_p():
    meas_series = request.args.get('measurement_id', type=str)

    query = {}
    if meas_series is not None:
        query["measurement_id"] = meas_series

    queried_measurements = MeasurementValues.query.filter_by(**query).all()

    data_U_I = [{'x': d.U_module.magnitude, 'y': d.I_module.magnitude} for d in queried_measurements]
    data_U_P = [{'x': d.U_module.magnitude, 'y': d.P_module.magnitude} for d in queried_measurements]

    return jsonify([data_U_I, data_U_P])


@data_routes.route('/_query_modules')
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
