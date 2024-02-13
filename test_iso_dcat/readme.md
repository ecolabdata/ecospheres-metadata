Dossier pour comparaison de sortie ISO et mapping résultant de [la conversion XSLT vers GeoDCAT-AP de la commissione européenne](https://geodcat-ap.semic.eu/api/).

Pour chaque exemple, le fichier .xml est la sortie CSW ISO, tandis que le fichier .ttl est la sortie après mapping vers GeoDCAT-AP.

## Précisions

### NatureFrance

La sortie NatureFrance utilisée est la suivante : https://data.naturefrance.fr/geonetwork/srv/fre/csw?SERVICE=CSW&VERSION=2.0.2&REQUEST=GetRecordById&outputSchema=http://www.isotc211.org/2005/gmd&typenames=gmd:MD_Metadata&elementSetName=full&resultType=results&startPosition=1&Id=f00ce900-4381-4be2-aed5-991208499b79.
Le mapping de l'export CSW ISO échoue sur les fiches de NatureFrance. Aucun Dataset n'est retourné lors de la conversion.

