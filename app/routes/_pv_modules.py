from flask import Blueprint, render_template, abort, request
import numpy as np
import json

from ..database import _pv_module

pv_modules_routes = Blueprint('pv', __name__, template_folder='templates')


@pv_modules_routes.route('/pv_modules')
def pv_modules():
    return render_template('pv/pv_modules.html')
