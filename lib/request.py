"""
Service request commands for the skill-swap application.
"""
from datetime import datetime
from tabulate import tabulate
from . import db
from . import auth
from . import utils

@auth.require_login
def create_request(provider_id, skill_id, time_str, duration, credit_cost, notes=None):
    """
    Create a new service request.
    
    Args:
        provider_id (int): The ID of the service provider
        skill_id (int): The ID of the skill being requested
        time_str (str): The time of the service (YYYY-MM-DDTHH:MM)
        duration (int): The duration in minutes
        credit_cost (int): The cost in credits
        notes (str, optional): Additional notes
        
    Returns:
        bool: True if successful, False otherwise
    """
    current_user = auth.get_current_user()
    
    # Validate provider
    provider = db.execute_query(
        "SELECT id FROM users WHERE id = %s AND deleted_at IS NULL",
        (provider_id,),
        fetch=True
    )
    
    if not provider:
        print(f"Provider with ID {provider_id} not found.")
        return False
    
    # Validate skill
    skill = db.execute_query(
        """
        SELECT s.id FROM skills s
        JOIN user_skills us ON s.id = us.skill_id
        WHERE s.id = %s AND us.user_id = %s
        """,
        (skill_id, provider_id),
        fetch=True
    )
    
    if not skill:
        print(f"Provider does not offer the skill with ID {skill_id}.")
        return False
    
    # Validate time
    try:
        service_time = utils.parse_datetime(time_str)
        if service_time < datetime.now():
            print("Service time must be in the future.")
            return False
    except ValueError:
        print("Invalid time format. Use YYYY-MM-DDTHH:MM")
        return False
    
    # Validate duration and credit cost
    if not utils.validate_integer(duration, min_val=15):
        print("Duration must be at least 15 minutes.")
        return False
    
    if not utils.validate_integer(credit_cost, min_val=1):
        print("Credit cost must be at least 1.")
        return False
    
    # Create the request
    try:
        db.execute_query(
            """
            INSERT INTO service_requests
            (requester_id, provider_id, skill_id, time, duration, credit_cost, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                current_user.user_id, 
                provider_id, 
                skill_id, 
                service_time, 
                duration, 
                credit_cost, 
                notes
            )
        )
        print("Service request created successfully!")
        return True
    except Exception as e:
        print(f"Error creating service request: {e}")
        return False

@auth.require_login
def list_requests(user_id=None, status=None):
    """
    List service requests, optionally filtered.
    
    Args:
        user_id (int, optional): Filter by user ID
        status (str, optional): Filter by status
    """
    current_user = auth.get_current_user()
    
    # Build the query
    query = """
        SELECT r.id, r.status, 
               requester.username as requester, 
               provider.username as provider,
               s.name as skill_name, r.time, 
               r.duration, r.credit_cost
        FROM service_requests r
        JOIN users requester ON r.requester_id = requester.id
        JOIN users provider ON r.provider_id = provider.id
        JOIN skills s ON r.skill_id = s.id
        WHERE 1=1
    """
    params = []
    
    # Apply filters
    if user_id:
        query += " AND (r.requester_id = %s OR r.provider_id = %s)"
        params.extend([user_id, user_id])
    else:
        # If no user_id specified, only show requests for the current user
        query += " AND (r.requester_id = %s OR r.provider_id = %s)"
        params.extend([current_user.user_id, current_user.user_id])
    
    if status:
        query += " AND r.status = %s"
        params.append(status)
    
    query += " ORDER BY r.time DESC"
    
    # Execute query
    requests = db.execute_query(query, params, fetch=True)
    
    if not requests:
        print("No service requests found.")
        return
    
    # Format requests for display
    headers = ["ID", "Status", "Requester", "Provider", "Skill", "Time", "Duration", "Credits"]
    rows = []
    
    for r in requests:
        # Format the datetime
        time_str = utils.format_datetime(r[5])
        rows.append([r[0], r[1], r[2], r[3], r[4], time_str, f"{r[6]} min", r[7]])
    
    print("\n=== Service Requests ===")
    print(tabulate(rows, headers=headers, tablefmt="simple"))

@auth.require_login
def view_request(request_id):
    """
    View details of a specific service request.
    
    Args:
        request_id (int): The ID of the request to view
    """
    current_user = auth.get_current_user()
    
    # Get request details
    request = db.execute_query(
        """
        SELECT r.id, r.status, 
               requester.id as requester_id, requester.username as requester_name,
               provider.id as provider_id, provider.username as provider_name,
               s.id as skill_id, s.name as skill_name, 
               r.time, r.duration, r.credit_cost, r.notes,
               r.created_at, r.updated_at
        FROM service_requests r
        JOIN users requester ON r.requester_id = requester.id
        JOIN users provider ON r.provider_id = provider.id
        JOIN skills s ON r.skill_id = s.id
        WHERE r.id = %s AND (r.requester_id = %s OR r.provider_id = %s)
        """,
        (request_id, current_user.user_id, current_user.user_id),
        fetch=True
    )
    
    if not request:
        print(f"Service request with ID {request_id} not found or you don't have access.")
        return
    
    r = request[0]
    
    print(f"\n=== Service Request: ID {r[0]} ===")
    print(f"Status: {r[1]}")
    print(f"Requester: {r[3]} (ID: {r[2]})")
    print(f"Provider: {r[5]} (ID: {r[4]})")
    print(f"Skill: {r[7]} (ID: {r[6]})")
    print(f"Time: {utils.format_datetime(r[8])}")
    print(f"Duration: {r[9]} minutes")
    print(f"Credit Cost: {r[10]}")
    print(f"Notes: {r[11] or 'N/A'}")
    print(f"Created: {utils.format_datetime(r[12])}")
    print(f"Last Updated: {utils.format_datetime(r[13])}")
    
    # Check if there are reviews for this request
    reviews = db.execute_query(
        """
        SELECT reviewer.username, reviewee.username, r.rating, r.comments
        FROM reviews r
        JOIN users reviewer ON r.reviewer_id = reviewer.id
        JOIN users reviewee ON r.reviewee_id = reviewee.id
        WHERE r.service_request_id = %s
        """,
        (request_id,),
        fetch=True
    )
    
    if reviews:
        print("\nReviews:")
        for review in reviews:
            print(f"- {review[0]} rated {review[1]} {review[2]}/5: {review[3]}")

@auth.require_login
def update_request(request_id, status=None, notes=None, time_str=None):
    """
    Update a service request.
    
    Args:
        request_id (int): The ID of the request to update
        status (str, optional): New status
        notes (str, optional): New notes
        time_str (str, optional): New time (YYYY-MM-DDTHH:MM)
        
    Returns:
        bool: True if successful, False otherwise
    """
    current_user = auth.get_current_user()
    
    # Get the request
    request = db.execute_query(
        """
        SELECT requester_id, provider_id, status
        FROM service_requests
        WHERE id = %s
        """,
        (request_id,),
        fetch=True
    )
    
    if not request:
        print(f"Service request with ID {request_id} not found.")
        return False
    
    requester_id, provider_id, current_status = request[0]
    
    # Check permissions
    is_requester = requester_id == current_user.user_id
    is_provider = provider_id == current_user.user_id
    
    if not (is_requester or is_provider):
        print("You don't have permission to update this request.")
        return False
    
    # Build update query
    query = "UPDATE service_requests SET updated_at = NOW()"
    params = []
    
    if status:
        # Validate status transition
        valid_status = False
        
        if current_status == 'pending':
            # Requester can cancel, provider can accept/reject
            if is_requester and status == 'cancelled':
                valid_status = True
            elif is_provider and status in ('accepted', 'rejected'):
                valid_status = True
        elif current_status == 'accepted':
            # Provider can mark as completed
            if is_provider and status == 'completed':
                valid_status = True
        
        if not valid_status:
            print(f"Invalid status transition from '{current_status}' to '{status}'.")
            return False
        
        query += ", status = %s"
        params.append(status)
    
    if notes:
        query += ", notes = %s"
        params.append(notes)
    
    if time_str:
        if not is_requester:
            print("Only the requester can change the time.")
            return False
        
        try:
            service_time = utils.parse_datetime(time_str)
            if service_time < datetime.now():
                print("Service time must be in the future.")
                return False
            
            query += ", time = %s"
            params.append(service_time)
        except ValueError:
            print("Invalid time format. Use YYYY-MM-DDTHH:MM")
            return False
    
    # If nothing to update
    if not params:
        print("No updates specified.")
        return False
    
    # Add the WHERE clause
    query += " WHERE id = %s"
    params.append(request_id)
    
    # Execute the update
    try:
        db.execute_query(query, params)
        print("Service request updated successfully!")
        return True
    except Exception as e:
        print(f"Error updating service request: {e}")
        return False

@auth.require_login
def delete_request(request_id):
    """
    Delete a service request.
    
    Args:
        request_id (int): The ID of the request to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    current_user = auth.get_current_user()
    
    # Check if request exists and user is the requester
    request = db.execute_query(
        "SELECT requester_id FROM service_requests WHERE id = %s",
        (request_id,),
        fetch=True
    )
    
    if not request:
        print(f"Service request with ID {request_id} not found.")
        return False
    
    if request[0][0] != current_user.user_id:
        print("You can only delete requests that you created.")
        return False
    
    # Delete the request
    try:
        db.execute_query(
            "DELETE FROM service_requests WHERE id = %s",
            (request_id,)
        )
        print("Service request deleted successfully!")
        return True
    except Exception as e:
        print(f"Error deleting service request: {e}")
        return False
