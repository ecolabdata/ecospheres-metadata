# Description des Métadonnées dans Ecosphères

## Enjeux

Le catalogue Ecosphères a pour vocation de faciliter l'identification sur chaque territoire des données utiles à l'appui des politiques publiques (diagnostic, planificaiton, suivi). Dans le cadre de ces observations, nous nous intéressons au potentiel de priorisation des données remontées lors d'une recherche à partir des métadonnées disponibles au regard de critères thématiques, géographiques, temporels, d'accès à la donnée et enfin de fiabilité. Nous nous appuierons sur une sélection de métadonnées parmi les champs décrits dans des documents de références tels que la documentation du profile [GeoDCAT-AP](https://semiceu.github.io/GeoDCAT-AP/releases/) et le guide de saisie des éléments de métadonnées [INSPIRE](https://semiceu.github.io/GeoDCAT-AP/releases/).

Les métadonnées recueillies par le POC CKAN Ecosphères à partir des [points de moissonnage](https://github.com/ecolabdata/guichetdonnees-public/blob/main/moissonnages.json) sont à la base de ces observations. Les métadonnées sur les jeux de données sont entreposés dans les tables `package` et `package_extra` de la [base de données CKAN](https://boykoc.github.io/ckan/2019/10/21/ckan-283-database-diagram.html), également disponibles par API suivant le [schéma Ecosphères](https://github.com/ecolabdata/ckanext-ecospheres/blob/main/ckanext/ecospheres/scheming/ecospheres_dataset_schema.yaml) DCAT compatible.

Nous tâcherons d'évaluer en quoi la qualité des métadonnées disponibles ainsi que les fonctionnalités de requête des plateformes impactent la découverte des données mais également la capacité de maintenir un ensemble de jeux de données (actualisation, suivi de l'interopérabilité, enrichissement). Enfin, au-delà des seules considérations sur la découvrabilité, nous nous intéresserons à des problématiques propres aux moissonnages telles que l'identification a posteriori de doublons, de données obsolètes ou encore la sensibilité du périmètre des jeux de données moissonnés aux paramètres des filtres CSW.

## Rapport HTML

L'observation des métadonnées est réalisée à partir de notebooks Jupyter. Préalablement à l'execution de ces derniers, il est nécessaire de renseigner le fichier `config.ini` avec les informations relatives à la base de données requêtée. L'analyse est subdivisée en notebooks indépendants dont le nom doit commencer par une chaîne de caractères à deux chiffres. Par la suite, la commande `python -m merge` en permet la fusion par ordre numérique croissant et convertit sous forme HTML une version slide des cellules à partir du module [nbconvert](https://nbconvert.readthedocs.io/en/latest/). Pour toute cellule, il est nécessaire de renseigner la métadonnée `slide_type` suivant le souhait d'afficher la cellulle comme slide, sous-slide, fragment ou encore de l'ignorer.

Dans cette phase exploratoire, par rapport à des outils de visualisation tels qu'Apache Superset, cette approche tire profit de la flexibilité des librairies Python pour le traitement des données et de l'ergonomie des notebooks pour documenter la démarche tout en permettant la visualisation des résultats sous forme de diagrammes interactifs.

## Commit

Lors d'un commit, certains notebooks pouvant être trop volumineux, il peut être nécessaire d'effacer les résultats obtenus après execution des cellules.

## Investigation

H : Hypothèse ; Q : Question

*H : En complément de la barre de recherche, l'activation de filtres tels que ceux disponibles sur les catalogues Ecosphères ou data.gouv est suffisante pour identifier les jeux de données utiles.*  
Cette hypothèse est à rapprocher des taux de remplissage et du caractère discriminant des métadonnées associées à ces filtres, du niveau d'adéquation entre ces filtres et les critères de recherches exprimés par les utilisateurs, du nombre de données remontées à l'issue d'une recherche multicritère et de leur priorisation. Evaluer l'apport des *Large Language Model (LLM)* au regard des questions soulevées par cette hypothèse.

*H : Un aperçu du patrimoine des données disponibles sur chaque territoire est limité par le trop grand nombre de données qui y sont associées.*
En se focalisant sur la maille départementale, il s'agit de visualiser la distribution du nombre de données par territoire.

*H : A l'issu du moissonnage, les jeux de données collectés en doublon constituent une minorité et n'affectent pas la recherche.*  
Comptabiliser le nombre de doublons.

*Q : Dans quelle mesure les vocabulaires contrôlés facilitent-il la découvrabilité d'un jeu de données ?*  
Lien entre vocabulaires contrôlés, filtres et indexations par le moteur de recherche.

*Q : Quelle est la part des jeux de données associés à un document de référence (PLU, SUP, PPR, etc.) ?*

*Q : Quels critères permettraient d'affirmer qu'une donnée est obsolète ?*  

*Q : Suivant quels critères serait-il possible de caractériser l'efficacité d'une recherche (nombre de clicks utilisateurs, complexité algorithmique, etc.) ?*

*Q : Quelle est la part des données restreintes ?*

## Métadonnées dans Ecosphères

Métadonnées et vocabulaires contrôlés dans Ecosphères (list non exhaustive, [voir schéma complet](https://github.com/ecolabdata/ckanext-ecospheres/blob/main/ckanext/ecospheres/scheming/ecospheres_dataset_schema.yaml)).

|            |Métadonnées[CKAN] | Vocabulaires Contrôlés | Definition |
|:--                 |:--          |:--                     |:--                     |
|**Métadonnées thématiques** | title | | Libellé du jeu de données. |
|                     | notes | | Description du jeu de données. |
|                     | category | ecospheres_themes | Thèmes (et sous-thèmes) de la nomenclature du guichet, déduit de "theme", "subject" et "free_tag" lors du moissonnage, stockage sous forme d'une liste d'URI (appartenant au registre du guichet). |
|                     | theme | inspire_theme, inspire_topic_category, eu_theme | Thèmes des nomemclatures externes, notamment celle de la commission européenne et la nomenclature INSPIRE, mapper dct:subject vers cette propriété (utilisé dans GeoDCAT-AP v2 pour les catégories ISO), stockage sous la forme d'une liste d'URI.
|                     | free_tags | | Mots-clés libres. |
|                     | attribute_pages | | Lien de la page où sont décrits les champs du jeu de données. |
|**Métadonnées géographiques**| bbox | | Rectangle d'emprise. Stockage et exposition sous forme de littéral GML ou WKT, comme il convient pour cette propriété, calculé à partir de "spatial" pour les métadonnées INSPIRE |
|                       | crs | | Pour les référentiels de coordonnées, stockage et exposition sous forme d'une liste d'URI, affichage de l'étiquette, récupérée en interrogeant l'URI. |
|                       | spatial_coverage | | Couverture géographique, territoires sur lesquels portent les données, le champ "uri" correspond à l'objet du triplet <...> dct:spatial <uri>, s'il n'est pas défini, l'exposition utilise un noeud anonyme de classe dct:Location  |
|                       | spatial | | Rectangle d'emprise, utilisé par ckanext-spatial pour la prévisualisation cartographique, non exposé en DCAT, stockage sous la forme d'un dump GeoJSON (cf. http://docs.ckan.org/projects/ckanext-spatial/en/latest/spatial-search.html#geo-indexing-your-datasets), calculé à partir de "bbox" (propriété de "spatial_coverage") pour, les métadonnées DCAT.
|                       | territory | | Divisions administratives (régions, départements...) présumées couvertes par les données, non repris dans l'export DCAT (hormis pour les   informations mappées depuis la propriété "spatial"), utilisé uniquement pour le filtrage par territoire, déduit de "spatial" si possible, à défaut du territoire de compétence de l'organisation, stockage sous la forme d'une liste d'URI. |
|                       | spatial_resolution | | Plus petite distance significative dans le contexte du jeu de données, exprimée en mètres. |
|                       | equivalent_scale | | Non exposé, permet uniquement de conserver cette information présente dans les métadonnées INSPIRE et sur la base de laquelle "spatial_resolution" est calculé. |
|**Métadonnées temporelles**| temporal | | Périodes décrites par le jeu de données.|
|                     | modified | | Date de dernière modification du jeu de données. |
|                     | created | | Date de création du jeu de données. |
|                     | issued | | Date de publication du jeu de données. |
|                     | accrual_periodicity | inspire_maintenance_frequency, eu_frequency | Fréquence de mise à jour, stockage et exposition sous forme d'URI, affichage de l'étiquette récupérée par interrogation de l'URI. |
|                     | temporal_resolution || Plus petit pas de temps significatif dans le contexte du jeu de données, stockage et exposition sous forme standardisée (ex: 'P2HT30M' pour 2h30). |
|**Accès et utilisation**| restricted_access | | Donnée à accès restreint, non exposé dans l'export DCAT, utilisé pour l'élément "Données ouvertes / Accès restreint", booléen déduit de access_rights. |
|                     | access_rigths | | Contraintes réglementaires limitant l'accès au jeu de données. |
|                     | rights_holder | | Organisme ou personne qui détient des droits sur les données. |
|                     | conforms_to | plume_data_service_standard | Standard, schéma, etc. auquel se conforment les données. |
|                     | license | eu_licence, spdx_license, adms_licence_type | Calculé à partir des champs "license" des ressources. Champs CKAN hors DCAT. |
|                     | status | eu_dataset_status, adms_status, iso19139_progress_code | Maturité, stockage et exposition sous forme d'URI, affichage de l'étiquette récupérée par interrogation de l'URI. |
|**Généalogie**| contact_point | | Entité à contacter pour obtenir des informations sur les données.|
|                     | publisher | | Organisme ou personne qui assure la publication des données. |
|                     | creator | | Principal responsable de la production des données. |
|                     | qualified_attribution |  | Organisme qui est intervenu ou exerce une responsabilité sur les données. |
|                     | version |  | Version ou millésime du jeu de données. |
|                     | version_notes |  | Différences entre la version courante des données et les versions antérieures. |
|                     | provenance |  | Informations sur les sources et méthodes de production des données. |