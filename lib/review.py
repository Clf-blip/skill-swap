"""
Review commands for the skill-swap application.
"""
from tabulate import tabulate
from . import db
from . import auth
from . import utils

@auth.require_login
def add_review(request_id, rating, comments):
    """
    Add a review for a completed service request.
    
    Args:
        request_id (int): The ID of the service request
        rating (int): Rating from 1 to 5
        comments (str): Review comments
        
    Returns:
        bool: True if successful, False otherwise
    """
    current_user = auth.get_current_user()
    
    # Validate rating
    if not utils.validate_integer(rating, min_val=1, max_val=5):
        print("Rating must be between 1 and 5.")
        return False
    
    # Get the service request
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
    
    requester_id, provider_id, status = request[0]
    
    # Check if user is part of the request
    if current_user.user_id != requester_id and current_user.user_id != provider_id:
        print("You can only review requests you participated in.")
        return False
    
    # Check if request is completed
    if status != 'completed':
        print("You can only review completed requests.")
        return False
    
    # Determine reviewer and reviewee
    reviewer_id = current_user.user_id
    reviewee_id = provider_id if reviewer_id == requester_id else requester_id
    
    # Check if review already exists
    existing_review = db.execute_query(
        """
        SELECT id FROM reviews
        WHERE service_request_id = %s AND reviewer_id = %s
        """,
        (request_id, reviewer_id),
        fetch=True
    )
    
    if existing_review:
        print("You have already reviewed this service request.")
        return False
    
    # Create the review
    try:
        db.execute_query(
            """
            INSERT INTO reviews
            (service_request_id, reviewer_id, reviewee_id, rating, comments)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (request_id, reviewer_id, reviewee_id, rating, comments)
        )
        print("Review added successfully!")
        return True
    except Exception as e:
        print(f"Error adding review: {e}")
        return False

@auth.require_login
def list_reviews_by_reviewer(reviewer_id):
    """
    List reviews by a specific reviewer.
    
    Args:
        reviewer_id (int): The ID of the reviewer
    """
    # Validate reviewer
    if not db.execute_query(
        "SELECT id FROM users WHERE id = %s AND deleted_at IS NULL",
        (reviewer_id,),
        fetch=True
    ):
        print(f"User with ID {reviewer_id} not found.")
        return
    
    # Get reviews
    reviews = db.execute_query(
        """
        SELECT r.id, u.username as reviewee, r.rating, r.comments, 
               r.created_at, sr.id as request_id
        FROM reviews r
        JOIN users u ON r.reviewee_id = u.id
        JOIN service_requests sr ON r.service_request_id = sr.id
        WHERE r.reviewer_id = %s
        ORDER BY r.created_at DESC
        """,
        (reviewer_id,),
        fetch=True
    )
    
    if not reviews:
        print("No reviews found.")
        return
    
    # Format reviews for display
    headers = ["ID", "Reviewee", "Rating", "Comments", "Date", "Request ID"]
    rows = [
        [
            r[0], r[1], f"{r[2]}/5", 
            r[3][:50] + ('...' if len(r[3]) > 50 else ''), 
            utils.format_datetime(r[4]), r[5]
        ] 
        for r in reviews
    ]
    
    print("\n=== Reviews Given ===")
    print(tabulate(rows, headers=headers, tablefmt="simple"))

@auth.require_login
def list_reviews_by_reviewee(reviewee_id):
    """
    List reviews for a specific reviewee.
    
    Args:
        reviewee_id (int): The ID of the reviewee
    """
    # Validate reviewee
    if not db.execute_query(
        "SELECT id FROM users WHERE id = %s AND deleted_at IS NULL",
        (reviewee_id,),
        fetch=True
    ):
        print(f"User with ID {reviewee_id} not found.")
        return
    
    # Get reviews
    reviews = db.execute_query(
        """
        SELECT r.id, u.username as reviewer, r.rating, r.comments, 
               r.created_at, sr.id as request_id
        FROM reviews r
        JOIN users u ON r.reviewer_id = u.id
        JOIN service_requests sr ON r.service_request_id = sr.id
        WHERE r.reviewee_id = %s
        ORDER BY r.created_at DESC
        """,
        (reviewee_id,),
        fetch=True
    )
    
    if not reviews:
        print("No reviews found.")
        return
    
    # Calculate average rating
    total_rating = sum(r[2] for r in reviews)
    avg_rating = total_rating / len(reviews)
    
    # Format reviews for display
    headers = ["ID", "Reviewer", "Rating", "Comments", "Date", "Request ID"]
    rows = [
        [
            r[0], r[1], f"{r[2]}/5", 
            r[3][:50] + ('...' if len(r[3]) > 50 else ''), 
            utils.format_datetime(r[4]), r[5]
        ] 
        for r in reviews
    ]
    
    print(f"\n=== Reviews Received (Average: {avg_rating:.1f}/5) ===")
    print(tabulate(rows, headers=headers, tablefmt="simple"))

@auth.require_login
def view_reviews_for_request(request_id):
    """
    View all reviews for a specific service request.
    
    Args:
        request_id (int): The ID of the service request
    """
    current_user = auth.get_current_user()
    
    # Check if request exists and user is part of it
    request = db.execute_query(
        """
        SELECT requester_id, provider_id
        FROM service_requests
        WHERE id = %s
        """,
        (request_id,),
        fetch=True
    )
    
    if not request:
        print(f"Service request with ID {request_id} not found.")
        return
    
    requester_id, provider_id = request[0]
    
    if current_user.user_id != requester_id and current_user.user_id != provider_id:
        print("You can only view reviews for requests you participated in.")
        return
    
    # Get reviews
    reviews = db.execute_query(
        """
        SELECT r.id, 
               reviewer.username as reviewer_name,
               reviewee.username as reviewee_name,
               r.rating, r.comments, r.created_at
        FROM reviews r
        JOIN users reviewer ON r.reviewer_id = reviewer.id
        JOIN users reviewee ON r.reviewee_id = reviewee.id
        WHERE r.service_request_id = %s
        """,
        (request_id,),
        fetch=True
    )
    
    if not reviews:
        print("No reviews found for this service request.")
        return
    
    print(f"\n=== Reviews for Service Request ID {request_id} ===")
    
    for r in reviews:
        print(f"Review ID: {r[0]}")
        print(f"Reviewer: {r[1]}")
        print(f"Reviewee: {r[2]}")
        print(f"Rating: {r[3]}/5")
        print(f"Comments: {r[4]}")
        print(f"Date: {utils.format_datetime(r[5])}")
        print("-" * 40)
