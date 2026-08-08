"""
End-to-end UI automation for the login page, using Selenium WebDriver.

Requires the Flask app to be running (default http://localhost:5000).
Requires Chrome/Chromium + a matching chromedriver on PATH (webdriver-manager
handles this automatically).

Run with:
    pytest tests/test_login_selenium.py -v
"""
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session")
def driver():
    options = Options()
   #options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")

    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(3)
    yield drv
    drv.quit()


def login_as(driver, username, password):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-btn").click()


def test_login_page_has_correct_title(driver):
    driver.get(f"{BASE_URL}/login")
    assert driver.title == "Login"
    assert driver.find_element(By.TAG_NAME, "h1").text == "Sign in"


def test_valid_login_redirects_to_dashboard(driver):
    login_as(driver, "admin", "password123")
    WebDriverWait(driver, 5).until(EC.url_contains("/dashboard"))
    welcome = driver.find_element(By.ID, "welcome-message")
    assert "Welcome, admin!" in welcome.text


def test_invalid_login_shows_error_message(driver):
    login_as(driver, "admin", "wrongpassword")
    error = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "error-message"))
    )
    assert "Invalid username or password" in error.text
    # should stay on the login page
    assert "/login" in driver.current_url


def test_empty_form_submission_shows_required_error(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "login-btn").click()
    error = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "error-message"))
    )
    assert "required" in error.text.lower()


def test_logout_returns_to_login_page(driver):
    login_as(driver, "admin", "password123")
    WebDriverWait(driver, 5).until(EC.url_contains("/dashboard"))

    driver.find_element(By.ID, "logout-link").click()
    WebDriverWait(driver, 5).until(EC.url_contains("/login"))
    assert driver.find_element(By.TAG_NAME, "h1").text == "Sign in"


def test_dashboard_redirects_unauthenticated_user_to_login(driver):
    driver.get(f"{BASE_URL}/dashboard")
    WebDriverWait(driver, 5).until(EC.url_contains("/login"))
    assert "/login" in driver.current_url


def test_account_locks_after_repeated_failed_attempts(driver):
    for _ in range(3):
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("wrong")
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(0.2)

    error = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "error-message"))
    )
    assert "locked" in error.text.lower()
