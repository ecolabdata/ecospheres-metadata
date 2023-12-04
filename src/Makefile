.PHONY: dump-data

# Variables
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_DB="metabase-metadata"
POSTGRES_USER=""
POSTGRES_PASSWORD=""
BACKUP_FILE="./metabase.dump"

# -> kubectl get pods
KUBE_POD_NAME="metabase-db-0" 


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk -F ":" '{print $$2 ":" $$3}' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

backup_metabase_config:
	kubectl exec $(KUBE_POD_NAME) -- env PGPASSWORD=${POSTGRES_PASSWORD} pg_dump -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -d $(POSTGRES_DB) -U $(POSTGRES_USER) -Fc -f /tmp/backup.dump
	kubectl cp $(strip $(KUBE_POD_NAME)):/tmp/backup.dump $(BACKUP_FILE)
	kubectl exec $(KUBE_POD_NAME) -- rm /tmp/backup.dump


restore-metabase-config:
	kubectl cp $(BACKUP_FILE) $(strip $(KUBE_POD_NAME)):/tmp/backup.dump
	kubectl exec $(KUBE_POD_NAME) -- env PGPASSWORD=${POSTGRES_PASSWORD} pg_restore -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -d $(POSTGRES_DB) -U $(POSTGRES_USER) -c -v /tmp/backup.dump
	kubectl exec $(KUBE_POD_NAME) -- rm /tmp/backup.dump
