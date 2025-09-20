-- Initialize database with required user and database
CREATE USER root WITH PASSWORD 'Babyna3*.';
ALTER USER root SUPERUSER;
CREATE DATABASE fpl OWNER root;
GRANT ALL PRIVILEGES ON DATABASE fpl TO root;



