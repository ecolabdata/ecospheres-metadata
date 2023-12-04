import pandas as pd
import logging
from unidecode import unidecode

from dotenv import load_dotenv

load_dotenv()


def create_universe_pprn(row):
    """
    For a specific row, return if the element is considered to be a part of the 'PPRN' universe
    """
    for elem in ['title', 'description']:
        if 'pprn' in row[elem].lower():
            return 'PPRN'
        elif 'prevention des risques naturel' in unidecode(row[elem]).lower():
            return 'PPRN'
    return None


if __name__ == "__main__":
    filename = 'metadata'
    df = pd.read_csv(filename + '.csv', sep=';')
    df['univers'] = df.apply(create_universe_pprn, axis=1)
    df['test_infra'] = 0
    df.to_csv(filename + '_processed.csv' , sep=';', index=False)
