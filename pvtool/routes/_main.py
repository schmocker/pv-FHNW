"""Contains home domain and error handlers"""
from flask import Blueprint, render_template, flash, jsonify, request
from urllib.parse import urlparse, urljoin

main_routes = Blueprint('main', __name__, template_folder='templates')


@main_routes.route('/')
def home():
    """render main page"""
    return render_template('main/home.html')


@main_routes.errorhandler(404)
def page_not_found(e):
    """error handler for page not found"""
    flash(e.description, 'danger')
    return render_template('main/404.html'), 404


@main_routes.errorhandler(500)
def internal_server_error(e):
    """error handler for internal server error"""
    flash(e.description, 'danger')
    return render_template('main/500.html'), 500, 'hallo'


@main_routes.route('/test')
def test():
    """TODO: Remove this function"""
    return render_template('main/pv_at_fhnw.html')


def is_safe_url(target):
    """Prevents undesired redirects through next parameter"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

