"""
Skill management commands for the skill-swap application.
"""
from tabulate import tabulate
from . import db
from . import auth
from . import utils

@auth.require_login
def add_skill(skill_name):
    """
    Add a skill to the current user.
    
    Args:
        skill_name (str): The name of the skill to add
    """
    current_user = auth.get_current_user()
    
    # Check if skill exists
    skill = db.execute_query(
        "SELECT id FROM skills WHERE name = %s",
        (skill_name,),
        fetch=True
    )
    
    skill_id = None
    if skill:
        skill_id = skill[0][0]
    else:
        # Create the skill if it doesn't exist
        try:
            db.execute_query(
                "INSERT INTO skills (name) VALUES (%s) RETURNING id",
                (skill_name,),
                fetch=True
            )
            
            skill = db.execute_query(
                "SELECT id FROM skills WHERE name = %s",
                (skill_name,),
                fetch=True
            )
            skill_id = skill[0][0]
        except Exception as e:
            print(f"Error creating skill: {e}")
            return False
    
    # Check if user already has this skill
    user_skill = db.execute_query(
        "SELECT id FROM user_skills WHERE user_id = %s AND skill_id = %s",
        (current_user.user_id, skill_id),
        fetch=True
    )
    
    if user_skill:
        print(f"You already have the skill '{skill_name}'.")
        return False
    
    # Add skill to user
    try:
        db.execute_query(
            "INSERT INTO user_skills (user_id, skill_id) VALUES (%s, %s)",
            (current_user.user_id, skill_id)
        )
        print(f"Skill '{skill_name}' added successfully!")
        return True
    except Exception as e:
        print(f"Error adding skill: {e}")
        return False

@auth.require_login
def remove_skill(skill_id):
    """
    Remove a skill from the current user.
    
    Args:
        skill_id (int): The ID of the skill to remove
    """
    current_user = auth.get_current_user()
    
    # Check if user has this skill
    skill = db.execute_query(
        """
        SELECT s.name FROM skills s
        JOIN user_skills us ON s.id = us.skill_id
        WHERE us.user_id = %s AND s.id = %s
        """,
        (current_user.user_id, skill_id),
        fetch=True
    )
    
    if not skill:
        print(f"You don't have a skill with ID {skill_id}.")
        return False
    
    # Remove skill from user
    try:
        db.execute_query(
            "DELETE FROM user_skills WHERE user_id = %s AND skill_id = %s",
            (current_user.user_id, skill_id)
        )
        print(f"Skill '{skill[0][0]}' removed successfully!")
        return True
    except Exception as e:
        print(f"Error removing skill: {e}")
        return False

@auth.require_login
def list_skills():
    """List all available skills."""
    skills = db.execute_query(
        """
        SELECT s.id, s.name, COUNT(us.user_id) as user_count
        FROM skills s
        LEFT JOIN user_skills us ON s.id = us.skill_id
        GROUP BY s.id
        ORDER BY s.name
        """,
        fetch=True
    )
    
    if not skills:
        print("No skills found.")
        return
    
    # Format skills for display
    headers = ["ID", "Skill Name", "Users with Skill"]
    rows = [[s[0], s[1], s[2]] for s in skills]
    
    print("\n=== Skills ===")
    print(tabulate(rows, headers=headers, tablefmt="simple"))
    
@auth.require_login
def browse_users_by_skill(skill_id):
    """
    List users who have a specific skill.
    
    Args:
        skill_id (int): The ID of the skill to browse
    """
    # Check if skill exists
    skill = db.execute_query(
        "SELECT name FROM skills WHERE id = %s",
        (skill_id,),
        fetch=True
    )
    
    if not skill:
        print(f"Skill with ID {skill_id} not found.")
        return
    
    # Get users with this skill
    users = db.execute_query(
        """
        SELECT u.id, u.username, u.full_name, u.bio
        FROM users u
        JOIN user_skills us ON u.id = us.user_id
        WHERE us.skill_id = %s AND u.deleted_at IS NULL
        ORDER BY u.username
        """,
        (skill_id,),
        fetch=True
    )
    
    if not users:
        print(f"No users found with skill '{skill[0][0]}'.")
        return
    
    # Format users for display
    headers = ["ID", "Username", "Full Name", "Bio"]
    rows = [[u[0], u[1], u[2] or 'N/A', (u[3] or 'N/A')[:50]] for u in users]
    
    print(f"\n=== Users with Skill: {skill[0][0]} ===")
    print(tabulate(rows, headers=headers, tablefmt="simple"))

@auth.require_login
def list_user_skills():
    """List the skills of the current user."""
    current_user = auth.get_current_user()
    
    skills = db.execute_query(
        """
        SELECT s.id, s.name
        FROM skills s
        JOIN user_skills us ON s.id = us.skill_id
        WHERE us.user_id = %s
        ORDER BY s.name
        """,
        (current_user.user_id,),
        fetch=True
    )
    
    if not skills:
        print("You don't have any skills listed.")
        return
    
    # Format skills for display
    headers = ["ID", "Skill Name"]
    rows = [[s[0], s[1]] for s in skills]
    
    print(f"\n=== Your Skills ===")
    print(tabulate(rows, headers=headers, tablefmt="simple"))
