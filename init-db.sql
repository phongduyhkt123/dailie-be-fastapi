-- Initialize database for Dailee application
-- This file is executed when the PostgreSQL container starts for the first time

-- Create the main database (if not exists)
SELECT 'CREATE DATABASE dailee'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dailee')\gexec

-- Connect to the dailee database
\c dailee;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create initial tables (these will be managed by Alembic in production)
-- This is just for initial setup, actual schema will be created by migrations

-- You can add any initial data or setup scripts here
-- For example, creating initial admin user, default settings, etc.

-- Example: Create initial admin role (optional)
-- INSERT INTO users (email, hashed_password, is_active, is_admin) 
-- VALUES ('admin@dailee.com', '$2b$12$...', true, true) 
-- ON CONFLICT (email) DO NOTHING;
