import os
import pandas as pd
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from .routes._main import main_routes
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, DateField, SelectField, SubmitField, FloatField
from .db import db, Measurement, PvModule
import configparser

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'pvtool/files')
ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx'])


class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.length(min=3, max=25)])
    accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])
    submit = SubmitField('PV-Modul hinzufügen')


class PvModuleForm(RegistrationForm):
    hersteller = StringField('Modellnummer', [validators.length(min=5, max=40)])
    hersteller = StringField('Hersteller', [validators.length(min=5, max=40)])
    hersteller = StringField('Zelltype', [validators.length(min=5, max=40)])
    hersteller = StringField('Bemerkung', [validators.length(min=5, max=40)])
    hersteller = StringField('Neupreis[CHF]', [validators.length(min=5, max=40)])
    hersteller = StringField('Länge[m]', [validators.length(min=5, max=40)])
    hersteller = StringField('Breite[m]', [validators.length(min=5, max=40)])



class MeasurementForm(RegistrationForm):
    measurement_date = DateField('Measurement Date')


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

