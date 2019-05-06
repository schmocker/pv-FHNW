from flask_sqlalchemy import SQLAlchemy
from flask import request, flash, render_template, redirect, url_for

import sqlalchemy
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, logout_user
from .db import db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from .routes._main import main_routes
from flask_bcrypt import Bcrypt


login_manager = LoginManager()
bcrypt = Bcrypt()


class RegisterForm(FlaskForm):
    user_name = StringField('Benutzer', validators=[DataRequired(), Length(min=4, max=40)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8, max=20)])
    password_repeat = PasswordField('Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

class LoginForm(FlaskForm):
    user_name = StringField('Benutzer', validators=[DataRequired(), Length(min=4, max=40)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=8, max=20)])
    submit = SubmitField('Anmelden')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name =  db.Column(db.String, unique=True, nullable=False)
    _password = db.Column(db.String(128), nullable=False)

    is_authenticated = False
    is_anonymous = True
    is_active = False

    def get_id(self):
        return self.id

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    def __init__(self, user_name, _password):
        self.user_name = user_name
        self._password = bcrypt.generate_password_hash(_password)

    def _repr__(self):
        return '<User {0}'.format(self.name)


@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = User(form.user_name.data, form.password.data)
                new_user.is_authenticated = True
                db.session.add(new_user)
                db.session.commit()
                flash('Vielen Dank für die Registrierung!', category='success')
                return redirect(url_for('main.home'))
            except IntegrityError:
                db.session.rollback()
                flash('Der Benutzername <{}> wird bereits verwendet.'.format(form.user_name.data), 'danger')
    return render_template('main/register.html', form=form)


@main_routes.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.user_name.data).first_or_404()
        if user.is_correct_password(form.password.data):
            login_user(user)

            # add next parameter
            flash('Erfolgreich angemeldet!', category='success')
            return redirect(url_for('main.home'))
        else:
            flash('Passwort oder Benutzername falsch!', category='danger')
            return redirect(url_for('main.signin'))
    return render_template('/main/signin.html', form=form)


@main_routes.route('/signout')
def signout():
    logout_user()

    flash('Erfolgreich abgemeldet', category='success')
    return redirect(url_for('main.home'))