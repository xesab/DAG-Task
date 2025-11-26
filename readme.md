# Task Management API

A Django REST API for managing tasks with dependency tracking and status management.

## Features

- **Task Management**: Create, read, update, and delete tasks
- **Task Dependencies**: Define and manage task dependencies (prevent circular dependencies)
- **Status Tracking**: Track task status (Pending, Running, Completed)
- **REST API**: Full REST API using Django Ninja
- **Admin Dashboard**: Django admin interface for easy management
- **Database**: SQLite for data persistence

## Tech Stack

- **Framework**: Django 5.2.8
- **API**: Django Ninja 1.5.0
- **Validation**: Pydantic 2.12.4
- **Static Files**: WhiteNoise 6.11.0
- **Database**: SQLite3

## Installation

### Prerequisites
- Python 3.8+

### Setup

1. Clone the repository
```bash
git clone "url"
cd problem
```

2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py migrate
```

5. Create a superuser (optional, for admin access)
```bash
python manage.py createsuperuser
```

## Running the Server

```bash
uvicorn demoapi.asgi:application --host 0.0.0.0 --port 8000 --reload | python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

Access the interactive API documentation at:
- **API Docs**: `http://localhost:8000/api/docs`
- **Admin Panel**: `http://localhost:8000/admin`

## Project Structure

```
core/               # Main application
├── models.py       # Task and Dependency models
├── api.py          # API endpoints
├── schemas.py      # Pydantic schemas
└── services.py     # Business logic

demoapi/            # Django project settings
├── settings.py     # Project configuration
├── urls.py         # URL routing
└── wsgi.py         # WSGI application
```

## Environment Variables

Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key
DEBUG=True
```