import os
import pandas as pd
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from .routes._main import main_routes
from .db import db, Measurement, PvModule
import configparser
from .forms import MeasurementForm

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'pvtool/files')
ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_routes.route('/upload', methods=['GET', 'POST'])
def upload_file():
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


@main_routes.route('/add_measurement', methods=['GET', 'POST'])
def add_measurement():
    """Ugly code"""
    form = MeasurementForm()
    modules = db.session.query(PvModule).all()

    form.hersteller.choices = []
    form.modellnummer.choices = []
    for module in modules:
        if (module.manufacturer, module.manufacturer) not in form.hersteller.choices:
            form.hersteller.choices.append((module.manufacturer, module.manufacturer))
        if (module.model, module.model) not in form.modellnummer.choices:
            form.modellnummer.choices.append((module.model, module.model))

    if request.method == 'POST':
        chosen_module = db.session.query(PvModule).filter(PvModule.model == form.modellnummer.data).first()
        new_measurement = Measurement(date=form.mess_datum.data,
                                      measurement_series=form.mess_reihe.data,
                                      weather=form.wetter.data,
                                      producer=form.erfasser.data,
                                      )
        # save file that was uploaded
        if form.validate_on_submit():
            f = form.messungen.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, filename))
        chosen_module.measurements.append(new_measurement)
        db.session.add(chosen_module)
        db.session.commit()

    return render_template('data/add_measurement.html', form=form)

def process_file(file_type='pvmodule', filename=''):
    """open the file containing data and return table as pandas dataframe"""
    path_to_file = os.path.join(UPLOAD_FOLDER, filename)
    with open(path_to_file) as f:
        dataframe = pd.read_csv(f, sep=';')
        commit_dataframe_to_database(dataframe, file_type)
    os.remove(path_to_file)


def get_columns_of_table(type_of_data):
    config = configparser.ConfigParser()
    # preserve case
    config.optionxform = lambda option: option

    filepath = os.path.join(os.getcwd(), 'pvtool/config.ini')
    try:
        config.read(filepath)
    except FileNotFoundError:
        return
    print(config.sections())
    columns = [option for option in config[type_of_data]]
    print("new columns: ",columns)
    return columns


def convert_df_columns_to_desired_type(type_of_data, df):
    config = configparser.ConfigParser()
    # preserve case
    config.optionxform = lambda option: option

    filepath = os.path.join(os.getcwd(), 'pvtool/config.ini')
    try:
        config.read(filepath)
    except FileNotFoundError:
        return
    for column in df:
        df[column] = df[column].astype(config[type_of_data][column])


def commit_measurement_values_to_database(df):
    """take data frame and write it as dictionary and insert into sql alchemy"""
    print("current columns: ", df.columns)

    # format: dict like {index -> {column -> value}}
    dictionary_for_insertion = df.to_dict(orient='index')
    print(dictionary_for_insertion)

    # "**" star operator take dictionary for values in ORM model
    for key in dictionary_for_insertion:
        print(dictionary_for_insertion[key])
        new_data = Measurement(**(dictionary_for_insertion[key]))
        db.session.add(new_data)
        db.session.commit()

def commit_dataframe_to_database(df, type_of_data="MEASUREMENT"):
    """take data frame and write it as dictionary and insert into sql alchemy"""
    print("current columns: ", df.columns)
    df.columns = get_columns_of_table(type_of_data)
    convert_df_columns_to_desired_type(type_of_data, df)

    # format: dict like {index -> {column -> value}}
    dictionary_for_insertion = df.to_dict(orient='index')
    print(dictionary_for_insertion)
    if type_of_data is 'MEASUREMENT':
        # "**" star operator take dictionary for values in ORM model
        for key in dictionary_for_insertion:
            print(dictionary_for_insertion[key])
            new_data = Measurement(**(dictionary_for_insertion[key]))
            db.session.add(new_data)
    elif type_of_data is 'PVMODULE':
        for key in dictionary_for_insertion:
            new_data = PvModule(**(dictionary_for_insertion[key]))
            db.session.add(new_data)
    else:
        raise ValueError("dataframe from excel was neither labeled measurement or pv_module")

