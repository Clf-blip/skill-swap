"""
Utility functions for the skill-swap application.
"""
import re
import getpass
from datetime import datetime

def get_input(prompt, required=False, validator=None):
    """
    Get user input with validation.
    
    Args:
        prompt (str): The prompt to display to the user
        required (bool): Whether the input is required
        validator (callable, optional): A function to validate the input
        
    Returns:
        str: The validated input
    """
    while True:
        value = input(prompt).strip()
        
        if not value and not required:
            return value
            
        if not value and required:
            print("This field is required.")
            continue
            
        if validator and not validator(value):
            continue
            
        return value

def get_password(prompt="Password: ", confirm=False):
    """
    Get a password from the user securely.
    
    Args:
        prompt (str): The prompt to display
        confirm (bool): Whether to confirm the password
        
    Returns:
        str: The password
    """
    while True:
        password = getpass.getpass(prompt)
        
        if not password:
            print("Password is required.")
            continue
            
        if len(password) < 8:
            print("Password must be at least 8 characters.")
            continue
            
        if confirm:
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print("Passwords do not match.")
                continue
                
        return password

def validate_email(email):
    """
    Validate an email address.
    
    Args:
        email (str): The email to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        print("Invalid email address.")
        return False
    return True

def validate_username(username):
    """
    Validate a username.
    
    Args:
        username (str): The username to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if len(username) < 3:
        print("Username must be at least 3 characters.")
        return False
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        print("Username can only contain letters, numbers, underscores, and hyphens.")
        return False
        
    return True

def validate_datetime(time_str):
    """
    Validate a datetime string (YYYY-MM-DDTHH:MM).
    
    Args:
        time_str (str): The datetime string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
        return True
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DDTHH:MM")
        return False

def validate_integer(value, min_val=None, max_val=None):
    """
    Validate an integer.
    
    Args:
        value (str): The value to validate
        min_val (int, optional): The minimum allowed value
        max_val (int, optional): The maximum allowed value
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        num = int(value)
        
        if min_val is not None and num < min_val:
            print(f"Value must be at least {min_val}.")
            return False
            
        if max_val is not None and num > max_val:
            print(f"Value must be at most {max_val}.")
            return False
            
        return True
    except ValueError:
        print("Please enter a valid number.")
        return False

def format_datetime(dt):
    """
    Format a datetime object or string for display.
    
    Args:
        dt: The datetime to format (can be datetime object or string)
        
    Returns:
        str: The formatted datetime
    """
    if isinstance(dt, str):
        try:
            # Try to parse it as a datetime string
            dt_obj = parse_datetime(dt)
            return dt_obj.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            # If parsing fails, return the string as-is
            return dt
    elif dt:
        # If it's a datetime object, format it
        return dt.strftime("%Y-%m-%d %H:%M")
    return ""

def parse_datetime(dt_str):
    """
    Parse a datetime string.
    
    Args:
        dt_str (str): The datetime string to parse
        
    Returns:
        datetime: The parsed datetime
    """
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
