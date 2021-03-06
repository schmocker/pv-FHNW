import os
import pandas as pd
from .db import db, Measurement, PvModule, FlasherData, ManufacturerData, MeasurementValues
import configparser
from flask import flash
from .routes._main import internal_server_error

UPLOAD_FOLDER = os.path.join('/var/www/pv-FHNW/', 'pvtool/files')
ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx'])


class InvalidFileType(Exception):
    pass


class InvalidTemplate(Exception):
    pass


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_invalid_file_type(path_to_file):
    flash('Ungültiges Dateiformat', category='danger')
    os.remove(path_to_file)
    #raise InvalidFileType('Invalid file type was inserted')


def process_data_file(filename, linked_measurement):
    """open the file containing data and pass table as pandas dataframe with measurement to be linked"""
    path_to_file = os.path.join(UPLOAD_FOLDER, filename)
    if not allowed_file(filename):
        handle_invalid_file_type(path_to_file)
        raise InvalidFileType
    try:
        with open(path_to_file) as f:
            if filename.endswith('.csv'):
                dataframe = pd.read_csv(f, sep=';', encoding='utf-8')
            elif filename.endswith(('.xls', '.xlsx')):
                dataframe = pd.read_excel(path_to_file)
            commit_measurement_values_to_database(dataframe, linked_measurement)
        os.remove(path_to_file)
    except InvalidTemplate:
        flash('Hochgeladene Messwerte sind ungültig.', category='danger')
        handle_invalid_file_type(path_to_file)
    except FileNotFoundError:
        flash('Hochladen der Messung fehlgeschlagen.', category='danger')


def process_pv_module_file(filename):
    """open the file containing pvmodule and pass table as pandas dataframe with pvmodules to be linked"""
    path_to_file = os.path.join(UPLOAD_FOLDER, filename)
    if not allowed_file(filename):
        handle_invalid_file_type(path_to_file)
    try:
        with open(path_to_file) as f:
            if filename.endswith('.csv'):
                dataframe = pd.read_csv(f, sep=';', encoding='utf-8')
            elif filename.endswith(('.xls', '.xlsx')):
                dataframe = pd.read_excel(path_to_file)
        commit_pvmodule_to_database(dataframe)
        os.remove(path_to_file)
    except InvalidTemplate:
        flash('Hochgeladene Messwerte sind ungültig.', category='danger')
        handle_invalid_file_type(path_to_file)
    except FileNotFoundError:
        flash('Hochladen der Messung fehlgeschlagen.', category='danger')


def process_multiple_measurements_file(filename):
    path_to_file = os.path.join(UPLOAD_FOLDER, filename)
    if not allowed_file(filename):
        handle_invalid_file_type(path_to_file)
    try:
        with open(path_to_file) as f:
            if filename.endswith('.csv'):
                dataframe = pd.read_csv(f, sep=';', encoding='utf-8')
            elif filename.endswith(('.xls', '.xlsx')):
                dataframe = pd.read_excel(path_to_file)
        commit_measurement_files_to_database(dataframe)
        os.remove(path_to_file)
    except InvalidTemplate:
        flash('Hochgeladene Messwerte sind ungültig.', category='danger')
        handle_invalid_file_type(path_to_file)
    except FileNotFoundError:
        flash('Hochladen der Messung fehlgeschlagen.', category='dangeer')


def get_columns_of_table(type_of_data):
    """gets columns for dataframe from configfile"""
    config = configparser.ConfigParser()
    # preserve case
    config.optionxform = lambda option: option

    filepath = os.path.join(os.getcwd(), 'pvtool/config.ini')
    try:
        config.read(filepath)
    except FileNotFoundError:
        return
    columns = [option for option in config[type_of_data]]
    return columns


def convert_df_columns_to_desired_type(type_of_data, df):
    config = configparser.ConfigParser()
    # preserve case
    config.optionxform = lambda option: option

    filepath = os.path.join(os.getcwd(), 'pvtool/config.ini')
    try:
        config.read(filepath)
    except FileNotFoundError:
        return
    for column in df:
        df[column] = df[column].astype(config[type_of_data][column])


