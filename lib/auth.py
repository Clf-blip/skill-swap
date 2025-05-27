"""
Authentication and session management for the skill-swap application.
"""
import bcrypt
import os
import json
from . import db
from . import utils

# Session file path
SESSION_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.session')

# Global session storage
current_session = None

class Session:
    """Session class to store user authentication details."""
    def __init__(self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email
        
    def to_dict(self):
        """Convert session to dictionary for serialization."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create session from dictionary."""
        if not data:
            return None
        return cls(data['user_id'], data['username'], data['email'])

def save_session(session):
    """Save session to file."""
    if session:
        with open(SESSION_FILE, 'w') as f:
            json.dump(session.to_dict(), f)
    else:
        # Remove session file if session is None
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

def load_session():
    """Load session from file."""
    global current_session
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
            current_session = Session.from_dict(data)
        except Exception:
            # If there's an error loading the session, remove the file
            os.remove(SESSION_FILE)
            current_session = None
    else:
        current_session = None

def login(username, password):
    """
    Authenticate a user and create a session.
    
    Args:
        username (str): The username to authenticate
        password (str): The password to check
        
    Returns:
        bool: True if login successful, False otherwise
    """
    global current_session
    
    # Query for the user
    result = db.execute_query(
        "SELECT id, username, email, password_hash FROM users WHERE username = %s AND deleted_at IS NULL",
        (username,),
        fetch=True
    )
    
    if not result:
        print("Invalid username or password.")
        return False
    
    user_id, db_username, email, password_hash = result[0]
    
    # Check password
    if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        print("Invalid username or password.")
        return False
    
    # Create session
    current_session = Session(user_id, db_username, email)
    # Save session to file
    save_session(current_session)
    print(f"Welcome back, {db_username}!")
    return True

def register(username, email, password, full_name=None, bio=None):
    """
    Register a new user.
    
    Args:
        username (str): The username for the new user
        email (str): The email for the new user
        password (str): The password for the new user
        full_name (str, optional): The full name of the user
        bio (str, optional): The bio of the user
        
    Returns:
        bool: True if registration successful, False otherwise
    """
    # Check if username or email already exists
    result = db.execute_query(
        "SELECT username FROM users WHERE username = %s OR email = %s",
        (username, email),
        fetch=True
    )
    
    if result:
        print("Username or email already exists.")
        return False
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Insert the new user
    try:
        db.execute_query(
            """
            INSERT INTO users (username, email, password_hash, full_name, bio)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (username, email, password_hash, full_name, bio)
        )
        print(f"User '{username}' registered successfully!")
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        return False

def logout():
    """Log out the current user."""
    global current_session
    if current_session:
        print(f"Goodbye, {current_session.username}!")
        current_session = None
        # Remove session file
        save_session(None)
        return True
    return False

def get_current_user():
    """Get the current user session."""
    global current_session
    if current_session is None:
        # Try to load session from file
        load_session()
    return current_session

def require_login(func):
    """Decorator to require login for a function."""
    def wrapper(*args, **kwargs):
        global current_session
        if current_session is None:
            # Try to load session from file before rejecting
            load_session()
            if current_session is None:
                print("You must be logged in to use this command.")
                return False
        return func(*args, **kwargs)
    return wrapper
