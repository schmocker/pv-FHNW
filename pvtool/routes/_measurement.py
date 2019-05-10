"""Overview of all Measurements and linked functions such as uploading removing and single view of measurement"""
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, flash, g, current_app
from flask_login import current_user
from ..db import db, Measurement, PvModule
from ..forms import MeasurementForm
from ..file_upload import UPLOAD_FOLDER, allowed_file, process_data_file

measurement_routes = Blueprint('measurement', __name__, template_folder='templates')


@measurement_routes.route('/measurements')
def measurements():
    """Display all measurements as table with clickable individual measurements"""
    measurements_for_displaying = Measurement.query.all()
    return render_template('measurement/measurements.html', measurements=measurements_for_displaying)


@measurement_routes.route('/measurement')
def measurement():
    """Display a single measurement with link to removal, plot and returning to all measurements"""
    try:
        meas_id = request.args.get('id', type=int)
        if meas_id is None:
            raise Exception(f'no valid id for pv module')
        meas = Measurement.query.get(meas_id)
        if meas is None:
            raise Exception(f'no measurement with id {meas_id} exists')
        return render_template('measurement/measurement.html', measurement=meas)
    except Exception as e:
        flash(str(e), category='danger')
        return redirect('measurements')


@measurement_routes.route('/measurement/remove')
def remove_measurement():
    """Remove the individual measurement and its corresponding measurement values, does not affect the user"""
    meas_id = request.args.get('id', type=int)
    if meas_id is not None:
        db.session.query(Measurement).filter(Measurement.id == meas_id).delete()
        db.session.commit()

    return redirect('/measurements')


@measurement_routes.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Legacy function
    TODO: REMOVE
    """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            flash('file chosen')
            process_file('MEASUREMENT', filename)
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
    return render_template('main/upload.html')


@measurement_routes.route('/add_measurement', methods=['GET', 'POST'])
def add_measurement():
    """Form to add measurement with populated pvmodules field"""
    form = MeasurementForm()
    modules = db.session.query(PvModule).all()
    flash('Logged in as:', )
    flash(current_user.__dict__['user_name'], category='primary')

    current_user_data = current_user.__dict__

    user = {}
    user['students'] = current_user_data['student1'] + ', ' +\
                       current_user_data['student2'] + ', ' +\
                       current_user_data['student3']
    user['meas_series'] = current_user_data['user_name']

    form.pv_modul.choices = []

    # populate select field with available distinct modules
    for module in modules:
        if (module.model, str(module.manufacturer) + ' ' + str(module.model)) not in form.pv_modul.choices:
            form.pv_modul.choices.append((module.model, str(module.manufacturer) + ' ' + str(module.model)))

    if request.method == 'POST':
        chosen_module = db.session.query(PvModule).filter(PvModule.model == form.pv_modul.data).first()
        # noinspection PyArgumentList
        new_measurement = Measurement(date=form.mess_datum.data,
                                      measurement_series=user['meas_series'],
                                      producer=user['students'],
                                      )
        # save file that was uploaded
        # if form.validate_on_submit():
        f = form.messungen.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(UPLOAD_FOLDER, filename))

        chosen_module.measurements.append(new_measurement)
        process_data_file(filename, new_measurement)
        db.session.add(chosen_module)
        db.session.commit()

    return render_template('measurement/add_measurement.html', form=form, user=user)
