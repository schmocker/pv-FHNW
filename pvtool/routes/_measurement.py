"""Overview of all Measurements and linked functions such as uploading removing and single view of measurement"""
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, flash, g, current_app, url_for
from flask_login import current_user, login_required
from ..db import db, Measurement, PvModule, MeasurementValues
from ..forms import MeasurementForm
from ..file_upload import UPLOAD_FOLDER, allowed_file, process_data_file, InvalidFileType,\
    process_multiple_measurements_file
from ._users import add_timestamp, requires_access_level

measurement_routes = Blueprint('measurement', __name__, template_folder='templates')


@measurement_routes.route('/measurements')
def measurements():
    """Display all measurements as table with clickable individual measurements"""
    measurements_for_displaying = db.session.query(Measurement).all()
    return render_template('measurement/measurements.html', measurements=measurements_for_displaying)


@measurement_routes.route('/measurement')
def measurement():
    """Display a single measurement with link to removal, plot and returning to all measurements"""
    try:
        meas_id = request.args.get('id', type=int)
        if meas_id is None:
            raise Exception(f'no valid id for pv module')
        meas = db.session.query(Measurement).get(meas_id)
        meas_values = db.session.query(MeasurementValues).filter(MeasurementValues.measurement_id == meas_id).all()
        print(meas_values)
        if meas is None:
            raise Exception(f'no measurement with id {meas_id} exists')
        return render_template('measurement/measurement.html', measurement=meas, measurement_values=meas_values)
    except Exception as e:
        flash(str(e), category='danger')
        return redirect('measurements')


@measurement_routes.route('/measurement/remove')
@requires_access_level('Admin')
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
@login_required
def add_measurement():
    """Form to add measurement with populated pvmodules field"""
    form = MeasurementForm()
    modules = db.session.query(PvModule).all()

    current_user_data = current_user.__dict__

    user = {'students': current_user_data['student1'] + ', ' +
                        current_user_data['student2'] + ', ' +
                        current_user_data['student3'],
            'meas_series': current_user_data['user_name']}

    form.pv_modul.choices = []

    # Every user can only insert one measurement
    if db.session.query(Measurement).filter(Measurement.measurement_series == user['meas_series']).first() is not None:
        print(db.session.query(Measurement).filter(Measurement.measurement_series == user['meas_series']).first())
        flash('Sie haben bereits eine Messung hinzugefügt.', category='danger')
        return redirect(url_for('measurement.measurements'))

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
        try:
            process_data_file(filename, new_measurement)
        except InvalidFileType:
            flash('Messung hochladen fehlgeschlagen!', category='danger')
            return redirect(url_for('measurement.measurements'))
        db.session.add(chosen_module)
        db.session.commit()

        add_timestamp()
        flash('Messung erfolgreich hinzugefügt.', category='success')
        return redirect(url_for('measurement.measurements'))

    # flash current user
    flash('Angemeldet als:', )
    flash(current_user_data['user_name'], category='primary')

    return render_template('measurement/add_measurement.html', form=form, user=user)


@measurement_routes.route('/add_measurements', methods=['GET', 'POST'])
@requires_access_level('Admin')
def add_measurements():
    """Form to add measurement from excel, multiple measurements possible"""
    form = MeasurementForm()

    if request.method == 'POST':
        f = form.messungen.data

        filename = secure_filename(f.filename)
        path_to_file = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path_to_file)
        process_multiple_measurements_file(filename)
        return redirect(url_for('measurement.measurements'))

    return render_template('measurement/add_measurements.html', form=form)
