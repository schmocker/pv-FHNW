from flask import Blueprint, render_template, abort, request, redirect, flash

from ..db import PvModule

from ..file_upload import PvModuleForm

pv_modules_routes = Blueprint('pv', __name__, template_folder='templates')


@pv_modules_routes.route('/pv_modules')
def pv_modules():
    modules = PvModule.query.all()
    print(modules[0].ff_f)
    return render_template('pv/pv_modules.html', modules=modules)


@pv_modules_routes.route('/pv_module')
def pv_module():
    try:
        id = request.args.get('id', type=int)
        if id is None:
            raise Exception(f'no valid id for pv module')
        module = PvModule.query.get(id)
        if module is None:
            raise Exception(f'no pv module with id {id} exists')
        return render_template('pv/pv_module.html', module=module)
    except Exception as e:
        flash(str(e), category='danger')
        return redirect('pv_modules')


@pv_modules_routes.route('/pv_modules/add', methods=['GET', 'POST'])
def add_pv_module():
    form = PvModuleForm()
    return render_template('pv/add_pv_module.html', form=form)


@pv_modules_routes.route('/pv_modules/edit')
def edit_pv_module():
    id = request.args.get('id', type=int)
    # todo: edit-form (evt. combine edit and add form if possible)


@pv_modules_routes.route('/pv_modules/remove')
def remove_pv_module():
    id = request.args.get('id', type=int)
    # todo: remove request
