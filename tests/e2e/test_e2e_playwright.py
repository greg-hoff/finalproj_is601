import pytest

@pytest.mark.e2e
def test_homepage_loads(page, fastapi_server):
    """
    Test that the homepage loads correctly and shows the expected content.
    
    This test navigates to the homepage and verifies that the welcome message
    and authentication links are displayed correctly.
    """
    # Navigate to the test server (not hardcoded localhost)
    page.goto(fastapi_server)
    
    # Wait for the page to load
    page.wait_for_load_state('networkidle')
    
    # Check that the page title is correct (matches template block title)
    assert "Home" in page.title()
    
    # Check that the welcome message is displayed (it's an h1, not h2)
    welcome_text = page.locator('h1:has-text("Welcome to the Calculations App")')
    assert welcome_text.is_visible()
    
    # Check that login/register links are shown
    login_link = page.locator('a:has-text("Login")')
    register_link = page.locator('a:has-text("Register")')
    assert login_link.is_visible()
    assert register_link.is_visible()

@pytest.mark.e2e
def test_login_validation_error_handling(page, fastapi_server):
    """Test that login form handles invalid credentials (stays on login page)."""
    page.goto(f"{fastapi_server}login")
    
    # Try to login with invalid credentials
    page.fill('#username', 'invalid_user')
    page.fill('#password', 'wrong_password')
    page.click('button[type="submit"]')
    
    # Wait a moment for potential redirect, then verify we're still on login page
    page.wait_for_timeout(1000)  # Wait 1 second
    assert 'login' in page.url

@pytest.mark.e2e
def test_registration_to_login_flow(page, fastapi_server):
    """Test basic registration form submission and redirect to login."""
    page.goto(f"{fastapi_server}register")
    
    # Fill registration form with valid data
    page.fill('#first_name', 'Test')
    page.fill('#last_name', 'User')
    page.fill('#email', 'testuser@example.com')
    page.fill('#username', 'testuser123')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Should redirect to login page after successful registration
    page.wait_for_url('**/login')
    assert 'login' in page.url

@pytest.mark.e2e
def test_unauthenticated_dashboard_redirect(page, fastapi_server):
    """Test that accessing dashboard without authentication redirects to login."""
    # Try to access dashboard directly without authentication
    page.goto(f"{fastapi_server}dashboard")
    
    # Should be redirected to login page
    page.wait_for_url('**/login')
    assert 'login' in page.url
