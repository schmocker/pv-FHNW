from flask import Blueprint, render_template, abort, request, redirect, flash, send_file
import numpy as np
import json

from ..db import Measurement

data_routes = Blueprint('data', __name__, template_folder='templates')


@data_routes.route('/data')
def data():
    data = Measurement.query.all()

    data_U_I = [{'x': d.U_module.magnitude, 'y': d.I_module.magnitude} for d in data]
    data_U_P = [{'x': d.U_module.magnitude, 'y': d.P_module.magnitude} for d in data]
    chart_data = {'datasets': [{'label':   'U',
                                'xAxisID': 'ax_U',
                                'yAxisID': 'ax_I',
                                'data':    data_U_I},
                               {'label':   'P',
                                'xAxisID': 'ax_U',
                                'yAxisID': 'ax_P',
                                'data':    data_U_P}
                               ]}
    return render_template('data/data.html', data=data, chart_data=chart_data)


@data_routes.route('/data/template')
def template():
    data = Measurement.get_xlsx_template()
    return send_file(data, attachment_filename="template.xlsx", as_attachment=True)
