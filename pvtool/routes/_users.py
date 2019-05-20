"""Implements login function and links users to measurement"""
from flask import Blueprint, flash, render_template, redirect, url_for, request, abort, send_file, current_app, g
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
from ..db import db, get_db, Measurement
from ._main import is_safe_url
from flask_bcrypt import Bcrypt
from ..forms import RegisterForm, GenerateUser, LoginForm

from random import randint
from io import BytesIO
import xlsxwriter
import click
import datetime

login_manager = LoginManager()
bcrypt = Bcrypt()

users_routes = Blueprint('users', __name__, template_folder='templates')


class User(UserMixin,db.Model):
    """User class for flask-login and distributing passwords and usernames
    to students"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name =  db.Column(db.String, unique=True, nullable=False)
    _password = db.Column(db.String(128), nullable=False)
    year = db.Column(db.String)
    student1 = db.Column(db.String)
    student2 = db.Column(db.String)
    student3 = db.Column(db.String)
    submission_date = db.Column(db.String, default='nicht eingereicht')
    rights = db.Column(db.String, default='student')

    def is_correct_password(self, plaintext):
        return self._password == plaintext

    def generate_password(self, year):
        password = 'pvtool'
        password += str(randint(1, 10e6))
        password += '_' + str(year)
        return password

    def store_password(self, year):
        self._password = self.generate_password(year)

    def generate_username(self, group_number):
        self.user_name = 'pv-FHNW_FS' + str(self.year) + '_' + str(group_number)

    def __init__(self, year, student1, student2, student3):
        self.year = year
        self.student1 = student1
        self.student2 = student2
        self.student3 = student3
        self.store_password(year)

    def _repr__(self):
        return '<User {0}'.format(self.user_name)


@users_routes.route('/signin', methods=['GET', 'POST'])
def signin():
    """Render a login form and sign in the user"""
    if current_user.is_authenticated:
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('main.home'))

    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(user_name=form.user_name.data).first_or_404()
            if user.is_correct_password(form.password.data):
                login_user(user)

                flash('Erfolgreich angemeldet!', category='success')
                next = request.args.get('next')
                if not is_safe_url(next):
                    return abort(400)
                return redirect(next or url_for('main.home'))
            else:
                flash('Passwort oder Benutzername falsch!', category='danger')
                return redirect(url_for('users.signin'))
    return render_template('/users/signin.html', form=form)


@users_routes.route('/signout')
def signout():
    """Signout the current user."""
    logout_user()

    flash('Erfolgreich abgemeldet', category='success')
    return redirect(url_for('main.home'))


@users_routes.route('/export_users')
def export_users():
    """send xlsx file with valid users
    TODO: has troubles with updating template in same session, if db is changed and xlsx file is exported in same session
    xlsx file might not change"""
    template_name = 'login_pvtool.xlsx'
    # create output
    print('heeeeeello')
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Logins')
    bold = workbook.add_format({'bold': True})

    worksheet.write(0, 0, 'Benutzername', bold)
    worksheet.write(0, 1, 'Passwort', bold)
    worksheet.write(0, 2, '1.Student', bold)
    worksheet.write(0, 3, '2.Student', bold)
    worksheet.write(0, 4, '3.Student', bold)
    row = 1
    col = 0
    users = db.session.query(User).all()

    for user in users:

        worksheet.write(row, col, user.user_name)
        worksheet.write(row, col + 1, user._password)
        worksheet.write(row, col + 2, user.student1)
        worksheet.write(row, col + 3, user.student2)
        worksheet.write(row, col + 4, user.student3)

        row += 1
    workbook.close()
    output.seek(0)

    return send_file(output, attachment_filename=template_name, as_attachment=True)


@users_routes.route('/generate_user')
def generate_user():

    form = GenerateUser(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(form.jahr.data, form.student1.data,
                            form.student2.data, form.student3.data)
            number_of_users_in_current_year = len(User.query.filter(User.year == form.jahr.data).all())
            new_user.generate_username(number_of_users_in_current_year + 1)
            print(new_user.id)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('users.users'))

    return render_template('users/generate_users.html', form=form)


@users_routes.route('/users')
def users():
    """Overview as table of all registered users"""
    users = User.query.all()
    return render_template('users/users.html', users=users)


@users_routes.route('/user')
def user():
    """Detailed view for specific user"""
    try:
        user_id = request.args.get('id', type=int)
        if user_id is None:
            raise Exception(f'no valid id for user')
        user = User.query.get(user_id)
        measurement = Measurement.query.filter(Measurement.measurement_series == user.user_name).first()
        if user is None:
            raise Exception(f'no user with id {user_id} exists')
        return render_template('users/user.html', user=user, measurement=measurement)
    except Exception as e:
        flash(str(e), category='danger')
        return redirect(url_for('users.users'))


@users_routes.route('/users/remove')
def remove_user():
    """Remove user without cascading deletion of inserted measurements"""
    user_id = request.args.get('id', type=int)
    if user_id is not None:
        db.session.query(User).filter(User.id == user_id).delete()
        db.session.commit()

    return redirect(url_for('users.users'))


def add_timestamp():
    """Adds a timestamp to the logged in user when measurement is uploaded"""
    user = db.session.query(User).filter(User.id == current_user.id).first()
    user.submission_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    db.session.add(user)
    db.session.commit()
