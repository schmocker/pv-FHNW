import os
import pandas as pd
from .db import db, Measurement, PvModule, FlasherData, ManufacturerData, MeasurementValues
import configparser

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'pvtool/files')
ALLOWED_EXTENSIONS = set(['csv', 'xls', 'xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_data_file(filename, linked_measurement):
    """open the file containing data and pass table as pandas dataframe with measurement to be linked"""
    path_to_file = os.path.join(UPLOAD_FOLDER, filename)
    with open(path_to_file) as f:
        if filename.endswith('.csv'):
            dataframe = pd.read_csv(f, sep=',')
        elif filename.endswith(('.xls', '.xlsx')):
            dataframe = pd.read_excel(f)
        commit_measurement_values_to_database(dataframe, linked_measurement)
    os.remove(path_to_file)


def process_pv_module_file(filename):
    path_to_file = os.path.join(UPLOAD_FOLDER, filename)
    with open(path_to_file) as f:
        if filename.endswith('.csv'):
            dataframe = pd.read_csv(f, sep=',')
        elif filename.endswith(('.xls', '.xlsx')):
            dataframe = pd.read_excel(f)
    commit_pvmodule_to_database(dataframe)
    os.remove(path_to_file)


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
    print(config.sections())
    columns = [option for option in config[type_of_data]]
    print("new columns: ", columns)
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
    print("current columns: ", df.columns)
    df.columns = get_columns_of_table("MEASUREMENT")
    convert_df_columns_to_desired_type("MEASUREMENT", df)

    # format: dict like {index -> {column -> value}}
    dictionary_for_insertion = df.to_dict(orient='index')
    print(dictionary_for_insertion)

    # "**" star operator take dictionary for values in ORM model
    for key in dictionary_for_insertion:
        print(dictionary_for_insertion[key])
        new_measurement_values = MeasurementValues(**(dictionary_for_insertion[key]))
        linked_measurement.measurement_values.append(new_measurement_values)
        db.session.add(linked_measurement)
    db.session.commit()


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
    print("current columns: ", df.columns)
    df.columns = get_columns_of_table(type_of_data)
    convert_df_columns_to_desired_type(type_of_data, df)

    # format: dict like {index -> {column -> value}}
    dictionary_for_insertion = df.to_dict(orient='index')
    print(dictionary_for_insertion)
    if type_of_data is 'MEASUREMENT':
        # "**" star operator take dictionary for values in ORM model
        for key in dictionary_for_insertion:
            print(dictionary_for_insertion[key])
            new_data = Measurement(**(dictionary_for_insertion[key]))
            db.session.add(new_data)
    elif type_of_data is 'PVMODULE':
        for key in dictionary_for_insertion:
            new_data = PvModule(**(dictionary_for_insertion[key]))
            db.session.add(new_data)
    else:
        raise ValueError("dataframe from excel was neither labeled measurement or pv_module")
