# Skill Swap CLI

A command-line interface (CLI) application for skill exchange. Users can register, list their skills, request services from other users, and leave reviews.

## Usage

All commands are executed through the `skill_swap.py` script:

```
./bin/skill_swap.py <command> [subcommand] [options]
```

### Getting Started

1. First, register a new user:
   ```bash
   ./bin/skill_swap.py register
   ```
   Follow the prompts to enter your username, email, password, and optional profile information.

2. Login to the system:
   ```bash
   ./bin/skill_swap.py login
   ```
   Enter your username and password when prompted.

3. Once logged in, you can use all the available commands. Your session will persist between commands.

### Authentication Commands

- Register: `./bin/skill_swap.py register`
- Login: `./bin/skill_swap.py login`
- Logout: `./bin/skill_swap.py logout`

### User Commands

- List users: `./bin/skill_swap.py user list`
- View user details: `./bin/skill_swap.py user view <id>`
- Update profile: `./bin/skill_swap.py user update`
- Delete account: `./bin/skill_swap.py user delete`

### Skill Commands

- Add a skill: `./bin/skill_swap.py skill add <skill name>`
- Remove a skill: `./bin/skill_swap.py skill remove <skill id>`
- List all skills: `./bin/skill_swap.py skill list`
- Browse users by skill: `./bin/skill_swap.py skill browse <skill id>`

### Service Request Commands

- Create a request: `./bin/skill_swap.py request create --provider=<id> --skill=<id> --time="YYYY-MM-DDTHH:mm" --duration=<minutes> --credit=<amount> [--notes="..."]`
- List requests: `./bin/skill_swap.py request list [--user=<id>] [--status=<status>]`
- View request details: `./bin/skill_swap.py request view <id>`
- Update request: `./bin/skill_swap.py request update <id> [--status=<status>] [--notes="..."] [--time="..."]`
- Delete request: `./bin/skill_swap.py request delete <id>`

### Review Commands

- Add a review: `./bin/skill_swap.py review add --request=<id> --rating=<1-5> --comments="..."`
- List reviews by reviewer: `./bin/skill_swap.py review list --reviewer=<userId>`
- List reviews by reviewee: `./bin/skill_swap.py review list --reviewee=<userId>`

### Database Management

- Run migrations: `./bin/skill_swap.py db migrate`
- Run seeds: `./bin/skill_swap.py db seed`

## Project Structure

```
skill-swap/
│
├── bin/
│   └── skill_swap.py         # CLI entry point, executable with shebang
│
├── lib/
│   ├── __init__.py
│   ├── db.py                # DB connection, migration & seed helpers
│   ├── auth.py              # Authentication & session management
│   ├── user.py              # User commands: register, login, update, delete, list
│   ├── skill.py             # Skill commands: add, remove, list, browse users
│   ├── request.py           # Service request commands: create, update, delete, list
│   ├── review.py            # Review commands: add, view, list
│   ├── utils.py             # Helpers: hashing, validation, input prompts
│   ├── models.py            # SQLAlchemy models for the database
│   ├── skill_swap.db        # SQLite database file
│   ├── alembic.ini          # Alembic configuration file
│   └── alembic/             # Alembic migrations directory
│       ├── env.py           # Alembic environment configuration
│       ├── script.py.mako   # Alembic script template
│       └── versions/        # Alembic migration versions
│
├── migrations/
│   └── 001_create_schema.sql  # Legacy SQL migrations
│
├── seeds/
│   └── 001_seed_skills_users.sql # Seed SQL: users, skills, assignments
│
├── sql/
│   └── schema.sql           # Complete DB schema (reference only)
│
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (optional with SQLite)
└── README.md              # This file
```

## Database Schema

The application uses the following database schema:

- `users`: Stores user account information
- `skills`: Stores available skills
- `user_skills`: Maps skills to users (many-to-many relationship)
- `service_requests`: Stores service request information
- `reviews`: Stores reviews for completed service requests
- `alembic_version`: Used by Alembic to track migration versions

## Seed Data

The application comes with seed data including:
- 5 users (alice, bob, carol, dave, eve)
- 5 skills (UX Design, French Tutoring, JavaScript Programming, Guitar Lessons, Plumbing)
- Skills assigned to users

The default password for all seed users is 'password123'.

## Setup

### Prerequisites

- Python 3.6+

### Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Database Setup

The application uses SQLite with Alembic for database migrations. The database file is located at `lib/skill_swap.db`.

#### Option 1: Using the built-in commands

The simplest way to set up the database:

```bash
./bin/skill_swap.py db migrate
./bin/skill_swap.py db seed
```

#### Option 2: Using Alembic directly

For more control over migrations:

1. Generate a new migration (if making schema changes):

```bash
alembic -c lib/alembic.ini revision --autogenerate -m "your migration description"
```

2. Run migrations:

```bash
alembic -c lib/alembic.ini upgrade head
```

3. Run seeds:

```bash
./bin/skill_swap.py db seed
```

## Features

- User authentication (register, login, logout)
- User profile management
- Skill management (add, remove, list, browse)
- Service request system (create, update, delete, list)
- Review and rating system
- SQLite database with SQLAlchemy ORM
- Alembic migration system
- Seed data support
- Persistent session between commands

## Example Workflow

Here's an example workflow to get started with the application:

1. Set up the database:
   ```bash
   ./bin/skill_swap.py db migrate
   ```

2. Register a new user:
   ```bash
   ./bin/skill_swap.py register
   ```

3. Login with your credentials:
   ```bash
   ./bin/skill_swap.py login
   ```

4. Add a skill you can offer (remember to use quotes for multi-word skills):
   ```bash
   ./bin/skill_swap.py skill add "Python Programming"
   ```

5. List all skills:
   ```bash
   ./bin/skill_swap.py skill list
   ```

6. Browse users with a specific skill:
   ```bash
   ./bin/skill_swap.py skill browse 1  # Skill with ID 1
   ```

7. Create a service request:
   ```bash
   ./bin/skill_swap.py request create --provider=1 --skill=1 --time="2025-06-01T14:00" --duration=60 --credit=10 --notes="Need help with coding"
   ```

8. List your service requests:
   ```bash
   ./bin/skill_swap.py request list
   ```

9. After a service is completed, add a review:
   ```bash
   ./bin/skill_swap.py review add --request=1 --rating=5 --comments="Great service!"
   ```

## Troubleshooting

### Database Issues

If you encounter database issues:

1. Check if the SQLite database file exists at `lib/skill_swap.db`
2. Try deleting the database file and running migrations again
3. Check if Alembic migrations were applied with `alembic -c lib/alembic.ini history`
4. For detailed error information, examine the SQLite database directly with `sqlite3 lib/skill_swap.db`

### Session Persistence

The application stores your session in a `.session` file in the project directory. If you experience authentication issues:

1. Check if the `.session` file exists
2. Try logging in again
3. If problems persist, delete the `.session` file and log in again

### Adding Multiple-Word Skills

When adding skills with multiple words, use quotes:

```bash
./bin/skill_swap.py skill add "Software Development"
```

## License

This project is open source and available under the MIT License.
