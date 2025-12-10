github - https://github.com/greg-hoff/module14_is601
dockerhub - https://hub.docker.com/repository/docker/greghoff/module14_is601/general

For this assignment, I added a suite of playwright tests. We look at registration, manipulating calculations, and error responses. 

# Calculator App - Quick Start Guide

## Prerequisites
- Docker and Docker Compose
- Python 3.10+ with virtual environment
- Git

## Starting the Application

1. **Clone and setup:**
   ```bash
   git clone git@github.com:greg-hoff/module14_is601.git
   cd module14_is601
   ```

2. **Start with Docker (Recommended):**
   ```bash
   docker-compose up -d
   ```
   - App runs on: http://localhost:8000
   - PgAdmin: http://localhost:5050

3. **Alternative - Local development:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## Running Tests

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install Playwright browsers (for e2e tests):**
   ```bash
   playwright install
   ```

3. **Run all tests:**
   ```bash
   pytest
   ```

4. **Run specific test types:**
   ```bash
   # Unit tests only
   pytest tests/unit/
   
   # Integration tests only
   pytest tests/integration/
   
   # E2E tests only
   pytest tests/e2e/
   
   # With coverage report
   pytest --cov=app
   ```

## Key Features
- User registration and authentication
- Calculator operations (add, subtract, multiply, divide)
- Calculation history and management
- JWT token-based security
- Redis session management
- PostgreSQL database

## Stopping the Application
```bash
docker-compose down
```
