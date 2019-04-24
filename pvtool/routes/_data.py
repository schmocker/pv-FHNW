from flask import Blueprint, render_template, abort, request, redirect, flash, send_file
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
    print("IMPORTANT",plot_form.pv_modul.data)
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

    data = MeasurementValues.query.filter(MeasurementValues.measurement_id==meas_id)

    data_U_I = [{'x': d.U_module.magnitude, 'y': d.I_module.magnitude} for d in data]
    data_U_P = [{'x': d.U_module.magnitude, 'y': d.P_module.magnitude} for d in data]
    chart_data = {'datasets': [{'label':   'U',
                                'xAxisID': 'ax_U',
                                'yAxisID': 'ax_I',
                                'data':    data_U_I,
                                'borderColor':  '[rgba(8,8,251,1)]'},
                               {'type': 'line',
                                'label':   'P',
                                'xAxisID': 'ax_U',
                                'yAxisID': 'ax_P',
                                'data':    data_U_P,
                                'borderColor': '[rgba(255,99,132,0.2)]'}
                               ]}
    return render_template('data/data.html', data=data, chart_data=chart_data, form=plot_form)


@data_routes.route('/data/template')
def template():
    data = MeasurementValues.get_xlsx_template()
    return send_file(data, attachment_filename="template.xlsx", as_attachment=True)
