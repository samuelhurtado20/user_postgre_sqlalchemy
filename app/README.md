# User CRUD API

A comprehensive User CRUD (Create, Read, Update, Delete) API implementation using FastAPI and PostgreSQL.

## Features

- **Complete User Management**: Create, read, update, and delete users
- **Authentication**: JWT-based authentication with secure password hashing
- **Validation**: Comprehensive input validation using Pydantic schemas
- **Pagination**: Built-in pagination support for user listings
- **Soft Delete**: Users are soft-deleted (marked as inactive) rather than permanently removed
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Logging**: Comprehensive logging throughout the application
- **Error Handling**: Proper error handling with meaningful error messages

## Project Structure

```
app/
├── api/
│   └── v1/
│       └── user_controller.py    # User API endpoints
├── core/
│   ├── config.py                 # Application configuration
│   ├── dependencies.py           # Dependency injection
│   └── logging.py                # Logging configuration
├── db/
│   ├── base.py                   # Database base classes
│   └── session.py                # Database session management
├── models/
│   └── user.py                   # User SQLAlchemy model
├── schemas/
│   └── user.py                   # Pydantic schemas for validation
├── services/
│   └── user_service.py           # Business logic layer
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment variables example
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd basic_api_folder_structure/app
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and configuration
   ```

5. **Set up PostgreSQL database**:
   - Create a PostgreSQL database
   - Update the DATABASE_URL in your .env file

## Running the Application

```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### User Management

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/api/v1/users/` | Create a new user | No |
| GET | `/api/v1/users/` | Get all users (paginated) | No |
| GET | `/api/v1/users/{id}` | Get user by ID | No |
| PUT | `/api/v1/users/{id}` | Update user | No |
| DELETE | `/api/v1/users/{id}` | Delete user (soft delete) | No |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/login` | Login and get access token |
| GET | `/api/v1/users/me` | Get current user info (requires token) |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API information |

## User Model

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Example Usage

### Create a User
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "email": "john@example.com",
       "password": "SecurePass123",
       "first_name": "John",
       "last_name": "Doe"
     }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "password": "SecurePass123"
     }'
```

### Get Users (with pagination)
```bash
curl "http://localhost:8000/api/v1/users/?page=1&size=10"
```

## Configuration

Key configuration options in `.env`:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `DEBUG`: Enable debug mode
- `DEFAULT_PAGE_SIZE`: Default pagination size
- `MAX_PAGE_SIZE`: Maximum allowed page size

## Security Features

- **Password Hashing**: Passwords are hashed using bcrypt
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive validation of all inputs
- **SQL Injection Protection**: SQLAlchemy ORM provides protection
- **CORS**: Configurable CORS middleware

## Development

### Running Tests
```bash
pytest
```

### Code Style
The project follows Python best practices and includes comprehensive logging and error handling.

## Production Deployment

1. Set `DEBUG=false` in production
2. Use a strong, random `SECRET_KEY`
3. Configure proper CORS origins
4. Set up proper database credentials
5. Use environment variables for sensitive configuration
6. Consider using a production WSGI server like Gunicorn

## License

This project is licensed under the MIT License.
