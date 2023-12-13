import pandas as pd
from unidecode import unidecode
from dotenv import load_dotenv

load_dotenv()

pattern_open_access = [
    "pas de restriction d'accès public selon inspire",
    "licence ouverte",
    "open licence",
]


RAW_COLUMNS = [
    'catalog',
    'contact_point',
    'licenses',
    'modification',
    'rights_holder',
    'right_statement',
    'spatial',
    'status',
    'title'
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
    """
    For a given RightsStatement, indicates if it matches a set of saved patterns.
    If a pattern is included in the RightsStatement, returns True to indicate it's open access
    """
    if isinstance(x, str):
        return any(label in x.lower().replace('\n', ' ') for label in pattern_open_access)
    else:
        return False


def clean_contact_point(contact_point: pd.Series):
    """
    Clean the field ContactPoint by removing the URL prefix
    """
    return contact_point.apply(lambda x: x.split('catalog/')[1] if isinstance(x, str) else None)


def clean_licenses(licenses: pd.Series):
    """
    Clean the field Licenses by removing the URL prefix and uniformization of null values
    """
    def clean_values(x):
        if x == '[]' or x == '[None]' or 'BNode' in x or x is None:
            return None
        x = x.replace('rdflib.term.URIRef', '')
        x = x.replace('\'', '')
        x = x.replace('(', '').replace(')', '')
        return x
    return licenses.apply(clean_values)


def percantage_filling(df: pd.DataFrame) -> pd.Series:
    return 100 * df[RAW_COLUMNS].count(axis=1) / len(RAW_COLUMNS)


#############
# Utils
#############



def read_as_list(x):
    """
    Convert a string as a list
    """
    return x.strip("[]").split(", ")


#############
# Main
#############


def transform(filename='metadata'):
    df = pd.read_csv(filename + '.csv', sep=';', converters={"spatial": read_as_list})

    df['percantage_filling'] = percantage_filling(df)
    df['univers'] = df.apply(create_universe_pprn, axis=1)
    df = process_geo_data(df)
    df["right_statement_processed"] = df["right_statement"].apply(map_right_statement)
    df["contact_point"] = clean_contact_point(df["contact_point"])
    df["licenses"] = clean_licenses(df["licenses"])

    # Convert all array elemnets to PSQL arrays
    for col in ['departement', 'commune', 'themes', 'key_words', 'licenses']:
        df[col] = df[col].apply(lambda x: str(x).replace('[', '{').replace(']', '}').replace('\'', ''))

    df.to_csv(filename + '_processed.csv', sep=';', index=False, mode='w')
    return df


if __name__ == "__main__":
    transform()
