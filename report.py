import nbformat
import glob
import sqlalchemy
import configparser
import os
from utils import get_environment_tag
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup
import argparse
import papermill as pm
import os

def __execute():
    """ Execute available notebooks from the rootfolder and save
    resutling outputs in the temp folder. Only output-clear
    notebooks are pushed.
    """
    
    # notebooks = []
    for notebook in glob.glob("[0-9][0-9]*.ipynb"):
        # notebooks.append(nbformat.read(notebook, as_version=4))        
    # for notebook in notebooks:
        output_notebook = "temp/" + str(notebook)
        print("Execute " + notebook)
        try:
            pm.execute_notebook(notebook, output_notebook)
        except Exception as exception:
            print(f"Exception: {exception}")

def __generate():
    """ Merge all notbooks with cell-outputs and generate
    reveal.js slides.
    """    
    notebooks = []
    for notebook in glob.glob("temp/[0-9][0-9]*.ipynb"):
        print(notebook)
        notebooks.append(nbformat.read(notebook, as_version=4))
        
    metadata_report = nbformat.v4.new_notebook(metadata=notebooks[0].metadata)
    metadata_report.cells = notebooks[0].cells
    for i, notebook in enumerate(notebooks):
        if i > 0:
            metadata_report.cells += notebooks[i].cells

    # Get data environment
    config = configparser.ConfigParser()
    config.read("config.ini")

    database_url = "postgresql+psycopg2://{}:{}@{}/{}".format(
        config["DATABASE"]["user"],
        config["DATABASE"]["password"],
        config["DATABASE"]["host"],
        config["DATABASE"]["database"],
    )
    
    engine = sqlalchemy.create_engine(database_url)
    environment_tag = get_environment_tag(engine.url.host, engine.url.database)
    nbformat.write(metadata_report, "temp/metadata_report.ipynb".format(environment_tag))
    
    subprocess.run(
        [
            "jupyter",
            "trust",
            "temp/metadata_report.ipynb",
        ]
    )
    # Convert notebooks to revealjs slides    
    subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "temp/metadata_report.ipynb",
            "--to",
            "slides",
            "--output-dir",
            os.getcwd(),
            "--output",
            environment_tag,
            "--SlidesExporter.reveal_scroll=True",
            "--SlidesExporter.reveal_number=c/t",
            "--no-input",
            "--ExecutePreprocessor.timeout=1200",
        ]
    )

    # Add date and environment tags in slides
    with open(environment_tag + ".slides.html", 'r',  encoding="utf8") as file:
        report_html = file.read()
    
    soup = BeautifulSoup(report_html, 'html.parser')
    soup.find(id="header_left").string.replace_with(datetime.today().strftime('%Y-%m-%d'))
    soup.find(id="header_right").string.replace_with(config["DATABASE"]["host"].split(".")[0])
    
    with open(environment_tag + ".slides.html", "wb") as file:
        file.write(soup.prettify("utf-8"))
        
    # Delete temporary file
    os.remove("temp/metadata_report.ipynb")
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', default=False)
    parser.add_argument('--generate', default=False)
    
    args = parser.parse_args()
    
    if args.execute:
        __execute()
        
    if args.generate:
        __generate()
        
    if (args.generate is False) and (args.execute is False):
        print("Select option --generate True and/or --execute True") 