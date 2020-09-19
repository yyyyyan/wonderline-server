# You may add some other conditionals that fits your stuation here
sleep 20
until cqlsh -f /docker-entrypoint-initdb.d/init_1_schema.cql; do
  echo "cqlsh: Cassandra is unavailable to initialize - will retry later"
  sleep 10
done &

until cqlsh -f /docker-entrypoint-initdb.d/init_2_mock_data.cql; do
  echo "cqlsh: Cassandra is unavailable to initialize - will retry later"
  sleep 10
done &

exec /docker-entrypoint.sh "$@"