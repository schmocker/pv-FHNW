import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, abort, request, redirect, flash

from ..db import PvModule, FlasherData, ManufacturerData, db

from ..forms import PvModuleForm, FlasherDataForm, ManufacturerDataForm
from ..file_upload import process_pv_module_file, UPLOAD_FOLDER

pv_modules_routes = Blueprint('pv', __name__, template_folder='templates')


@pv_modules_routes.route('/pv_modules')
def pv_modules():
    """show all modules in table"""
    modules = PvModule.query.all()
    # print(modules[0].ff_f)
    return render_template('pv/pv_modules.html', modules=modules)


@pv_modules_routes.route('/pv_module')
def pv_module():
    """detailed view for specific module"""
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
        return redirect('/pv_modules')

    return render_template('pv/add_pv_module.html', form=form)


@pv_modules_routes.route('/pv_modules/add_data', methods=['GET', 'POST'])
def add_pv_module_data():
    form_flasher = FlasherDataForm()
    form_manufacturer = ManufacturerDataForm()

    pv_id = request.args.get('id', type=int)

    if request.method == 'POST':
        new_flasher_data = FlasherData(_U_mpp_f=form_flasher.u_mpp_fl.data,
                                       _I_mpp_f=form_flasher.i_mpp_fl.data,
                                       _U_oc_f=form_flasher.u_ll_fl.data,
                                       _I_sc_f=form_flasher.i_ks_fl.data,
                                       _ff_f=form_flasher.ff_fl.data,
                                       _G_f=form_flasher.einstrahlung_fl.data,
                                       _T_module_f=form_flasher.modultemperatur_fl.data)
        new_manufacturer_data = ManufacturerData(_U_mpp_m=form_manufacturer.u_mpp_m.data,
                                                 _I_mpp_m=form_manufacturer.i_mpp_m.data,
                                                 _U_oc_m=form_manufacturer.u_ll_m.data,
                                                 _I_sc_m=form_manufacturer.i_ks_m.data,
                                                 _ff_m=form_manufacturer.ff_m.data,
                                                 _a_U_oc=form_manufacturer.u_temp_koeff_m.data,
                                                 _a_I_sc=form_manufacturer.i_temp_koeff_m.data)

        current_module = db.session.query(PvModule).filter(PvModule.id == pv_id).first()

        current_module.flasher_data = new_flasher_data
        current_module.manufacturer_data = new_manufacturer_data

        db.session.add(current_module)
        db.session.commit()

    return render_template('pv/add_data.html', form_fl=form_flasher, form_m=form_manufacturer)


@pv_modules_routes.route('/pv_modules/add_multiple_modules', methods=['GET','POST'])
def add_multiple_pv_modules():
    """Upload csv with complete values"""
    form = PvModuleForm()
    if request.method == 'POST':
        f = form.pv_modul_file.data

        filename = secure_filename(f.filename)
        path_to_file = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path_to_file)
        process_pv_module_file(filename)
    return render_template('pv/add_multiple_pv_modules.html', form=form)


@pv_modules_routes.route('/pv_modules/edit', methods=['GET', 'POST'])
def edit_pv_module():
    pv_id = request.args.get('id', type=int)
    form = PvModuleForm()
    if request.method == 'POST':
        module_entry = db.session.query(PvModule).filter(PvModule.id == pv_id).first()
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

