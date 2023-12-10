import pandas as pd
import logging
from unidecode import unidecode
from dotenv import load_dotenv

load_dotenv()

pattern_open_access = [
    "pas de restriction d'accès public selon inspire",
    "licence ouverte",
    "open licence",
]


def split_geo_levels(insee_uris: list, geo_level: str) -> str:
    """
    Filter a list of INSEE URI to a specific geographical zoom level
    Attribute zoom_level can be 'commune' or 'departement'

    Returns a string in which the different elements of the same zoom are seperated by a ','
    """
    geos_elements = []
    for insee_uri in insee_uris:
        if geo_level in insee_uri:
            geos_elements.append(insee_uri.split(f'{geo_level}/')[1].split('\'')[0])
    return geos_elements

def define_geo_coverage(insee_uris: list) -> str:
    """
    Map a list or INSEE URI to a spatial coverage : 'departemental' or 'intra-departemental'
    """
    communes = 0
    departements = 0
    for insee_uri in insee_uris:
        if 'commune' in insee_uri:
            communes += 1
        elif 'departement' in insee_uri:
            departements += 1
    if communes >= 1:
        return 'Communale'
    elif departements >= 1:
        return 'Départementale'
    else:
        return None


def create_universe_pprn(row):
    """
    For a specific row, return if the element is considered to be a part of the 'PPRN' universe
    """
    for elem in ['title', 'description']:
        if 'pprn' in row[elem].lower():
            return 'PPRN'
        elif 'prevention des risques naturels' in unidecode(row[elem]).lower():
            return 'PPRN'
    return None


def process_geo_data(df: pd.DataFrame) -> pd.DataFrame:
    # Isolate commune or departement values
    df['commune'] = df['spatial'].apply(lambda x: split_geo_levels(x, 'commune'))
    df['departement'] = df['spatial'].apply(lambda x: split_geo_levels(x, 'departement'))
    df['departement'] = df.apply(lambda row: row['departement'] if not row['commune'] else None, axis=1) 
    
    # Define the zoom level of the spatial resolution
    df['geo_coverage'] = df['spatial'].apply(define_geo_coverage)
    del df['spatial']
    return df


def map_right_statement(x):
    if isinstance(x, str):
        return any(label in x.lower().replace('\n', ' ') for label in pattern_open_access)
    else :
        return False
    

def read_as_list(x):
    return x.strip("[]").split(", ")


def clean_contact_points(contact_points:pd.Series):
    return contact_points.apply(lambda x: x.split('catalog/')[1] if isinstance(x, str) else None)


def clean_licenses(licenses:pd.Series):
    def clean_values(x):
        if x == '[]' or x == '[None]' or 'BNode' in x:
            x = '[]'
        return x.split('rdflib.term.URIRef(')[1] if x != '[]' else '[]'
    return licenses.apply(clean_values)


def transform(filename='metadata'):
    df = pd.read_csv(filename + '.csv', sep=';', converters={"spatial": read_as_list})
    df['univers'] = df.apply(create_universe_pprn, axis=1)
    df = process_geo_data(df)
    df["right_statement_processed"] = df["right_statement"].apply(map_right_statement)
    df["contact_points"] = clean_contact_points(df["contact_points"])
    df["licenses"] = clean_licenses(df["licenses"])
    # Convert all array elemnts to PSQL arrays
    for col in ['departement', 'commune', 'themes', 'key_words', 'licenses']:
        df[col] = df[col].apply(lambda x: str(x).replace('[', '{').replace(']', '}').replace('\'', ''))

    df.to_csv(filename + '_processed.csv', sep=';', index=False, mode='w')


if __name__ == "__main__":
    transform()
