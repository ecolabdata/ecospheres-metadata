import unittest
from utils.dcat_reader_ckan import DCATReaderCKAN
import rdflib

class TestDCATReaderCKAN(unittest.TestCase):

    dcat_read = DCATReaderCKAN("ecospheres-metadata/utils/test_dcat_exposition.json")
    dataset_uri = rdflib.term.URIRef("http://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/catalog.search#/metadata/fr-120066022-jdd-0a3ba9b5-5d70-4bca-9cac-11748af921cf")

    def test_get_dataset_title(self):
        # Test proper title is returned
        title = self.dcat_read.get_dataset_title(self.dataset_uri)              
        self.assertEqual(str(title),
                         "Zones exposées au bruit en Haute-Savoie (Lden)")
        
        # Test error is raised if dataset_uri not of type rdflib.term.URIRef
        dataset_uri_as_str = "http://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/catalog.search#/metadata/fr-120066022-jdd-0a3ba9b5-5d70-4bca-9cac-11748af921cf"
        with self.assertRaises(AssertionError):
            self.assertRaises(self.dcat_read.get_dataset_title(dataset_uri_as_str))  
            
    def test_get_dataset_description(self):
        # Test proper description is returned
        description = self.dcat_read.get_dataset_description(self.dataset_uri)              
        self.assertEqual(str(description),
                         "Zones exposées à des niveaux sonores supérieurs à 55 dB(A) le long des routes dont le trafic annuel est supérieur à 3 millions de véhicules.\nCes zones sont délimitées par des courbes isophones calculées selon l’indicateur Lden, avec un pas de 5 en 5 dB(A), pour l’établissement des cartes stratégiques de bruit le long des infrastructures routières de Haute-Savoie.\nLden est un indicateur du niveau de bruit global pendant une journée (jour, soir et nuit) utilisé pour qualifier la gêne liée à l'exposition au bruit. Il est calculé à partir des indicateurs “Lday”, “Levening”, “Lnight”, niveaux sonores moyennés sur les périodes 6h-18h, 18h-22h et 22h-6h.\nDe plus, une pondération de +5 dB(A) est appliquée à la période du soir et de +10 dB(A) à celle de la nuit, pour tenir compte du fait que nous sommes plus sensibles au bruit au cours de ces périodes.\nUne extraction pour un itinéraire peut-être produite par la DDT 74 en adressant un message au contact.")
        
        # Test error is raised if dataset_uri not of type rdflib.term.URIRef
        dataset_uri_as_str = "http://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/catalog.search#/metadata/fr-120066022-jdd-0a3ba9b5-5d70-4bca-9cac-11748af921cf"
        with self.assertRaises(AssertionError):
            self.assertRaises(self.dcat_read.get_dataset_description(dataset_uri_as_str))

    def test_get_dataset_modification(self):
        # Test proper description is returned
        modification_date = self.dcat_read.get_dataset_modification(self.dataset_uri)              
        self.assertEqual("2018-08-02",
                         str(modification_date))
        
        # Test error is raised if dataset_uri not of type rdflib.term.URIRef
        dataset_uri_as_str = "http://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/catalog.search#/metadata/fr-120066022-jdd-0a3ba9b5-5d70-4bca-9cac-11748af921cf"
        with self.assertRaises(AssertionError):
            self.assertRaises(self.dcat_read.get_dataset_modification(dataset_uri_as_str))

    def test_get_dataset_modification(self):
        # Test proper modification date is returned
        modification_date = self.dcat_read.get_dataset_modification(self.dataset_uri)              
        self.assertEqual("2018-08-02",
                         str(modification_date))
        
        # Test error is raised if dataset_uri not of type rdflib.term.URIRef
        dataset_uri_as_str = "http://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/catalog.search#/metadata/fr-120066022-jdd-0a3ba9b5-5d70-4bca-9cac-11748af921cf"
        with self.assertRaises(AssertionError):
            self.assertRaises(self.dcat_read.get_dataset_modification(dataset_uri_as_str))
            
    def test_get_dataset_right_statement(self):
        # Test proper modification date is returned
        right_statement = self.dcat_read.get_dataset_right_statement(self.dataset_uri)      
        
        right_statement_1 = "Aucun des articles de la loi ne peut être invoqué pour justifier d'une restriction d'accès public."
        right_statement_2 = "Pas de restriction d'accès public selon INSPIRE" 
        right_statement_ref = right_statement_1 + " " + right_statement_2       
        
        self.assertEqual(right_statement,
                         right_statement_ref)
        
        # Test error is raised if dataset_uri not of type rdflib.term.URIRef
        dataset_uri_as_str = "http://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/catalog.search#/metadata/fr-120066022-jdd-0a3ba9b5-5d70-4bca-9cac-11748af921cf"
        with self.assertRaises(AssertionError):
            self.assertRaises(self.dcat_read.get_dataset_right_statement(dataset_uri_as_str))
            
    def test_get_dataset_key_words(self):
        # Test proper modification date is returned
        key_words = self.dcat_read.get_dataset_key_words(self.dataset_uri)      
        
        key_word_1 = "zone de bruit"
        key_word_2 = "directive 2002/49/ce"
        key_word_3 = "données ouvertes"
        key_word_4 = "Zones de gestion, de restriction ou de réglementation et unités de déclaration"
        key_word_5 = "Nuisance/Bruit" 
        key_words_ref = key_word_1 + " " + key_word_2 + " " + key_word_3 + " " + key_word_4 + " " + key_word_5
        
        self.assertEqual(key_words,
                         key_words_ref)
        
        # Test error is raised if dataset_uri not of type rdflib.term.URIRef
        dataset_uri_as_str = "http://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/catalog.search#/metadata/fr-120066022-jdd-0a3ba9b5-5d70-4bca-9cac-11748af921cf"
        with self.assertRaises(AssertionError):
            self.assertRaises(self.dcat_read.get_dataset_key_words(dataset_uri_as_str))
            
    def test_get_data(self):
        # Nombre de datasets collectés
        datasets = self.dcat_read.get_data() 
        datasets.to_excel("datasets.xlsx")
        
        search_word = '\"dcat:Dataset\"'
        with open("utils/test_dcat_exposition.json", "r") as file:
            data = file.read()
            dataset_count = data.count(search_word)
        
        self.assertEqual(dataset_count, len(datasets))
            
if __name__ == '__main__':
    unittest.main()