import os
import pandas as pd
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
from .routes._main import main_routes

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app/files')
ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx'])

from wtforms import Form, BooleanField, StringField, PasswordField, validators, DateField, SelectField

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
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('main/upload.html')



