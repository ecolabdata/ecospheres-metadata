# Chaîne de traitements des données

Cette chaîne de traitement fonctionne avec les services suivants, hébérgés dans un environnemnt Kubernetes :
1. MinIO (ou autre service compatible S3)
1. PostgreSQL
1. Metabase

## Mise à jour automatique

La mise à jour se fait grâce à un cronjob Kubernetes (défini par le fichier src/cronjob.yaml). Ce cronjob doit s'éxectuer au sein du réseau du SSPCloud (le service PostgreSQL est contraint dans ce réseau).

Afin de le créer :
1. Récupérer les variables d'environnement du service Metabase que vous voulez sauvegarder : -> Mes Services -> Metabase -> ℹ️ et s'en servir pour remplir les variables d'environnement du fichier `cronjob.yaml`
1. Lancer la commande `kubectl create -f src/cronjob.yaml` afin de démarrer le service de cronjob. Une fois lancé, celui-ci va exécuter le code à la fréquence renseignée (tous les jours : 0 0 * * * )
1. Il est ensuite possible de vérifier que le service Cronjob est bien actif avec la commande `kubectl get cronjobs`

## Mise à jour manuelle

Actuellement il n'est pas possible de réaliser toutes les étapes d'automatisation hors du réseau interne du SSPCloud.  Pour cela, il faudrait ouvrir sur internet le service Postgresql.
Les étapes **Extract** et **Transform** peuvent être exécutés, mais pas **Load**.

Afin de lancer ces deux scripts :
1. Renseigner les variables d'environnement dans un fichier .env
1. Lancer `python extract.py` qui lit le dump sur le S3 et en crée une version brute en csv.
1. Lancer `transform.py` qui va lire le fichier csv temporaire, le transformer et enregistrer une nouvelle version en csv.

## Sauvegarde et restauration de metabase

La sauvergarde des dashboard/questions faites sur metabase se fait via le Makefile du projet.

1. [Récupérer](https://datalab.sspcloud.fr/account/k8sCredentials) le script shell de connexion à Kubernetes sur la plateforme SSPCloud
1. Exécuter ce script dans un terminal
1. Exécuter `kubectl get pods` et noter le nom du pod de la base de données metabase (probablement : `metabase-db-0`). Ce nom permettra de remplir la variable d'environnement `KUBE_POD_NAME_REFORMAT` ou `KUBE_POD_NAME_REFORMAT`

### Sauvegarde

1. Récupérer les variables d'environnement du service Metabase que vous voulez sauvegarder : -> Mes Services -> Metabase -> ℹ️ et s'en servir pour remplir les variables d'environnement
    * `POSTGRES_DB= Valeur de <global.postgresql.auth.database>`
    * `POSTGRES_PASSWORD= Valeur de <global.postgresql.auth.password>`
    * `POSTGGRES_USER= Valeur de <global.postgresql.auth.username>`
1. Lancer `make backup_metabase_config` 

La sauvergarde se trouve dans le fichier `metabase.dump`

### Restauration/ Reformatage

> [!WARNING]  
> Le processus de restauration va reformater toute l'instance metabase ! Il est **fortement recommandé** d'utiliser une instance vide car toutes les données seront supprimées

1. S'assurer d'avoir un fichier `metabase.dump` dans le dossier des scripts.
1. Récupérer les variables d'environnement du service Metabase que vous voulez reformater avec les dashboard/questions sauvergardées  : -> Mes Services -> Metabase -> ℹ️ et s'en servir pour remplir les variables d'environnement
    `POSTGRES_DB= Valeur de <global.postgresql.auth.database>
     POSTGRES_PASSWORD= Valeur de <global.postgresql.auth.password>
     POSTGGRES_USER= Valeur de <global.postgresql.auth.username>`
1. Lancer `make restore_metabase_config` 


## Améliorations de la chaîne de traitement
* Lecture des variables d'environnement depuis le Vault