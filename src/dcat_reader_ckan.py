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
    None: None
}
        
class DatasetReader():

    def __init__(self, graph_src: bytes, format='json-ld'):
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
                    "creator": self.get_dataset_creator(uri),
                    "rights_holder": self.get_dataset_right_holders(uri),
                    "contact_points": self.get_dataset_contact_points(uri),
                    "status": self.get_dataset_status(uri),
                    "catalog": self.get_dataset_catalog(uri),
                    "spatial": self.get_dataset_spatial(uri),
                    "licenses": self.get_dataset_licenses(uri)
                }
            )
        return pd.DataFrame(data)
        
    def get_title(self, dataset_uri:rdflib.term.URIRef)->rdflib.term.Literal:
        return self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/title"))
        
    def get_datasets_uri(self) -> list[rdflib.term.URIRef]:        
        uri_list = []
        for subject, _, _ in self._graph.triples((None, rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),rdflib.term.URIRef("http://www.w3.org/ns/dcat#Dataset"))):
            uri_list.append(subject)
        return uri_list
    
    def get_dataset_description(self, dataset_uri: rdflib.term.URIRef) -> rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        return self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/description"))
    
    def get_dataset_modification(self, dataset_uri: rdflib.term.URIRef) -> rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        return self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/modified"))
    
    def get_dataset_right_statement(self, dataset_uri: rdflib.term.URIRef) -> str:
        """ Returns a joined string of available ritht statements.
        """
        assert type(dataset_uri) == rdflib.term.URIRef
        rigth_statements = []
        for _, _, object in self._graph.triples((dataset_uri,rdflib.term.URIRef("http://purl.org/dc/terms/accessRights"), None)):    
            for _, _, label in self._graph.triples((object,rdflib.term.URIRef("http://www.w3.org/2000/01/rdf-schema#label"), None)):
                rigth_statements.append(label)
        return rigth_statements
        
    def get_dataset_themes(self, dataset_uri: rdflib.term.URIRef) -> str:
        """ Returns a joined string of available themes. 
        """
        assert type(dataset_uri) == rdflib.term.URIRef
        themes = []
        for _, _, object in self._graph.triples((dataset_uri,rdflib.term.URIRef("http://www.w3.org/ns/dcat#theme"), None)):
            themes.append(object)
        return themes
    
    def get_dataset_key_words(self, dataset_uri: rdflib.term.URIRef) ->str:
        """ Returns a joined string of available key words. 
        """
        assert type(dataset_uri) == rdflib.term.URIRef
        key_words = []
        for _, _, object in self._graph.triples((dataset_uri, rdflib.term.URIRef("http://www.w3.org/ns/dcat#keyword"), None)):
            key_words.append(object)
        return key_words

    def get_dataset_creator(self, dataset_uri: rdflib.term.URIRef) -> rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        creator = self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/creator"))
        # Creator is an Organization
        if creator:
            return self._graph.value(subject=creator, predicate=rdflib.term.URIRef("http://xmlns.com/foaf/0.1/name")).value
        else:
            return None

    def get_dataset_right_holders(self, dataset_uri: rdflib.term.URIRef) -> rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        rights_holder = self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/rights_holder"))
        # Rights Holder is an Organization
        if rights_holder:
            return self._graph.value(subject=rights_holder, predicate=rdflib.term.URIRef("http://xmlns.com/foaf/0.1/name")).value
        else:
            return None

    def get_dataset_status(self, dataset_uri: rdflib.term.URIRef) -> rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        status = self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://www.w3.org/ns/adms#status"))
        
        # Extract the status form the URL
        status = status.split('/')[-1] if status else None
        return MAPPER_STATUS[status]

    def get_dataset_catalog(self, dataset_uri: rdflib.term.URIRef) -> rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        catalog_record = self._graph.value(subject=dataset_uri, predicate=rdflib.term.URIRef("http://xmlns.com/foaf/0.1/isPrimaryTopicOf"))
        if catalog_record:
            catalog = self._graph.value(subject=catalog_record, predicate=rdflib.term.URIRef("http://www.w3.org/ns/dcat#inCatalog"))
            return self.get_title(catalog)
        return None

    
    def get_dataset_contact_points(self, dataset_uri: rdflib.term.URIRef) -> rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        contact_point = self._graph.value(subject=dataset_uri, predicate= rdflib.term.URIRef("http://www.w3.org/ns/dcat#contactPoint"))
        contact = self._graph.value(subject=contact_point, predicate=rdflib.term.URIRef("http://www.w3.org/2006/vcard/ns#hasEmail"))
        return contact

    def get_dataset_spatial(self, dataset_uri: rdflib.term.URIRef) -> rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        spatials = []
        for _, _, object in self._graph.triples((dataset_uri, rdflib.term.URIRef("http://purl.org/dc/terms/spatial"), None)):
            # Saving only the INSEE URI
            if 'insee' in object:
                spatials.append(object)
        return spatials

    def get_dataset_licenses(self, dataset_uri: rdflib.term.URIRef) -> rdflib.term.Literal:
        assert type(dataset_uri) == rdflib.term.URIRef
        licenses = []
        for _, _, distribution in self._graph.triples((dataset_uri, rdflib.term.URIRef("http://www.w3.org/ns/dcat#distribution"), None)):
            licenses.append(self._graph.value(subject=distribution, predicate=rdflib.term.URIRef("http://purl.org/dc/terms/license")))
        try:
            return list(set(licenses))  # only keeping one occurence of each license
        except TypeError:
            return []

