#!/bin/sh
echo "Waiting for database to be ready..."
until nc -z postgres_delivery 5432; do
  sleep 2
done
echo "Database is up! Running migrations..."
prisma db push
exec "$@"
