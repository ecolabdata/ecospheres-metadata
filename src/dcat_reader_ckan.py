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

def split_geo_levels(insee_uris: list, geo_level: str) -> str:
    """
    Filter a list of INSEE URI to a specific geographical zoom level
    Attribute zoom_level can be 'commune' or 'departement'

    Returns a string in which the different elements of the same zoom are seperated by a ','
    """
    geos_elements = []
    for insee_uri in insee_uris:
        if geo_level in insee_uri:
            geos_elements.append(str(insee_uri.split(f'{geo_level}/')[1]))
    if len(geos_elements) >= 1:
        return ','.join(geos_elements)
    else:
        return None


def define_geo_coverage(insee_uris: list) -> str:
    """
    Map a list or INSEE URI to a spatial coverage : 'departemental' or 'intra-departemental'
    """
    communes = 0
    departements = 0
    for insee_uri in insee_uris:
        if 'commune' in insee_uri:
            communes += 1
        elif 'departement' in insee_uri:
            departements += 1
    if communes >= 1:
        return 'Communale'
    elif departements >= 1:
        return 'Départementale'
    else:
        return None

        
class DatasetReader():

    def __init__(self, graph_src: bytes, format='json-ld'):
        self.graph_src = graph_src
        self.format = format
        self._graph = rdflib.Graph().parse(data=self.graph_src, format='json-ld')

        self.pattern_open_access = [
            "pas de restriction d'accès public selon inspire",
            "licence ouverte",
            "open licence",
        ]
    
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
        df = pd.DataFrame(data)
        
        # Split spatial attribute into different geographical zooms
        if 'spatial' in df.columns:
            df['commune'] = df['spatial'].apply(lambda x: split_geo_levels(x, 'commune'))
            df['departement'] = df['spatial'].apply(lambda x: split_geo_levels(x, 'departement'))
            df['departement'] = df.apply(lambda row: row['departement'] if not row['commune'] else None, axis=1) 

            df['geo_coverage'] = df['spatial'].apply(define_geo_coverage)

            del df['spatial']
        if 'right_statement' in df.columns:
            df["right_statement_processed"] = df["right_statement"].apply(lambda x: any(label in x.lower().replace('\n', ' ') for label in self.pattern_open_access))
        return df
        
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
        return ' '.join(rigth_statements)
        
    def get_dataset_themes(self, dataset_uri: rdflib.term.URIRef) -> str:
        """ Returns a joined string of available key words. 
        """
        assert type(dataset_uri) == rdflib.term.URIRef
        themes = []
        for _, _, object in self._graph.triples((dataset_uri,rdflib.term.URIRef("http://www.w3.org/ns/dcat#theme"), None)):
            themes.append(object)
        return ' '.join(themes)
    
    def get_dataset_key_words(self, dataset_uri: rdflib.term.URIRef) ->str:
        """ Returns a joined string of available key words. 
        """
        assert type(dataset_uri) == rdflib.term.URIRef
        key_words = []
        for _, _, object in self._graph.triples((dataset_uri, rdflib.term.URIRef("http://www.w3.org/ns/dcat#keyword"), None)):
            key_words.append(object)
        return ' '.join(key_words)

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
        if licenses:
            return list(set(licenses))  # only keeping one occurence of each license
        else :
            return None

