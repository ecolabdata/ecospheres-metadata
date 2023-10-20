import rdflib
import pandas as pd

class DCATReaderCKAN:
    def __init__(self, graph_path:str):
        self.graph_path = graph_path
        self._graph = rdflib.Graph().parse(graph_path)
        
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
                    "title": self.get_dataset_title(uri),
                    "description": self.get_dataset_description(uri),
                    "modification": self.get_dataset_modification(uri),
                    "right_statement": self.get_dataset_right_statement(uri),
                    "key_words": self.get_dataset_key_words(uri)
                }
            )
            
        return pd.DataFrame(data)
        
    def get_datasets_uri(self) -> list[rdflib.term.URIRef]:        
        uri_list = []
        for subject, _, _ in self._graph.triples((None, rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),rdflib.term.URIRef("http://www.w3.org/ns/dcat#Dataset"))):
            uri_list.append(subject)
        return uri_list
    
    def get_dataset_title(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        return self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/title"))
    
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
    
    def get_dataset_key_words(self, dataset_uri:rdflib.term.URIRef)->str:
        """ Returns a joined string of available key words. 
        """
        assert type(dataset_uri) == rdflib.term.URIRef
        key_words = []
        for _, _, object in self._graph.triples((dataset_uri,rdflib.term.URIRef("http://www.w3.org/ns/dcat#keyword"), None)):
            key_words.append(object)
        return ' '.join(key_words)