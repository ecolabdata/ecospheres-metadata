import nbformat
import glob
import sqlalchemy
import configparser
import os
from utils import get_environment_tag
import subprocess

def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    database_url = "postgresql+psycopg2://{}:{}@{}/{}".format(
        config["DATABASE"]["user"],
        config["DATABASE"]["password"],
        config["DATABASE"]["host"],
        config["DATABASE"]["database"],
    )

    notebooks = []
    for notebook in glob.glob("[0-9][0-9]*.ipynb"):
        print(notebook)
        notebooks.append(nbformat.read(notebook, as_version=4))
        
    metadata_report = nbformat.v4.new_notebook(metadata=notebooks[0].metadata)
    metadata_report.cells = notebooks[0].cells
    for i, notebook in enumerate(notebooks):
        if i > 0:
            metadata_report.cells += notebooks[i].cells

    engine = sqlalchemy.create_engine(database_url)
    environment_tag = get_environment_tag(engine.url.host, engine.url.database)
    
    nbformat.write(metadata_report, "metadata_report.ipynb".format(environment_tag))
    
    subprocess.run(
        [
            "jupyter",
            "trust",
            "metadata_report.ipynb",
        ]
    )
        
    output = "{}.html".format(environment_tag)

    subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "metadata_report.ipynb",
            "--to",
            "slides",
            "--output",
            output,
            "--SlidesExporter.reveal_scroll=True",
            "--no-input",
            "--ExecutePreprocessor.timeout=1200",
        ]
    )

    os.remove("metadata_report.ipynb")


if __name__ == "__main__":
    main()
