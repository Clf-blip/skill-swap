"""
Database connection and utilities for the skill-swap application.
"""
import os
import sqlite3
import glob
from dotenv import load_dotenv
from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command

# Load environment variables
load_dotenv()

# SQLite database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skill_swap.db')
ALEMBIC_INI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alembic.ini')

def init_db():
    """Initialize the database connection."""
    # Create SQLite database if it doesn't exist
    conn = sqlite3.connect(DB_PATH)
    conn.close()
    print(f"Connected to SQLite database at {DB_PATH}")
    return True

def get_connection():
    """Get a new SQLite connection."""
    return sqlite3.connect(DB_PATH)

def release_connection(conn):
    """Close a SQLite connection."""
    if conn:
        conn.close()

def execute_query(query, params=None, fetch=False):
    """Execute a database query."""
    conn = get_connection()
    result = None
    try:
        # Convert PostgreSQL placeholders (%s) to SQLite placeholders (?)
        query = query.replace('%s', '?')
        
        cur = conn.cursor()
        cur.execute(query, params or ())
        if fetch:
            result = cur.fetchall()
        conn.commit()
        cur.close()
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
            
        # Convert PostgreSQL-specific syntax to SQLite
        script = script.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        script = script.replace('TIMESTAMP', 'TEXT')
        script = script.replace('NOW()', "datetime('now')")
        script = script.replace(' CHECK ', ' ') # Simplified CHECK constraints
            
        cur = conn.cursor()
        # Split script into individual statements
        statements = script.split(';')
        for statement in statements:
            if statement.strip():
                cur.execute(statement)
        conn.commit()
        cur.close()
        print(f"Executed script: {script_path}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error executing script {script_path}: {e}")
        print(str(e))
        return False
    finally:
        release_connection(conn)

def run_migrations():
    """Run all migrations using Alembic."""
    try:
        # Load the Alembic configuration
        alembic_cfg = Config(ALEMBIC_INI)
        
        # Run the migrations
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully.")
        return True
    except Exception as e:
        print(f"Migration failed: {e}")
        return False
        
    # Legacy migration approach as fallback
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    migration_dir = os.path.join(base_dir, 'migrations')
    
    # Get all migration files in order
    migration_files = sorted(glob.glob(os.path.join(migration_dir, '*.sql')))
    
    for migration_file in migration_files:
        print(f"Running legacy migration: {migration_file}")
        if not execute_script(migration_file):
            print(f"Legacy migration failed: {migration_file}")
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
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'",
            fetch=True
        )
        return bool(result)
    except Exception:
        return False
