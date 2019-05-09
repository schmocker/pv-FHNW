from flask import Flask
from flask_navigation import Navigation
from flask_bcrypt import Bcrypt
from pvtool._config import Config, TestingConfig
from pvtool.db import db, PvModule
from .routes import main_routes, pv_modules_routes, measurement_routes, page_not_found, internal_server_error, \
    data_routes, users_routes
from .routes._users import login_manager, bcrypt, User


def create_app(config):
    # create pvtool
    app = Flask('pvtool')

    # TODO: Update this if other configs are needed
    app.config.from_object(config)
    # database
    db.init_app(app)
    # create db
    @app.before_first_request
    def create_db():
        db.create_all()

    login_manager.init_app(app)
    login_manager.login_view = 'main.signin'
    login_manager.login_message = 'Bitte melden Sie sich an um diese Seite zu sehen.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(userid):
        return User.query.filter(User.id == userid).first()

    bcrypt.init_app(app)

    # navigation
    nav = Navigation(app)
    nav.Bar('top', [
        nav.Item('Home', 'main.home'),
        nav.Item('PV-Module', 'pv.pv_modules'),
        nav.Item('Messungen', 'measurement.measurements'),
        nav.Item('Data', 'data.data'),
        nav.Item('Benutzer', 'users.users')
        # nav.Item('Home', 'main.home', items=[
        #     nav.Item('Home', 'main.home'),
        #     nav.Item('Home', 'main.home'),
        # ]),
    ])

    # routes
    app.register_blueprint(main_routes)
    app.register_blueprint(pv_modules_routes)
    app.register_blueprint(measurement_routes)
    app.register_blueprint(data_routes)
    app.register_blueprint(users_routes)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    return app
