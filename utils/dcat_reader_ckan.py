"""
DCATReaderCKAN
"""
import rdflib
import pandas as pd

MAPPER_STATUS = {
    'COMPLETED': 'Completed',
    'onGoing': 'On Going',
    'historicalArchive': 'Historical Archive',
    'UnderDevelopment': 'Under Development', 
    'obsolete': 'Obsolete',
    'required': 'Required',
    'planned': 'Planned',
     None: 'None'
}

class Reader:
    def __init__(self, graph_src:bytes, format='json-ld'):
        self.graph_src = graph_src
        self.format = format
        self._graph = rdflib.Graph().parse(data=self.graph_src, format='json-ld')
        
    def get_title(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        return self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/title"))


class CatalogReader(Reader):

    def get_data(self) -> pd.DataFrame:
        """ Given the path of a DCAT formated metadata graph,
        returns a DataFrame with dataset URIs as index and
        the following metadata : title, description,
        modification date, right stateme, key words. Each medatada
        is handled separetly in a dedicated method.
        """
        catalogs_uri = self.get_catalogs_uri()
        data = []
        for uri in catalogs_uri:
            data.append(
                {
                    "catalog": uri,
                    "title": self.get_title(uri),
                    #"catalog_records": self.get_records(uri)
                }
            )
        return pd.DataFrame(data)

    def get_catalogs_uri(self) -> list[rdflib.term.URIRef]:        
        uri_list = []
        for subject, _, _ in self._graph.triples((None, rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),rdflib.term.URIRef("http://www.w3.org/ns/dcat#Catalog"))):
            uri_list.append(subject)
        return uri_list
        
    def get_records(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        contact_points = []
        for _, _, object in self._graph.triples((dataset_uri,rdflib.term.URIRef("http://www.w3.org/ns/dcat#contactPoint"), None)):
            contact_points.append(object)
        return ' '.join(contact_points)

        
class DatasetReader(Reader):
    def __init__(self, graph_src:bytes, format='json-ld'):
        self.graph_src = graph_src
        self.format = format
        self._graph = rdflib.Graph().parse(data=self.graph_src, format='json-ld')
        
    def get_data(self) -> pd.DataFrame:
        """ Given the path of a DCAT formated metadata graph,
        returns a DataFrame with dataset URIs as index and
        the following metadata : title, description,
        modification date, right stateme, key words. Each medatada
        is handled separetly in a dedicated method.
        """
        dataset_uri = self.get_datasets_uri()

        data = []
        for uri in dataset_uri:
            data.append(
                {
                    "dataset": uri,
                    "title": self.get_title(uri),
                    "description": self.get_dataset_description(uri),
                    "modification": self.get_dataset_modification(uri),
                    "right_statement": self.get_dataset_right_statement(uri),
                    "themes": self.get_dataset_themes(uri),
                    "key_words": self.get_dataset_key_words(uri),
                    "standard": self.get_dataset_standard(uri),
                    "creator": self.get_dataset_creator(uri),
                    "status": self.get_dataset_status(uri),
                    "catalog": self.get_dataset_catalog(uri)
                }
            )
            
        return pd.DataFrame(data)
        
    def get_datasets_uri(self) -> list[rdflib.term.URIRef]:        
        uri_list = []
        for subject, _, _ in self._graph.triples((None, rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),rdflib.term.URIRef("http://www.w3.org/ns/dcat#Dataset"))):
            uri_list.append(subject)
        return uri_list
    
    def get_dataset_description(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        return self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/description"))
    
    def get_dataset_modification(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        return self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/modified"))
    
    def get_dataset_right_statement(self, dataset_uri:rdflib.term.URIRef)->str:
        """ Returns a joined string of available ritht statements.
        """
        assert type(dataset_uri) == rdflib.term.URIRef
        rigth_statements = []
        for _, _, object in self._graph.triples((dataset_uri,rdflib.term.URIRef("http://purl.org/dc/terms/accessRights"), None)):    
            for _, _, object_bnode in self._graph.triples((object,rdflib.term.URIRef("http://www.w3.org/2000/01/rdf-schema#label"), None)):
                rigth_statements.append(object_bnode)
                
        return ' '.join(rigth_statements)
        
    def get_dataset_themes(self, dataset_uri:rdflib.term.URIRef)->str:
        """ Returns a joined string of available key words. 
        """
        assert type(dataset_uri) == rdflib.term.URIRef
        themes = []
        for _, _, object in self._graph.triples((dataset_uri,rdflib.term.URIRef("http://www.w3.org/ns/dcat#theme"), None)):
            themes.append(object)
        return ' '.join(themes)
    
    def get_dataset_key_words(self, dataset_uri:rdflib.term.URIRef)->str:
        """ Returns a joined string of available key words. 
        """
        assert type(dataset_uri) == rdflib.term.URIRef
        key_words = []
        for _, _, object in self._graph.triples((dataset_uri,rdflib.term.URIRef("http://www.w3.org/ns/dcat#keyword"), None)):
            key_words.append(object)
        return ' '.join(key_words)

    def get_dataset_standard(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        return self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/Standard"))

    def get_dataset_creator(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        return self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/creator"))

    def get_dataset_status(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        status = self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://www.w3.org/ns/adms#status"))
        # Extract the status form the URL
        status = status.split('/')[-1] if status else None
        return MAPPER_STATUS[status]

    def get_dataset_catalog(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        catalog_record = self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://xmlns.com/foaf/0.1/isPrimaryTopicOf"))
        catalog = self._graph.value(subject=catalog_record, predicate=rdflib.term.URIRef("http://www.w3.org/ns/dcat#inCatalog"))
        return self.get_title(catalog)
        