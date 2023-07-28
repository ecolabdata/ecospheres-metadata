import geopandas as gpd
import time
import pandas as pd
from IPython.display import display, Markdown
import json
import requests
from bs4 import BeautifulSoup
import datetime
import configparser
import sqlalchemy

def count_words(sentence: str) -> int:
    try:
        return len(sentence.split())
    except AttributeError as exception:
        print(exception)


def compute_areas_km2(geoms: gpd.GeoSeries) -> gpd.GeoSeries:
    """Returns areas in km2."""
    if geoms.crs.coordinate_system.name != "cartesian":
        raise Exception("Invalid coordinate system")
    else:
        return geoms.apply(lambda x: x.area * 1e-6)

# Prefeference for itables.show
def head_as_table(data: pd.DataFrame, n_rows: int = 1, index=False) -> None:
    """Pretty-print the head of a Pandas table in a Jupyter notebook and show its dimensions."""
    display(
        Markdown(
            "**tableau complet :** {} lignes × {} colonnes".format(
                len(data), len(data.columns)
            )
        )
    )
    display(data.head(n_rows).style.hide(axis="index"))

def get_environment_tag(host: str, database: str) -> str:
    """From host and datbase name return a tag to distinguish between
    preprod, integration or backup data."""

    tag = time.strftime("%Y%m%d-%H%M%S")
    tag += "_" + host + "_" + database

    return tag


def get_value_from_json_serialization(data, key) -> list:
    """Get values associated to a key from JSON-serialized data.
    In the CKAN package_extra table, values are
    embedded in list of dictionnaries stored as strings.
    Example: '[{"uri": "http://www.opengis.net/def/crs/EPSG/0/2154"},
    {"uri": "http://www.opengis.net/def/crs/EPSG/0/2972"}]

    Parameters
    ----------
        data (str): JSON-serialized data
        key (str): dictionnary key whose value is to be read

    Returns
    ------
        List of values corresponding to the input key
    """

    try:
        data_list = json.loads(data)
        values = []
        for data_dict in data_list:
            values.append(data_dict[key])

        return values

    except Exception as exception:
        print("Exception: ", exception)
        return []


def get_value_from_xml(uri: str, tag: str, **kwargs) -> list:
    """Returns a list of values associated to given
    tags in an XML file.

    Parameters
    ----------
        uri(str): uri pointing at the XML file
        tag(str): XML tag to locate the desired value
        **kwargs(dict): to specify XML attributes
    """

    request = requests.get(uri)

    values = []
    if request.status_code == 200:
        contents = BeautifulSoup(request.content, "lxml").find_all(tag, **kwargs)
        for content in contents:
            values.append(content.text)
    else:
        print(f"Failed request for {uri}")

    return values

def date_string_to_datetime(date:str)->datetime.datetime:    
    try:
        return datetime.datetime.fromisoformat(date)
    except ValueError as exception:
        print("Exception: ", exception)
        return None
    
def wrapper_engine(config:str):
    """ Returns an SQLAlchemy engine
    """
    
    config = configparser.ConfigParser()
    config.read('config.ini')

    database_url = "postgresql+psycopg2://{}:{}@{}/{}".format(
    config['DATABASE']['user'],
    config['DATABASE']['password'],
    config['DATABASE']['host'], 
    config['DATABASE']['database'],
    )

    return sqlalchemy.create_engine(database_url)