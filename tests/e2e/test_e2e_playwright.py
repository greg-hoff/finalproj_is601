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

@pytest.mark.e2e
def test_calculation_create_and_retrieve(page, fastapi_server):
    """Test creating a calculation and viewing it in the history."""
    # First register and login a user
    page.goto(f"{fastapi_server}register")
    
    # Fill registration form
    page.fill('#first_name', 'Calc')
    page.fill('#last_name', 'Tester')
    page.fill('#email', 'calctester@example.com')
    page.fill('#username', 'calctester')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Should redirect to login, now login
    page.wait_for_url('**/login')
    page.fill('#username', 'calctester')
    page.fill('#password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Should be on dashboard now
    page.wait_for_url('**/dashboard')
    assert 'dashboard' in page.url
    
    # Create a new calculation
    page.select_option('#calcType', 'addition')
    page.fill('#calcInputs', '10, 20, 30')
    page.click('button[type="submit"]')
    
    # Wait for calculation to be processed and page to update
    page.wait_for_timeout(2000)
    
    # Check that calculation appears in history table
    # Look for the result value (10+20+30=60)
    result_cell = page.locator('td:has-text("60")')
    assert result_cell.is_visible()
    
    # Check that operation type is visible
    type_cell = page.locator('td:has-text("addition")')
    assert type_cell.is_visible()
    
    # Check that inputs are visible
    inputs_cell = page.locator('td:has-text("10, 20, 30")')
    assert inputs_cell.is_visible()

@pytest.mark.e2e
def test_calculation_view_details(page, fastapi_server):
    """Test viewing detailed calculation information."""
    # Register and login a user
    page.goto(f"{fastapi_server}register")
    
    page.fill('#first_name', 'View')
    page.fill('#last_name', 'Tester')
    page.fill('#email', 'viewtester@example.com')
    page.fill('#username', 'viewtester')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Login
    page.wait_for_url('**/login')
    page.fill('#username', 'viewtester')
    page.fill('#password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Create a calculation first
    page.wait_for_url('**/dashboard')
    page.select_option('#calcType', 'multiplication')
    page.fill('#calcInputs', '5, 4, 2')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    
    # Click on View button for the calculation
    view_button = page.locator('a:has-text("View")')
    assert view_button.is_visible()
    view_button.click()
    
    # Should be on view calculation page
    page.wait_for_url('**/view/**')
    assert 'view' in page.url
    
    # Check that calculation details are displayed using more specific locators
    assert page.locator('p.font-medium:has-text("multiplication")').is_visible()
    assert page.locator('text=40').first.is_visible()  # 5*4*2=40
    assert page.locator('text=5, 4, 2').first.is_visible()

@pytest.mark.e2e
def test_calculation_update_flow(page, fastapi_server):
    """Test updating a calculation through the edit form."""
    # Register and login
    page.goto(f"{fastapi_server}register")
    
    page.fill('#first_name', 'Edit')
    page.fill('#last_name', 'Tester')
    page.fill('#email', 'edittester@example.com')
    page.fill('#username', 'edittester')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Login
    page.wait_for_url('**/login')
    page.fill('#username', 'edittester')
    page.fill('#password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Create initial calculation
    page.wait_for_url('**/dashboard')
    page.select_option('#calcType', 'subtraction')
    page.fill('#calcInputs', '100, 25')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    
    # Click Edit button
    edit_button = page.locator('a:has-text("Edit")')
    assert edit_button.is_visible()
    edit_button.click()
    
    # Should be on edit page
    page.wait_for_url('**/edit/**')
    assert 'edit' in page.url
    
    # Modify the calculation (note: operation type is read-only, only inputs can be changed)
    # Clear the existing inputs and add new ones
    page.fill('#calcInputs', '100, 50, 25')
    
    # Submit the update
    update_button = page.locator('button:has-text("Save Changes")')
    update_button.click()
    
    # Should redirect back to dashboard or view page
    page.wait_for_timeout(2000)
    
    # Go back to dashboard to verify the change
    page.goto(f"{fastapi_server}dashboard")
    
    # Check that the calculation was updated (100-50-25=25 since type is still subtraction)
    page.wait_for_timeout(1000)
    # Look for the result in the specific result column (font-semibold class is used for results)
    result_cell = page.locator('td.font-semibold:has-text("25")')
    assert result_cell.is_visible()
    
    # Verify operation type is still subtraction (since it's read-only)
    type_cell = page.locator('td:has-text("subtraction")')
    assert type_cell.is_visible()
    
    # Verify inputs were updated
    inputs_cell = page.locator('td:has-text("100, 50, 25")')
    assert inputs_cell.is_visible()

@pytest.mark.e2e
def test_calculation_delete_functionality(page, fastapi_server):
    """Test deleting a calculation from the dashboard."""
    # Register and login
    page.goto(f"{fastapi_server}register")
    
    page.fill('#first_name', 'Delete')
    page.fill('#last_name', 'Tester')
    page.fill('#email', 'deletetester@example.com')
    page.fill('#username', 'deletetester')
    page.fill('#password', 'SecurePass123!')
    page.fill('#confirm_password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Login
    page.wait_for_url('**/login')
    page.fill('#username', 'deletetester')
    page.fill('#password', 'SecurePass123!')
    page.click('button[type="submit"]')
    
    # Create a calculation to delete
    page.wait_for_url('**/dashboard')
    page.select_option('#calcType', 'division')
    page.fill('#calcInputs', '100, 5')
    page.click('button[type="submit"]')
    
    page.wait_for_timeout(2000)
    
    # Verify calculation exists (100/5=20) - use specific result column locator
    result_cell = page.locator('td.font-semibold:has-text("20")')
    assert result_cell.is_visible()
    
    # Click Delete button
    delete_button = page.locator('button:has-text("Delete")')
    assert delete_button.is_visible()
    
    # Handle confirmation dialog if it exists
    page.on("dialog", lambda dialog: dialog.accept())
    delete_button.click()
    
    page.wait_for_timeout(2000)
    
    # Verify calculation is no longer in the table
    # The result "20" should not be visible in the result column anymore
    result_cell_after = page.locator('td.font-semibold:has-text("20")')
    assert not result_cell_after.is_visible()
