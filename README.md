# Dailee Task Madailee-be-fastapi/
├── src/
│   ├── main.py               # FastAPI application entry point
│   ├── core/                 # Core application components
│   │   ├── __init__.py
│   │   ├── config.py         # Application configuration
│   │   ├── dependencies.py   # Shared dependencies
│   │   └── database/         # Database connection and models
│   │       ├── __init__.py
│   │       ├── database.py   # Database connection and session management
│   │       └── models.py     # SQLAlchemy database models
│   ├── auth/                 # Authentication app
│   │   ├── __init__.py
│   │   ├── models.py         # Auth Pydantic models
│   │   ├── service.py        # Auth business logic
│   │   └── router.py         # Auth API endpoints
│   ├── tasks/                # Task management app
│   │   ├── __init__.py
│   │   ├── models.py         # Task Pydantic models
│   │   ├── service.py        # Task business logic
│   │   └── router.py         # Task API endpoints
│   ├── users/                # User management app
│   │   ├── __init__.py
│   │   ├── models.py         # User Pydantic models
│   │   ├── service.py        # User business logic
│   │   └── router.py         # User API endpoints
│   ├── schedules/            # Schedule management app
│   │   ├── __init__.py
│   │   ├── models.py         # Schedule Pydantic models
│   │   ├── service.py        # Schedule business logic
│   │   └── router.py         # Schedule API endpoints
│   └── statistics/           # Statistics and analytics app
│       ├── __init__.py
│       ├── models.py         # Statistics Pydantic models
│       ├── service.py        # Statistics business logic
│       └── router.py         # Statistics API endpointserview
This is a FastAPI backend for the Dailee task management mobile app. It provides RESTful APIs for managing tasks, users, schedules, task completions, and user streaks. The backend uses PostgreSQL as the database and is designed to work seamlessly with the Flutter mobile application.

## Features
- **Task Management**: Create, read, update, delete tasks
- **User Management**: User registration and management
- **Scheduled Tasks**: Recurring task scheduling
- **Task Completions**: Track task completion history
- **Streak Tracking**: Monitor user task completion streaks
- **Statistics**: Comprehensive task and user statistics
- **RESTful API**: Well-structured endpoints following REST principles

## Project Structure
```
dailie-be-fastapi/
├── src/
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Application configuration
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py       # Database connection and session management
│   │   └── models.py         # SQLAlchemy database models
│   ├── models/               # Pydantic models for API
│   │   ├── __init__.py
│   │   ├── task.py           # Task-related models
│   │   ├── user.py           # User models
│   │   ├── schedule.py       # Schedule models
│   │   └── user_task_streak.py # Streak models
│   └── routers/              # API route handlers
│       ├── __init__.py
│       ├── tasks.py          # Task endpoints
│       ├── users.py          # User endpoints
│       └── statistics.py     # Statistics and completion endpoints
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── setup_db.py               # Database setup script
├── run_server.py             # Server startup script
└── README.md                 # Project documentation
```

## Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd dailie-be-fastapi
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL
Install PostgreSQL and create a database:
```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE dailee;
CREATE USER dailee_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE dailee TO dailee_user;
```

### 5. Configure environment variables
Copy the example environment file and customize it:
```bash
cp .env.example .env
```

Edit `.env` with your database settings:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dailee
DB_USER=dailee_user
DB_PASSWORD=your_password
```

### 6. Set up the database
Run the database setup script to create tables:
```bash
python setup_db.py
```

## Running the Application

### Development Mode
Start the development server with hot-reload:
```bash
python run_server.py
```

Or using uvicorn directly:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode
For production, set `DEBUG=False` in your `.env` file and run:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

### Interactive Documentation
Once the server is running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/token` - Login and get access token
- `GET /api/v1/auth/me` - Get current authenticated user

#### Tasks
- `GET /api/v1/tasks/` - List all tasks
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{task_id}` - Get a specific task
- `PUT /api/v1/tasks/{task_id}` - Update a task
- `DELETE /api/v1/tasks/{task_id}` - Delete a task
- `POST /api/v1/tasks/scheduled` - Create a scheduled task
- `GET /api/v1/tasks/scheduled` - Get scheduled tasks

#### Users
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{user_id}` - Get a specific user

#### Schedules
- `GET /api/v1/schedules/` - List all schedules
- `POST /api/v1/schedules/` - Create a new schedule
- `GET /api/v1/schedules/{schedule_id}` - Get a specific schedule
- `PUT /api/v1/schedules/{schedule_id}` - Update a schedule
- `DELETE /api/v1/schedules/{schedule_id}` - Delete a schedule

#### Statistics & Completions
- `GET /api/v1/statistics/completions` - Get task completions
- `POST /api/v1/statistics/completions` - Record task completion
- `GET /api/v1/statistics/streaks` - Get user task streaks
- `GET /api/v1/statistics/streaks/{user_id}/{task_id}` - Get specific streak

#### Health Check
- `GET /` - API information
- `GET /health` - Health check endpoint

## Database Schema

The application uses the following main entities:
- **Tasks**: Core task information with type, status, and scheduling
- **Users**: User management and authentication
- **ScheduledTasks**: Recurring task scheduling information
- **TaskCompletions**: Historical record of completed tasks
- **UserTaskStreaks**: Track user completion streaks per task

## Environment Configuration

Available environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_NAME` | dailee | Database name |
| `DB_USER` | postgres | Database user |
| `DB_PASSWORD` | password | Database password |
| `API_HOST` | 0.0.0.0 | API server host |
| `API_PORT` | 8000 | API server port |
| `DEBUG` | True | Debug mode |
| `SECRET_KEY` | your-secret-key-here | JWT secret key |

## Flutter Integration

This backend is designed to work with the Dailee Flutter mobile app. The API endpoints match the data models used in the Flutter application, ensuring seamless integration.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License
This project is licensed under the MIT License.