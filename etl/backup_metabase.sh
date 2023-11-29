#!/bin/bash

# Variables for metabase backup
# All variables should be filled
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_DB="metabase-metadata"
POSTGRES_USER=""
POSTGRES_PASSWORD=""
BACKUP_FILE="./metabase.dump"

# kubectl get pods
KUBE_POD_NAME_BACKUP="metabase-db-0" 

kubectl exec $(KUBE_POD_NAME_BACKUP) -- env PGPASSWORD=${POSTGRES_PASSWORD} pg_dump -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -d $(POSTGRES_DB) -U $(POSTGRES_USER) -Fc -f /tmp/backup.dump
kubectl cp $(strip $(KUBE_POD_NAME_BACKUP)):/tmp/backup.dump $(BACKUP_FILE)
kubectl exec $(KUBE_POD_NAME_BACKUP) -- rm /tmp/backup.dump
