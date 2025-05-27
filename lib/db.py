"""
Database connection and utilities for the skill-swap application.
"""
import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import glob

# Load environment variables
load_dotenv()

# Create a connection pool
connection_pool = None

def init_db():
    """Initialize the database connection pool."""
    global connection_pool
    if connection_pool is None:
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=os.getenv('DATABASE_URL')
        )
    return connection_pool

def get_connection():
    """Get a connection from the pool."""
    if connection_pool is None:
        init_db()
    return connection_pool.getconn()

def release_connection(conn):
    """Release a connection back to the pool."""
    if connection_pool is not None:
        connection_pool.putconn(conn)

def execute_query(query, params=None, fetch=False):
    """Execute a database query."""
    conn = get_connection()
    result = None
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        release_connection(conn)
    return result

def execute_script(script_path):
    """Execute a SQL script file."""
    conn = get_connection()
    try:
        with open(script_path, 'r') as f:
            script = f.read()
        with conn.cursor() as cur:
            cur.execute(script)
        conn.commit()
        print(f"Executed script: {script_path}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error executing script {script_path}: {e}")
        return False
    finally:
        release_connection(conn)

def run_migrations():
    """Run all migrations in order."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    migration_dir = os.path.join(base_dir, 'migrations')
    
    # Get all migration files in order
    migration_files = sorted(glob.glob(os.path.join(migration_dir, '*.sql')))
    
    for migration_file in migration_files:
        print(f"Running migration: {migration_file}")
        if not execute_script(migration_file):
            print(f"Migration failed: {migration_file}")
            return False
    
    return True

def run_seeds():
    """Run all seed files in order."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seed_dir = os.path.join(base_dir, 'seeds')
    
    # Get all seed files in order
    seed_files = sorted(glob.glob(os.path.join(seed_dir, '*.sql')))
    
    for seed_file in seed_files:
        print(f"Running seed: {seed_file}")
        if not execute_script(seed_file):
            print(f"Seed failed: {seed_file}")
            return False
    
    return True

def check_db_exists():
    """Check if the database exists and has the required tables."""
    try:
        result = execute_query(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')",
            fetch=True
        )
        return result[0][0] if result else False
    except Exception:
        return False
