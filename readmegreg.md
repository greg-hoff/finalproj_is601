github - https://github.com/greg-hoff/finalproj_is601
dockerhub - https://hub.docker.com/repository/docker/greghoff/finalproj_is601/general

For the final, I chose to add the modulus operation and add tests to get closer to full coverage. 
Adding in a new operation went surprisingly smooth. Using all of the knowledge of where things go from the hands on videos, I was able to find the different places to update with relative ease and accuracy. 

Increasing coverage proved a little more difficult. I noticed that main.py was not covered - generating tests here was straightforward. 
jwt.py was also not covered, but is valuable to cover. In generating these tests, I initially encountered asyncio conflicts between JWT tests and Playwright E2E tests. The solution was to create synchronous wrapper functions for JWT testing (app/auth/jwt_sync.py), which eliminated the event loop conflicts while maintaining full test coverage. Now all tests run together seamlessly with a simple pytest command.  

# Calculator App - Quick Start Guide

## Prerequisites
- Docker and Docker Compose
- Python 3.12+ with virtual environment
- Git

## Starting the Application

1. **Clone and setup:**
   ```bash
   git clone git@github.com:greg-hoff/finalproj_is601.git
   cd finalproj_is601
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
- Calculator operations (add, subtract, multiply, divide, modulus)
- Calculation history and management
- JWT token-based security
- Redis session management
- PostgreSQL database

## Stopping the Application
```bash
docker-compose down
```
