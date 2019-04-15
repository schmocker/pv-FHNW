from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_navigation import Navigation
from pvtool._config import Config, TestingConfig
from pvtool.db import db, PvModule
from .routes import main_routes, pv_modules_routes, page_not_found, internal_server_error, data_routes
from .file_upload import upload_file


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

    # navigation
    nav = Navigation(app)
    nav.Bar('top', [
        nav.Item('Home', 'main.home'),
        nav.Item('PV-Modules', 'pv.pv_modules'),
        nav.Item('Data', 'data.data'),
        nav.Item('Upload', 'main.upload_file'),
        nav.Item('Home', 'main.home', items=[
            nav.Item('Home', 'main.home'),
            nav.Item('Home', 'main.home'),
        ]),
    ])

    # routes
    app.register_blueprint(main_routes)
    app.register_blueprint(pv_modules_routes)
    app.register_blueprint(data_routes)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    return app