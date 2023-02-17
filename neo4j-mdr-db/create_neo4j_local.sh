#!/usr/bin/env bash
set -e
# Stop and remove neo4j_local if it already exists
if [ -n "$(docker ps -qa -f name=neo4j_local)" ]; then
	echo "- Found container neo4j_local"
	if [ -n "$(docker ps -q -f name=neo4j_local)" ]; then
		echo "- Stopping running container neo4j_local"
		docker stop neo4j_local
	fi
	echo "- Removing container neo4j_local"
	docker rm neo4j_local
fi

# Source env file
echo "- Reading environment variables from $(pwd)/.env"
source .env

# Look up working directory
WD="$(dirname "$(realpath "$0")")"
echo "- Workdir: $WD"

# Database storage directory
DATA="$WD/data"
# Plugins directory
PLUGINS="$WD/plugins"
# Import directory
IMPORT="$WD/import_files"
# Load scripts directory
SCRIPTS="$WD/load_scripts"
# Directories for database import and export
DB_IMPORT_DIR="$WD/db_import"
DB_EXPORT_DIR="$WD/db_export"

# User and Group
USER_AND_GROUP="$(id -u):$(id -g)"

# Make sure direcories exist
echo "- Creating directories to mount"
[ -d "$DATA" ] || mkdir -p "$DATA"
[ -d "$PLUGINS" ] || mkdir -p "$PLUGINS"
[ -d "$IMPORT" ] || mkdir -p "$IMPORT"
[ -d "$SCRIPTS" ] || mkdir -p "$SCRIPTS"
[ -d "$DB_IMPORT_DIR" ] || mkdir -p "$DB_IMPORT_DIR"
[ -d "$DB_EXPORT_DIR" ] || mkdir -p "$DB_EXPORT_DIR"

echo "- Creating and starting container neo4j_local"
docker run -d \
    --user="$USER_AND_GROUP" \
    --name neo4j_local \
    --ulimit nofile=10000:10000 \
    -p"$NEO4J_MDR_HTTP_PORT":"$NEO4J_MDR_HTTP_PORT" -p"$NEO4J_MDR_HTTPS_PORT":"$NEO4J_MDR_HTTPS_PORT" -p"$NEO4J_MDR_BOLT_PORT":"$NEO4J_MDR_BOLT_PORT" \
    -v "$DATA":/data \
    -v "$PLUGINS":/plugins \
    -v "$IMPORT":/var/lib/neo4j/import \
    -v "$SCRIPTS":/var/lib/neo4j/load_scripts \
    -v "$DB_IMPORT_DIR":/db_import \
    -v "$DB_EXPORT_DIR":/db_export \
    -v /etc/ssl/certs:/etc/ssl/certs \
    -e NEO4J_AUTH="$NEO4J_MDR_AUTH_USER"/"$NEO4J_MDR_AUTH_PASSWORD" \
    -e NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_trigger_enabled=true \
    -e NEO4J_dbms_memory_heap_max__size=2g \
    -e NEO4J_dbms_memory_pagecache_size=4g \
    -e NEO4J_dbms_allow__upgrade=true\
    -e NEO4J_dbms_max__databases=1000 \
    -e NEO4J_dbms_connector_bolt_advertised__address="$NEO4J_MDR_HOST":"$NEO4J_MDR_BOLT_PORT" \
    -e NEO4J_dbms_connector_http_advertised__address="$NEO4J_MDR_HOST":"$NEO4J_MDR_HTTP_PORT" \
    -e NEO4J_dbms_connector_https_advertised__address="$NEO4J_MDR_HOST":"$NEO4J_MDR_HTTPS_PORT" \
    -e NEO4J_dbms_connector_bolt_listen__address=:"$NEO4J_MDR_BOLT_PORT" \
    -e NEO4J_dbms_connector_http_listen__address=:"$NEO4J_MDR_HTTP_PORT" \
    -e NEO4J_dbms_connector_https_listen__address=:"$NEO4J_MDR_HTTPS_PORT" \
    -e NEO4J_metrics_enabled=false \
    --env=NEO4JLABS_PLUGINS='["apoc"]' \
    neo4j:4.4.12-enterprise
