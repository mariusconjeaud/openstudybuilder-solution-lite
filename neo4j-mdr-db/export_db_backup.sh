#!/usr/bin/bash
set -e
if [ $# -lt 3 ]; then
	cat 1>&2 <<- EOF
		Error: not enough arguments
		Example usage, connects to the container 'database' and exports the database 'mdrdb' to the file ./my_mackup.tar.gz.
		$ ./backup_db.sh database mdrdb my_backup.tar.gz
		This script assumes that the directory 'db_export' exists in the same directory as itself,
		and that this directory is mounted at /db_export in the container.
	EOF
	exit 2
fi

# Look up working directory
WD="$(dirname "$(realpath "$0")")"
echo "- Workdir: $WD"

echo "- Clean up export directory, delete any conflicting files"
if [ -f "$WD/$3" ]; then
	echo "  Deleting existing archive $WD/$3"
	rm "$WD/$3"
fi
if [ -d "$WD/db_export/$2" ]; then
	echo "  Deleting existing export directory $WD/db_export/$2"
	rm -rf "$WD/db_export/$2"
fi
mkdir "$WD/db_export/$2"

echo "- List existing databases"
docker exec "$1" /var/lib/neo4j/bin/cypher-shell -d system -u "$NEO4J_MDR_AUTH_USER" -p "$NEO4J_MDR_AUTH_PASSWORD" -a "neo4j://localhost:$NEO4J_MDR_BOLT_PORT" "SHOW DATABASES;"

echo "- Perform backup"
docker exec "$1" /var/lib/neo4j/bin/neo4j-admin backup --backup-dir=/db_export --database="$2"

echo "- Compress backup files"
cd "$WD/db_export/$2"
tar -czf "$WD/$3" *