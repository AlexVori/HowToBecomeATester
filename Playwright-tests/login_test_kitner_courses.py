import re
from playwright.sync_api import sync_playwright, Page, expect

URL="http://testovani.kitner.cz/login"

# Cílem úkolu je doplnit funkci LOGIN, tak aby všechny testy prošly
def login(page: Page, email, password):
    print(f"\nZkouším přihlásit uživatele. Email: {email}, Heslo: {password}")

    # prohlížeč je otevřený přes page, není jej tedy třeba otevírat
    # otevřít stránku saucedemo.com, adresa je v proměnné URL
    page.goto(URL)

    # ověřit že se stránka otevřela
    page.wait_for_load_state('load')

    #fill user data and click login button
    page.locator('[data-test="email_input"]').fill(email)
    page.locator('[data-test="password_input"]').fill(password)
    page.click('[data-test="login_button"]')

def logout(page: Page):
    try:
        page.click('[data-test="logout_button"]')
    except TimeoutError:
        print("Error: Logout button not visible.")

def test_bad_email_ok_password(page: Page):
    login(page, "hinanoc939@naobk.com", "Alextajne123")
    try:
        expect(page.locator('[data-test="email_input_errors"]')).to_be_visible()
    except AssertionError:
        print("Error: Error messages not visible")

def test_no_email_ok_password(page: Page):
    login(page, "", "Alextajne123")
    try:
        expect(page.locator('[data-test="email_input_errors"]')).to_be_visible()
    except AssertionError:
        print("Error: Error messages not visible")

def test_ok_email_bad_password(page: Page):
    login(page, "anoc939@naobk.com", "extajne123")
    try:
        expect(page.locator('[data-test="email_input_errors"]')).to_be_visible()
    except AssertionError:
        print("Error: Error messages not visible")

def test_ok_email_no_password(page: Page):
    login(page, "hinanoc939@naobk.com", "")
    try:
        expect(page.locator('[data-test="password_input_errors"]')).to_be_visible()
    except AssertionError:
        print("Error: Error message not visible")

def test_no_email_no_password(page: Page):
    login(page, "", "")
    try:
        expect(page.locator('[data-test="email_input_errors"]')).to_be_visible()
        expect(page.locator('[data-test="password_input_errors"]')).to_be_visible()
    except AssertionError:
        print("Error: Error messages not visible")

def test_login_success(page: Page):
    login(page, "hinanoc939@naobk.com", "Alextajne123")
    try:
        expect(page.locator('[data-test="courses_title"]')).to_be_visible()
    except AssertionError:
        print("Error: User not logged in")
    page.screenshot(path="screenshot_login_success_kitner.png")

def test_logout_success(page: Page):
    login(page, "hinanoc939@naobk.com", "Alextajne123")

    try:
        expect(page.locator('[data-test="courses_title"]')).to_be_visible()
    except AssertionError:
        print("Error: User not logged in.")
    logout(page)
    try:
        expect(page.locator('[data-test="login_link"]')).to_be_visible()
    except AssertionError:
        print("Error: User not logged out.")

    page.screenshot(path="screenshot_logout_success_kitner.png")
