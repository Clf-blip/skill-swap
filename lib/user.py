"""
User management commands for the skill-swap application.
"""
from tabulate import tabulate
from . import db
from . import auth
from . import utils

def register_user():
    """Register a new user."""
    print("\n=== User Registration ===")
    
    # Get user details with validation
    username = utils.get_input("Username: ", required=True, validator=utils.validate_username)
    email = utils.get_input("Email: ", required=True, validator=utils.validate_email)
    password = utils.get_password(confirm=True)
    full_name = utils.get_input("Full Name: ")
    bio = utils.get_input("Bio: ")
    
    # Register the user
    return auth.register(username, email, password, full_name, bio)

def login_user():
    """Login a user."""
    print("\n=== User Login ===")
    
    username = utils.get_input("Username: ", required=True)
    password = utils.get_password()
    
    return auth.login(username, password)

@auth.require_login
def list_users():
    """List all users."""
    users = db.execute_query(
        """
        SELECT id, username, email, full_name, bio
        FROM users
        WHERE deleted_at IS NULL
        ORDER BY id
        """,
        fetch=True
    )
    
    if not users:
        print("No users found.")
        return
    
    # Format users for display
    headers = ["ID", "Username", "Email", "Full Name", "Bio"]
    rows = [[u[0], u[1], u[2], u[3] or '', (u[4] or '')[:50]] for u in users]
    
    print("\n=== Users ===")
    print(tabulate(rows, headers=headers, tablefmt="simple"))

@auth.require_login
def view_user(user_id):
    """
    View a user's details.
    
    Args:
        user_id (int): The ID of the user to view
    """
    # Get user details
    user = db.execute_query(
        """
        SELECT u.id, u.username, u.email, u.full_name, u.bio
        FROM users u
        WHERE u.id = %s AND u.deleted_at IS NULL
        """,
        (user_id,),
        fetch=True
    )
    
    if not user:
        print(f"User with ID {user_id} not found.")
        return
    
    # Get user skills
    skills = db.execute_query(
        """
        SELECT s.id, s.name
        FROM skills s
        JOIN user_skills us ON s.id = us.skill_id
        WHERE us.user_id = %s
        ORDER BY s.name
        """,
        (user_id,),
        fetch=True
    )
    
    user = user[0]
    print(f"\n=== User: {user[1]} (ID: {user[0]}) ===")
    print(f"Email: {user[2]}")
    print(f"Full Name: {user[3] or 'N/A'}")
    print(f"Bio: {user[4] or 'N/A'}")
    
    print("\nSkills:")
    if skills:
        for skill in skills:
            print(f"- {skill[1]} (ID: {skill[0]})")
    else:
        print("No skills listed.")

@auth.require_login
def update_user():
    """Update the current user's profile."""
    current_user = auth.get_current_user()
    
    # Get current user details
    user = db.execute_query(
        "SELECT username, email, full_name, bio FROM users WHERE id = %s",
        (current_user.user_id,),
        fetch=True
    )[0]
    
    print("\n=== Update Profile ===")
    print("Leave blank to keep current value.")
    
    # Get updated values
    username = utils.get_input(f"Username [{user[0]}]: ", validator=utils.validate_username) or user[0]
    email = utils.get_input(f"Email [{user[1]}]: ", validator=utils.validate_email) or user[1]
    full_name = utils.get_input(f"Full Name [{user[2] or ''}]: ") or user[2]
    bio = utils.get_input(f"Bio [{user[3] or ''}]: ") or user[3]
    
    # Check if username or email is taken by another user
    if username != user[0] or email != user[1]:
        check = db.execute_query(
            "SELECT id FROM users WHERE (username = %s OR email = %s) AND id != %s",
            (username, email, current_user.user_id),
            fetch=True
        )
        
        if check:
            print("Username or email already in use by another user.")
            return False
    
    # Update user
    try:
        db.execute_query(
            """
            UPDATE users
            SET username = %s, email = %s, full_name = %s, bio = %s
            WHERE id = %s
            """,
            (username, email, full_name, bio, current_user.user_id)
        )
        
        # Update session if username changed
        if username != user[0]:
            current_user.username = username
            
        if email != user[1]:
            current_user.email = email
            
        print("Profile updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False

@auth.require_login
def delete_user():
    """Delete (soft delete) the current user's account."""
    current_user = auth.get_current_user()
    
    # Confirm deletion
    confirm = utils.get_input(
        f"Are you sure you want to delete your account '{current_user.username}'? (y/n): "
    ).lower()
    
    if confirm != 'y':
        print("Account deletion cancelled.")
        return False
    
    # Soft delete the user
    try:
        db.execute_query(
            "UPDATE users SET deleted_at = NOW() WHERE id = %s",
            (current_user.user_id,)
        )
        
        print("Account deleted successfully.")
        auth.logout()
        return True
    except Exception as e:
        print(f"Error deleting account: {e}")
        return False
