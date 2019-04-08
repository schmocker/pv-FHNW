import os
import pandas as pd
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from .routes._main import main_routes
from wtforms import Form, BooleanField, StringField, PasswordField, validators, DateField, SelectField
from .db import db, Measurement, PvModule

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app/files')
ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx'])



class RegistrationForm(Form):
    date = DateField('Username')
    language = SelectField('PV-Modul', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])

    confirm = PasswordField('Upload')


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
            process_file('measurement', filename)
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))
    return render_template('main/upload.html')


def process_file(file_type='pvmodule', filename=''):
    """open the file containing data and return table as pandas dataframe"""
    path_to_file = os.path.join(UPLOAD_FOLDER, filename)
    with open(path_to_file) as f:
        dataframe = pd.read_csv(f)
        commit_dataframe_to_database(dataframe, file_type)
    os.remove(path_to_file)


def commit_dataframe_to_database(df, type_of_data):
    """take data frame and write it as dictionary and insert into sql alchemy"""
    dictionary_for_insertion = df.to_dict(orient='list')
    if type_of_data is 'measurement':
        # "**" star operator take dictionary for values in ORM model
        new_data = Measurement(**dictionary_for_insertion)
    elif type_of_data is 'pvmodule':
        new_data = PvModule(**dictionary_for_insertion)
    else:
        raise ValueError("dataframe from excel was neither labeled measurement or pv_module")
    db.session.add(new_data)

