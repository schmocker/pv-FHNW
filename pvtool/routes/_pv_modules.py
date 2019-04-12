from flask import Blueprint, render_template, abort, request, redirect, flash

from ..db import PvModule, db

from ..forms import PvModuleForm

from sqlalchemy.orm import sessionmaker

pv_modules_routes = Blueprint('pv', __name__, template_folder='templates')


@pv_modules_routes.route('/pv_modules')
def pv_modules():
    modules = PvModule.query.all()
    # print(modules[0].ff_f)
    return render_template('pv/pv_modules.html', modules=modules)


@pv_modules_routes.route('/pv_module')
def pv_module():
    try:
        pv_id = request.args.get('id', type=int)
        if pv_id is None:
            raise Exception(f'no valid id for pv module')
        module = PvModule.query.get(pv_id)
        if module is None:
            raise Exception(f'no pv module with id {pv_id} exists')
        return render_template('pv/pv_module.html', module=module)
    except Exception as e:
        flash(str(e), category='danger')
        return redirect('pv_modules')


@pv_modules_routes.route('/pv_modules/add', methods=['GET', 'POST'])
def add_pv_module():
    form = PvModuleForm()
    if request.method == 'POST':
        new_pv_module = PvModule(model=form.modellnummer.data,
                                 manufacturer=form.hersteller.data,
                                 cell_type=form.zelltyp.data,
                                 additional_information=form.bemerkung.data,
                                 price_CHF=form.neupreis.data,
                                 length=form.laenge.data,
                                 width=form.breite.data,
                                 shunt_resistance=form.widerstand.data,
                                 )
        db.session.add(new_pv_module)
        db.session.commit()
        print("The awesome module: ", new_pv_module)

    return render_template('pv/add_pv_module.html', form=form)


@pv_modules_routes.route('/pv_modules/edit', methods=['GET', 'POST'])
def edit_pv_module():
    pv_id = request.args.get('id', type=int)
    form = PvModuleForm()
    if request.method == 'POST':
        module_entry = PvModule.query.filter(PvModule.id == pv_id).first()
        print("module entry", module_entry)
        form = form.process(request.method, module_entry)

    return render_template('pv/add_pv_module.html', form=form)


@pv_modules_routes.route('/pv_modules/remove')
def remove_pv_module():
    pv_id = request.args.get('id', type=int)

    if pv_id is not None:
        db.session.query(PvModule).filter(PvModule.id == pv_id).delete()
        db.session.commit()

    return redirect('/pv_modules')

