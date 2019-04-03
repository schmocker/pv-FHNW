from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_navigation import Navigation
from app._config import Config
from app.db import db
from .routes import main_routes, pv_modules_routes, page_not_found, internal_server_error


def create_app(test_config=None, database_conn=None):
    config = Config()

    # create app
    app = Flask(__name__)
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
        nav.Item('Home', 'main.home', items=[
            nav.Item('Home', 'main.home'),
            nav.Item('Home', 'main.home'),
        ]),
    ])

    # routes
    app.register_blueprint(main_routes)
    app.register_blueprint(pv_modules_routes)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    return app