def commit_measurement_values_to_database(df, linked_measurement):
    """take data frame and write it as dictionary and insert into sql alchemy"""
    new_columns = get_columns_of_table('MEASUREMENT')
    if len(df.columns) != len(new_columns):
        raise InvalidTemplate()
        return
    df.columns = new_columns
    convert_df_columns_to_desired_type("MEASUREMENT", df)

    # format: dict like {index -> {column -> value}}
    dictionary_for_insertion = df.to_dict(orient='index')

    try:
        # "**" star operator take dictionary for values in ORM model
        for key in dictionary_for_insertion:
            new_measurement_values = MeasurementValues(**(dictionary_for_insertion[key]))
            linked_measurement.measurement_values.append(new_measurement_values)
            db.session.add(linked_measurement)
        db.session.commit()
    except:
        flash('Failed commit_measurement_to_database', category='danger')


def commit_measurement_files_to_database(df):
    """process dataframe from file with multiple measurements"""
    measurements = {}
    columns_for_values = ['Wetter', 'U [V]', 'U_Shunt [V]', 'U_T_amb [V]', 'U_G_hor [V]', 'U_G_pan [V]', 'U_G_ref [V]', 'U_T_pan [V]']
    columns_for_measurement = ['PV_Modul', 'Datum', 'Messreihe', 'Erfasser']

    # ugly code for quick fix, sorry!
    for column in columns_for_measurement:
        df[column] = df[column].astype(str)
    df['Wetter'] = df['Wetter'].astype(str)

    # create individual dataframes out of all measurements in dataframe
    for name, group in df.groupby(columns_for_measurement):
        measurements['group_' + str(name)] = group

        dict_for_measurement = group[columns_for_measurement].to_dict(orient='index')
        dict_for_measurement = list(dict_for_measurement.values())[0]

        dict_for_insertion = {}
        dict_for_insertion['date'] = dict_for_measurement['Datum']
        dict_for_insertion['producer'] = dict_for_measurement['Messreihe']
        dict_for_insertion['measurement_series'] = dict_for_measurement['Erfasser']
        pv_module_number = dict_for_measurement['PV_Modul'].split(': ')[1]

        #dict_for_measurement['pv_module_id'] = db.session.query(PvModule).filter(PvModule.model == pv_module_number).first()

        new_measurement = Measurement(**dict_for_insertion)
        chosen_module = db.session.query(PvModule).filter(PvModule.model == pv_module_number).first()

        chosen_module.measurements.append(new_measurement)

        measurement_values = 8
        commit_measurement_values_to_database(group[columns_for_values], new_measurement)


def commit_pvmodule_to_database(df):
    df.columns = get_columns_of_table("PVMODULE")
    convert_df_columns_to_desired_type("PVMODULE", df)

    pv_module_df = df[df.columns[0:8]]
    pv_module_dict = pv_module_df.to_dict(orient='index')

    manufacturer_df = df[df.columns[8:15]]
    manufacturer_dict = manufacturer_df.to_dict(orient='index')

    flasher_df = df[df.columns[15:22]]
    flasher_dict = flasher_df.to_dict(orient='index')
    # format: dict like {index -> {column -> value}}

    for key in pv_module_dict:
        new_pv_module = PvModule(**(pv_module_dict[key]))
        new_manufacturer_data = ManufacturerData(**(manufacturer_dict[key]))
        new_flasher_data = FlasherData(**(flasher_dict[key]))
        new_pv_module.manufacturer_data = new_manufacturer_data
        new_pv_module.flasher_data = new_flasher_data

        db.session.add(new_pv_module)
        db.session.commit()


def commit_dataframe_to_database(df, type_of_data="MEASUREMENT"):
    """take data frame and write it as dictionary and insert into sql alchemy"""
    df.columns = get_columns_of_table(type_of_data)
    convert_df_columns_to_desired_type(type_of_data, df)

    # format: dict like {index -> {column -> value}}
    dictionary_for_insertion = df.to_dict(orient='index')
    if type_of_data is 'MEASUREMENT':
        # "**" star operator take dictionary for values in ORM model
        for key in dictionary_for_insertion:
            new_data = Measurement(**(dictionary_for_insertion[key]))
            db.session.add(new_data)
    elif type_of_data is 'PVMODULE':
        for key in dictionary_for_insertion:
            new_data = PvModule(**(dictionary_for_insertion[key]))
            db.session.add(new_data)
    else:
        raise ValueError("dataframe from excel was neither labeled measurement or pv_module")
