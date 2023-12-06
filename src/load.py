"""
Load into a postgres database
"""
import logging
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()


def read_as_list(x):
    return x.strip("[]").split(", ")


def load_into_postgres(df):
    engine = create_engine(f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_URL']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}")
    with engine.begin() as connection:
        df.to_sql(name='datasets', con=connection, if_exists='replace', index=False)


def load(filename='metadata'):
    df = pd.read_csv(filename + '_processed.csv', sep=';', converters={"spatial": read_as_list})
    logging.info('Loading data into postgres')
    load_into_postgres(df)

if __name__ == "__main__":
    load()
