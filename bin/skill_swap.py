#!/usr/bin/env python3
"""
Skill Swap CLI - A command-line application for skill exchange

This is the main entry point for the skill-swap CLI application.
"""
import os
import sys
import argparse
from datetime import datetime

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import modules
from lib import db
from lib import auth
from lib import user
from lib import skill
from lib import request
from lib import review
from lib import utils

def setup_parser():
    """Set up the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Skill Swap - A CLI for exchanging skills",
        prog="skill_swap"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register a new user")
    
    # Login command
    login_parser = subparsers.add_parser("login", help="Login to the system")
    
    # Logout command
    logout_parser = subparsers.add_parser("logout", help="Logout from the system")
    
    # User commands
    user_parser = subparsers.add_parser("user", help="User management commands")
    user_subparsers = user_parser.add_subparsers(dest="subcommand", help="User command")
    
    user_list_parser = user_subparsers.add_parser("list", help="List all users")
    
    user_view_parser = user_subparsers.add_parser("view", help="View user details")
    user_view_parser.add_argument("id", type=int, help="User ID to view")
    
    user_update_parser = user_subparsers.add_parser("update", help="Update user profile")
    
    user_delete_parser = user_subparsers.add_parser("delete", help="Delete user account")
    
    # Skill commands
    skill_parser = subparsers.add_parser("skill", help="Skill management commands")
    skill_subparsers = skill_parser.add_subparsers(dest="subcommand", help="Skill command")
    
    skill_add_parser = skill_subparsers.add_parser("add", help="Add a skill")
    skill_add_parser.add_argument("name", help="Skill name to add")
    
    skill_remove_parser = skill_subparsers.add_parser("remove", help="Remove a skill")
    skill_remove_parser.add_argument("id", type=int, help="Skill ID to remove")
    
    skill_list_parser = skill_subparsers.add_parser("list", help="List all skills")
    
    skill_browse_parser = skill_subparsers.add_parser("browse", help="Browse users by skill")
    skill_browse_parser.add_argument("id", type=int, help="Skill ID to browse")
    
    # Request commands
    request_parser = subparsers.add_parser("request", help="Service request commands")
    request_subparsers = request_parser.add_subparsers(dest="subcommand", help="Request command")
    
    request_create_parser = request_subparsers.add_parser("create", help="Create a service request")
    request_create_parser.add_argument("--provider", type=int, required=True, help="Provider user ID")
    request_create_parser.add_argument("--skill", type=int, required=True, help="Skill ID")
    request_create_parser.add_argument("--time", required=True, help="Service time (YYYY-MM-DDTHH:MM)")
    request_create_parser.add_argument("--duration", type=int, required=True, help="Duration in minutes")
    request_create_parser.add_argument("--credit", type=int, required=True, help="Credit cost")
    request_create_parser.add_argument("--notes", help="Additional notes")
    
    request_list_parser = request_subparsers.add_parser("list", help="List service requests")
    request_list_parser.add_argument("--user", type=int, help="Filter by user ID")
    request_list_parser.add_argument("--status", choices=["pending", "accepted", "rejected", "completed", "cancelled"], 
                                      help="Filter by status")
    
    request_view_parser = request_subparsers.add_parser("view", help="View a service request")
    request_view_parser.add_argument("id", type=int, help="Request ID to view")
    
    request_update_parser = request_subparsers.add_parser("update", help="Update a service request")
    request_update_parser.add_argument("id", type=int, help="Request ID to update")
    request_update_parser.add_argument("--status", choices=["accepted", "rejected", "completed", "cancelled"], 
                                       help="New status")
    request_update_parser.add_argument("--notes", help="New notes")
    request_update_parser.add_argument("--time", help="New time (YYYY-MM-DDTHH:MM)")
    
    request_delete_parser = request_subparsers.add_parser("delete", help="Delete a service request")
    request_delete_parser.add_argument("id", type=int, help="Request ID to delete")
    
    # Review commands
    review_parser = subparsers.add_parser("review", help="Review commands")
    review_subparsers = review_parser.add_subparsers(dest="subcommand", help="Review command")
    
    review_add_parser = review_subparsers.add_parser("add", help="Add a review")
    review_add_parser.add_argument("--request", type=int, required=True, help="Service request ID")
    review_add_parser.add_argument("--rating", type=int, required=True, choices=range(1, 6), 
                                   help="Rating (1-5)")
    review_add_parser.add_argument("--comments", required=True, help="Review comments")
    
    review_list_parser = review_subparsers.add_parser("list", help="List reviews")
    review_list_group = review_list_parser.add_mutually_exclusive_group(required=True)
    review_list_group.add_argument("--reviewer", type=int, help="Filter by reviewer ID")
    review_list_group.add_argument("--reviewee", type=int, help="Filter by reviewee ID")
    
    # DB commands (for admins)
    db_parser = subparsers.add_parser("db", help="Database management commands")
    db_subparsers = db_parser.add_subparsers(dest="subcommand", help="DB command")
    
    db_migrate_parser = db_subparsers.add_parser("migrate", help="Run database migrations")
    db_seed_parser = db_subparsers.add_parser("seed", help="Run database seeds")
    
    return parser

def main():
    """Main entry point for the application."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Initialize DB connection
    try:
        db.init_db()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Make sure PostgreSQL is running and the .env file is configured correctly.")
        sys.exit(1)
    
    # Handle commands
    if not args.command:
        parser.print_help()
        return
    
    # DB Commands
    if args.command == "db":
        if not args.subcommand:
            print("Please specify a db subcommand")
            return
            
        if args.subcommand == "migrate":
            if db.run_migrations():
                print("Migrations completed successfully")
            else:
                print("Migration failed")
                
        elif args.subcommand == "seed":
            if db.run_seeds():
                print("Seeds completed successfully")
            else:
                print("Seeding failed")
        
    # Auth Commands
    elif args.command == "register":
        user.register_user()
        
    elif args.command == "login":
        user.login_user()
        
    elif args.command == "logout":
        auth.logout()
    
    # User Commands
    elif args.command == "user":
        if not args.subcommand:
            print("Please specify a user subcommand")
            return
            
        if args.subcommand == "list":
            user.list_users()
            
        elif args.subcommand == "view":
            user.view_user(args.id)
            
        elif args.subcommand == "update":
            user.update_user()
            
        elif args.subcommand == "delete":
            user.delete_user()
    
    # Skill Commands
    elif args.command == "skill":
        if not args.subcommand:
            print("Please specify a skill subcommand")
            return
            
        if args.subcommand == "add":
            skill.add_skill(args.name)
            
        elif args.subcommand == "remove":
            skill.remove_skill(args.id)
            
        elif args.subcommand == "list":
            skill.list_skills()
            
        elif args.subcommand == "browse":
            skill.browse_users_by_skill(args.id)
    
    # Request Commands
    elif args.command == "request":
        if not args.subcommand:
            print("Please specify a request subcommand")
            return
            
        if args.subcommand == "create":
            request.create_request(
                args.provider, args.skill, args.time,
                args.duration, args.credit, args.notes
            )
            
        elif args.subcommand == "list":
            request.list_requests(args.user, args.status)
            
        elif args.subcommand == "view":
            request.view_request(args.id)
            
        elif args.subcommand == "update":
            request.update_request(args.id, args.status, args.notes, args.time)
            
        elif args.subcommand == "delete":
            request.delete_request(args.id)
    
    # Review Commands
    elif args.command == "review":
        if not args.subcommand:
            print("Please specify a review subcommand")
            return
            
        if args.subcommand == "add":
            review.add_review(args.request, args.rating, args.comments)
            
        elif args.subcommand == "list":
            if args.reviewer:
                review.list_reviews_by_reviewer(args.reviewer)
            elif args.reviewee:
                review.list_reviews_by_reviewee(args.reviewee)

if __name__ == "__main__":
    main()
