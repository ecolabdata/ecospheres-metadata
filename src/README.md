# Actions qualité Ecosphères

Ce dossier contient les ressources utilisées pour générer [la visualisation d'indicateurs de qualité des métadonnées Ecosphères](https://projet-ecolab-action-qualite-702963.user.lab.sspcloud.fr/dashboard/1-ecospheres-actions-qualite).

Celle-ci a été conçue et documentée de telle façon à pouvoir être reprise, modifiée et redéployée le plus simplement possible avec des briques logicielles et servicielles standards.

## Chaîne de traitements des données

La chaîne de traitement prend en entrée les fichiers sources stockés sur MinIO, et donne en sortie une base de données PostgreSQL, elle-même requêtée par Metabase. Ces différents services sont hébergés dans un environnement Kubernetes et managés sur l'infrastructure [SSP Cloud](https://www.sspcloud.fr/).

Les services suivants sont à instancier dans le SSP Cloud pour pouvoir exécuter la chaîne de traitement et la visualisation :
1. *MinIO (existe par défaut dans le SSP Cloud)*
1. Postgres 
1. Jupyter (pour un lancement manue uniquement)
1. Metabase 

### Fichiers sources

Les fichiers sources sont une extraction ("dump") de l'exposition DCAT du [catalogue CKAN Ecosphères](https://preprod.data.developpement-durable.gouv.fr/) au format JSON, déposés manuellement sur l'espace de stockage MinIO (ou tout service de stockage d'objets compatible S3).

### Variables d'environnement
La chaîne de traitement a besoin des accès à Postgres et au service MinIO. Pour cela, il faut renseigner les variables d'environnement dans le fichier `src/.env` (gestion manuelle) ou dans le fichier `src/cronjob.yaml` (gestion automatique).
Vous pouvez les retrouvez ou créer :
* Pour Metabase : -> Mes Services -> Metabase -> ℹ️ (bouton information) 
* Pour MinIO : il faut créer ou récupérer un [compte de service](https://minio-console.lab.sspcloud.fr/login) (vous ne pouvez pas utiliser les identifiants personnels MinIO pour le moment). Ce compte de service permet d'avoir des indentifiants spécifiques, configurables et qui se mettent à jour à une fréquence choisie. Si le compte n'existe pas à cette adresse https://minio-console.lab.sspcloud.fr/access-keys, vous pouvez en créer un. Après avoir cliqué sur `Create acess key`, l'application propose un compte. Il faut alors valider l'option `Restrict beyond user policy`, et renseigner une configuration permettant de se connecter à l'espace de travail, comme dans cet exemple pour l'environnement de travail **projet-ecolab-action-qualite** :
``` json
{
 "Version": "2012-10-17",
 "Statement": [
  {
   "Effect": "Allow",
   "Action": [
    "s3:*"
   ],
   "Resource": [
    "arn:aws:s3:::projet-ecolab-action-qualite",
    "arn:aws:s3:::projet-ecolab-action-qualite/*"
   ]
  }
 ]
}
```


### Mise à jour automatique

La mise à jour se fait grâce à un cronjob Kubernetes (défini par le fichier src/cronjob.yaml). Ce cronjob doit s'éxectuer au sein du réseau du SSPCloud (le service PostgreSQL est contraint dans ce réseau).

Afin de le créer :

1. S'assurer d'avoir toutes les variables d'environnement renseignées (voir au dessus) dans le fichier `src/cronjob.yaml`
1. Lancer la commande `kubectl apply -f src/cronjob.yaml` afin de démarrer le service de cronjob. Une fois lancé, celui-ci va exécuter le code à la fréquence renseignée (tous les jours : 0 0 \* \* \* )
1. Il est ensuite possible de vérifier que le service Cronjob est bien actif avec la commande `kubectl get cronjobs`

### Mise à jour manuelle

#### Au sein du SSP Cloud


1. Démarrer un [service jupyter](https://datalab.sspcloud.fr/launcher/ide/jupyter-python?version=1.13.22) dans le projet 'projet-ecolab-action-qualite' sur le SSPCloud
1. S'assurer d'avoir toutes les variables d'environnement renseignées (voir au dessus) dans le fichier `src/.env`
1. Executer `pip install -r requirements.txt'
1. Ouvrir le notebook `src/etl.ipynb` et exécuter la brique ETL

#### En local

Actuellement il n'est pas possible de réaliser toutes les étapes d'automatisation hors du réseau interne du SSPCloud. Pour cela, il faudrait ouvrir sur internet le service Postgresql.
Les étapes **Extract** et **Transform** peuvent être exécutés, mais pas **Load**.

Afin de lancer ces deux scripts :

1. Renseigner les variables d'environnement dans un fichier .env
2. Lancer `python extract.py` qui lit le dump sur le S3 et en crée une version brute en csv.
3. Lancer `transform.py` qui va lire le fichier csv temporaire, le transformer et enregistrer une nouvelle version en csv.

### Sauvegarde et restauration de metabase

La sauvergarde des dashboard/questions faites sur metabase se fait via le Makefile du projet.

1. [Récupérer](https://datalab.sspcloud.fr/account/k8sCredentials) le script shell de connexion à Kubernetes sur la plateforme SSPCloud
2. Exécuter ce script dans un terminal
3. Exécuter `kubectl get pods` et noter le nom du pod de la base de données metabase (probablement : `metabase-db-0`). Ce nom permettra de remplir la variable d'environnement `KUBE_POD_NAME_REFORMAT` ou `KUBE_POD_NAME_REFORMAT`

#### Sauvegarde

1. Récupérer les variables d'environnement du service Metabase que vous voulez sauvegarder : -> Mes Services -> Metabase -> ℹ️ et s'en servir pour remplir les variables d'environnement
   - `POSTGRES_DB= Valeur de <global.postgresql.auth.database>`
   - `POSTGRES_PASSWORD= Valeur de <global.postgresql.auth.password>`
   - `POSTGGRES_USER= Valeur de <global.postgresql.auth.username>`
2. Lancer `make backup_metabase_config`

La sauvegarde se trouve dans le fichier `metabase.dump`

#### Restauration / Reformatage

> [!WARNING]  
> Le processus de restauration va reformater toute l'instance metabase ! Il est **fortement recommandé** d'utiliser une instance vide car toutes les données seront supprimées

1. S'assurer d'avoir un fichier `metabase.dump` dans le dossier des scripts.
2. Récupérer les variables d'environnement du service Metabase que vous voulez reformater avec les dashboard/questions sauvergardées : -> Mes Services -> Metabase -> ℹ️ (bouton information) et s'en servir pour remplir les variables d'environnement
   `POSTGRES_DB= Valeur de <global.postgresql.auth.database>
 POSTGRES_PASSWORD= Valeur de <global.postgresql.auth.password>
 POSTGGRES_USER= Valeur de <global.postgresql.auth.username>`
3. Lancer `make restore_metabase_config`

### Améliorations de la chaîne de traitement

- Lecture des variables d'environnement depuis le Vault
