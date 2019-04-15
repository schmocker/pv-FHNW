from flask import Blueprint, render_template, request, redirect, flash
from ..db import Measurement
from ..db import db, Measurement

measurement_routes = Blueprint('measurement', __name__, template_folder='templates')


@measurement_routes.route('/measurements')
def measurements():
    measurements_for_displaying = Measurement.query.all()
    return render_template('measurement/measurements.html', measurements=measurements_for_displaying)


@measurement_routes.route('/measurement')
def measurement():
    try:
        meas_id = request.args.get('id', type=int)
        if meas_id is None:
            raise Exception(f'no valid id for pv module')
        module = Measurement.query.get(meas_id)
        if module is None:
            raise Exception(f'no pv module with id {meas_id} exists')
        return render_template('measurement/measurement.html', module=module)
    except Exception as e:
        flash(str(e), category='danger')
        return redirect('measurements')


@measurement_routes.route('/measurement/remove')
def remove_measurement():
    meas_id = request.args.get('id', type=int)
    if meas_id is not None:
        db.session.query(Measurement).filter(Measurement.id == meas_id).delete()
        db.session.commit()

    return redirect('/measurements')