#!/bin/bash

# Variables for metabase reformat
# All variables should be filled
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_DB="metabase-metadata"
POSTGRES_USER=""
POSTGRES_PASSWORD=""
BACKUP_FILE="./metabase.dump"

# -> kubectl get pods
KUBE_POD_NAME_REFORMAT="metabase-db-0" 

kubectl cp $(BACKUP_FILE) $(strip $(KUBE_POD_NAME_REFORMAT)):/tmp/backup.dump
kubectl exec $(KUBE_POD_NAME_REFORMAT) -- env PGPASSWORD=${POSTGRES_PASSWORD} pg_restore -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -d $(POSTGRES_DB) -U $(POSTGRES_USER) -c -v /tmp/backup.dump
kubectl exec $(KUBE_POD_NAME_REFORMAT) -- rm /tmp/backup.dump