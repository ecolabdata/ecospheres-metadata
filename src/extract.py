import pandas as pd
import os
import s3fs
import logging
import json

from dotenv import load_dotenv
from dcat_reader_ckan import DatasetReader

load_dotenv()

def extract(filename: str) -> pd.DataFrame:
    """
    Extract data from dump on S3
    """
    fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': os.environ['S3_ENDPOINT_URL']}, key=os.environ['ACCESS_KEY'], secret=os.environ['SECRET_KEY'])

    datasets = []
    iteration = 0
        
    for graph in fs.ls(os.environ['BUCKET_NAME'] + '/DUMP_INTEGRATION_JSON'):
        if '.json' in graph:
            with fs.open(graph, mode="rb") as file_in:
                read_data = file_in.read()
                page_datasets = DatasetReader(read_data).get_data()
                logging.debug("Fichier: ", graph, "- Nombre de datasets : ", len(datasets))
                datasets.append(
                    page_datasets
                )
                iteration += 1

    logging.debug("Nombre de pages traitées : ", iteration)
    data = pd.concat(datasets)
    data.to_csv(filename, sep=';', index=False)
    return data


if __name__ == "__main__":
    extract("metadata.csv")
