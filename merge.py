import nbformat
import glob
import sqlalchemy
import configparser
import os
from utils import get_environment_tag
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup

def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    database_url = "postgresql+psycopg2://{}:{}@{}/{}".format(
        config["DATABASE"]["user"],
        config["DATABASE"]["password"],
        config["DATABASE"]["host"],
        config["DATABASE"]["database"],
    )

    # Merge notebooks
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
    
    # Convert notebooks to revealjs slides    
    subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "metadata_report.ipynb",
            "--to",
            "slides",
            "--output",
            environment_tag,
            "--SlidesExporter.reveal_scroll=True",
            "--SlidesExporter.reveal_number=c/t",
            "--no-input",
            "--ExecutePreprocessor.timeout=1200",
        ]
    )

    # Add date and environment tags in slides
    with open(environment_tag + ".slides.html", 'r',  encoding="utf8") as f:
        report_html = f.read()
    
    soup = BeautifulSoup(report_html, 'html.parser')
    soup.find(id="header_left").string.replace_with(datetime.today().strftime('%Y-%m-%d'))
    soup.find(id="header_right").string.replace_with(config["DATABASE"]["host"].split(".")[0])
    
    with open(environment_tag + ".slides.html", "wb") as file:
        file.write(soup.prettify("utf-8"))
        
    # Delete temporary file
    os.remove("metadata_report.ipynb")
    
if __name__ == "__main__":
    main()
