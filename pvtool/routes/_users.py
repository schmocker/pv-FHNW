from flask import Blueprint, flash, render_template, redirect, url_for, request, abort, send_file

from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
from ..db import db
from ._main import is_safe_url
from flask_bcrypt import Bcrypt
from ..forms import RegisterForm, GenerateUser, LoginForm

from random import randint
from io import BytesIO
import xlsxwriter

login_manager = LoginManager()
bcrypt = Bcrypt()

users_routes = Blueprint('users', __name__, template_folder='templates')


class User(UserMixin,db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name =  db.Column(db.String, unique=True, nullable=False)
    _password = db.Column(db.String(128), nullable=False)
    year = db.Column(db.String)
    student1 = db.Column(db.String)
    student2 = db.Column(db.String)
    student3 = db.Column(db.String)
    submission_date = db.Column(db.String, default='nicht eingereicht')

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    def generate_password(self, year):
        password = 'pvtool'
        password += str(randint(1, 10e6))
        password += '_' + year
        return password

    def store_password(self, year):
        self._password = self.generate_password(year)

    def generate_username(self, group_number):
        self.user_name = 'pv-FHNW_FS' + self.year + '_' + str(group_number)

    def __init__(self, year, student1, student2, student3):
        self.year = year
        self.student1 = student1
        self.student2 = student2
        self.student3 = student3
        self.store_password(year)

    def _repr__(self):
        return '<User {0}'.format(self.user_name)


@users_routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = User(form.user_name.data, form.password.data)
                db.session.add(new_user)
                db.session.commit()
                flash('Vielen Dank für die Registrierung!', category='success')
                return redirect(url_for('main.home'))
            except IntegrityError:
                db.session.rollback()
                flash('Der Benutzername <{}> wird bereits verwendet.'.format(form.user_name.data), 'danger')
    return render_template('main/register.html', form=form)


@users_routes.route('/signin', methods=['GET', 'POST'])
def signin():
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
                return redirect(url_for('main.signin'))
    return render_template('/main/signin.html', form=form)


@users_routes.route('/signout')
def signout():
    logout_user()

    flash('Erfolgreich abgemeldet', category='success')
    return redirect(url_for('main.home'))


@users_routes.route('/generate_users', methods=['GET', 'POST'])
def generate_users():
    """send xlsx file with valid users"""

    form = GenerateUser(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            print('hello')
            template_name = 'login_pvtool_' + form.jahr.data + '.xlsx'
            # create output
            output = BytesIO()

            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Logins')
            bold = workbook.add_format({'bold': True})

            worksheet.write(0, 0, 'Benutzername', bold)
            worksheet.write(0, 1, 'Passwort', bold)
            row = 1
            col = 0
            for i in range(1, form.anzahl_benutzer.data + 1):
                user = 'pv-FHNW' + form.jahr.data + '_' + str(i)
                password = generate_password(form.jahr.data)

                worksheet.write(row, col, user)
                worksheet.write(row, col + 1, password)

                row += 1
            workbook.close()
            output.seek(0)

            return send_file(output, attachment_filename=template_name, as_attachment=True)
            print('over')
            return redirect(url_for('users.users'))

    return render_template('users/generate_users.html', form=form)


@users_routes.route('/generate_user', methods=['GET', 'POST'])
def generate_user():
    """send xlsx file with valid users"""

    form = GenerateUser(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(form.jahr.data, form.student1.data,
                            form.student2.data, form.student3.data)
            number_of_users = len(User.query.all())
            new_user.generate_username(number_of_users + 1)
            print(new_user.id)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('users.users'))

    return render_template('users/generate_users.html', form=form)


@users_routes.route('/users')
def users():
    users = User.query.all()
    return render_template('users/users.html', users=users)


@users_routes.route('/user')
def user():
    """detailed view for specific user"""
    try:
        user_id = request.args.get('id', type=int)
        if user_id is None:
            raise Exception(f'no valid id for user')
        user = User.query.get(user_id)
        if user is None:
            raise Exception(f'no user with id {user_id} exists')
        return render_template('users/user.html', user=user)
    except Exception as e:
        flash(str(e), category='danger')
        return redirect(url_for('users.users'))


@users_routes.route('/users/remove')
def remove_user():
    user_id = request.args.get('id', type=int)
    if user_id is not None:
        db.session.query(User).filter(User.id == user_id).delete()
        db.session.commit()

    return redirect(url_for('users.users'))
