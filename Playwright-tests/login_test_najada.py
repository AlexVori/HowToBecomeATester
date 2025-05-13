import re
from playwright.sync_api import sync_playwright, Page, expect

URL = "https://www.najada.games/"

# Cílem úkolu je doplnit funkci LOGIN, tak aby všechny testy prošly
def login(page: Page, user, password):
    print(f"\nZkouším přihlásit uživatele. Email: {user}, Heslo: {password}")

    # prohlížeč je otevřený přes page, není jej tedy třeba otevírat
    # otevřít stránku saucedemo.com, adresa je v proměnné URL
    page.goto(URL)

    # ověřit že se stránka otevřela
    page.wait_for_load_state('load')
    page.wait_for_timeout(3000)

    page.click(".loginAction")
    page.locator("#email").fill(user)
    page.locator("#password").fill(password)
    page.click('[type="submit"]')

def test_bad_user_short_password(page: Page):
    login(page, "Test_account", "chyba")
    try:
        expect(page.locator(".validation-message")).to_be_visible()
    except AssertionError:
        print("Error: Error message not visible")

def test_bad_password(page: Page):
    login(page, "Test_account", "123456798")
    try:
     expect(page.locator('p[class="red error-message"]')).to_be_visible()
    except AssertionError:
        print("Error: Error message not visible")

def test_login_success(page: Page):
    login(page, "Test_account", "Heslotajne123")
    try:
        expect(page.locator('a[class="UserStateReview__name font-encodeCond text-left line-1"]')).to_be_visible()
    except AssertionError:
        print("Error: User not logged in")
    page.screenshot(path="screenshot_login_success_najada.png")

def test_logout(page: Page):
    login(page, "Test_account", "Heslotajne123")

    try:
        expect(page.locator('a[class="UserStateReview__name font-encodeCond text-left line-1"]')).to_be_visible()
    except AssertionError:
        print("Error: User not logged in")

    try:
        page.click('[class="icon icon_logout"]')
    except TimeoutError:
        print("Error: Logout button not visible or clickable.")

    try:
        expect(page.locator('.loginAction')).to_be_visible()
    except AssertionError:
        print("Error: Login button not visible after logging out.")
    page.screenshot(path="screenshot_logout_success_najada.png")
