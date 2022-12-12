#!/usr/bin/bash
set -e
if [ $# -lt 3 ]; then
	cat 1>&2 <<- EOF
		Error: not enough arguments
		Example usage, connects to the container 'database' and imports the backup data in cdiscdata.tar.gz into the database 'mdrdb'.
		$ ./import_db_backup.sh database mdrdb cdiscdata.tar.gz
		This script assumes that the directory 'db_import' exists in the same directory as itself,
		and that this directory is mounted at /db_import in the container.
	EOF
	exit 2
fi

# Look up working directory
WD="$(dirname "$(realpath "$0")")"
echo "- Workdir: $WD"

echo "- Checking for database alias"
DBNAME=$(docker exec "$1" /var/lib/neo4j/bin/cypher-shell -d system -u "$NEO4J_MDR_AUTH_USER" -p "$NEO4J_MDR_AUTH_PASSWORD" -a "neo4j://localhost:$NEO4J_MDR_BOLT_PORT" "SHOW ALIASES FOR DATABASE YIELD * WHERE name=\"$2\" RETURN database" | tail -n 1 | tr -d '"')
if [ -z "$DBNAME" ]
then
	DBNAME="$2"
else
	echo "$2 is an alias for database $DBNAME"
fi

echo "- Checking that database $DBNAME exists"
DBLISTING=$(docker exec "$1" /var/lib/neo4j/bin/cypher-shell -d system -u "$NEO4J_MDR_AUTH_USER" -p "$NEO4J_MDR_AUTH_PASSWORD" -a "neo4j://localhost:$NEO4J_MDR_BOLT_PORT" "SHOW DATABASE \`$DBNAME\` YIELD *")
if [ -z "$DBLISTING" ]
then
	echo "Error, database $DBNAME does not exist"
	exit 1
fi

echo "- Prepare import directory, deleting any conflicting files"
if [ -d "$WD/db_import/$DBNAME" ]; then
	echo "  Deleting existing export directory $WD/db_import/$DBNAME"
	rm -rf "$WD/db_import/$DBNAME"
fi
mkdir "$WD/db_import/$DBNAME"
tar -xf "$3" -C "$WD/db_import/$DBNAME/"

echo "- Stop database"
docker exec "$1" /var/lib/neo4j/bin/cypher-shell -d system -u "$NEO4J_MDR_AUTH_USER" -p "$NEO4J_MDR_AUTH_PASSWORD" -a "neo4j://localhost:$NEO4J_MDR_BOLT_PORT" "STOP DATABASE \`$DBNAME\`;"
echo "- Restore backup"
docker exec "$1" /var/lib/neo4j/bin/neo4j-admin restore --from=/db_import/$DBNAME --database="$DBNAME" --force
echo "- Ensure service user owns add database files"
DB_USER_AND_GROUP=$(docker exec "$1" stat -c "%u:%g" /data/databases)
echo "  Database service runs as user:group $DB_USER_AND_GROUP"
docker exec --user root "$1" chown -R "$DB_USER_AND_GROUP" /data
echo "- Create database if not already existing"
docker exec "$1" /var/lib/neo4j/bin/cypher-shell -d system -u "$NEO4J_MDR_AUTH_USER" -p "$NEO4J_MDR_AUTH_PASSWORD" -a "neo4j://localhost:$NEO4J_MDR_BOLT_PORT" "CREATE DATABASE \`$DBNAME\` IF NOT EXISTS;"
echo "- Start database"
docker exec "$1" /var/lib/neo4j/bin/cypher-shell -d system -u "$NEO4J_MDR_AUTH_USER" -p "$NEO4J_MDR_AUTH_PASSWORD" -a "neo4j://localhost:$NEO4J_MDR_BOLT_PORT" "START DATABASE \`$DBNAME\`;"
echo "- List existing databases"
docker exec "$1" /var/lib/neo4j/bin/cypher-shell -d system -u "$NEO4J_MDR_AUTH_USER" -p "$NEO4J_MDR_AUTH_PASSWORD" -a "neo4j://localhost:$NEO4J_MDR_BOLT_PORT" "SHOW DATABASES;"
