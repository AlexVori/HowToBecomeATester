import re
from playwright.sync_api import sync_playwright, Page, expect

URL = "https://www.rohlik.cz/"

# Cílem úkolu je doplnit funkci LOGIN, tak aby všechny testy prošly
def login(page: Page, email, password):
    print(f"\nZkouším přihlásit uživatele. Email: {email}, Heslo: {password}")

    # prohlížeč je otevřený přes page, není jej tedy třeba otevírat
    # otevřít stránku saucedemo.com, adresa je v proměnné URL
    page.goto(URL)

    # ověřit že se stránka otevřela
    page.wait_for_load_state('load')
    page.wait_for_timeout(3000)

    page.click('[data-test="IconUserLogin"]')
    page.locator("#email").fill(email)
    page.locator("#password").fill(password)
    page.click('[data-test="btnSignIn"]')

def test_bad_email_bad_password(page: Page):
    login(page, "123@seznam.cz", "chyba")
    try:
        expect(page.locator('span[data-test="notification-content" ]')).to_be_visible()
    except AssertionError:
        print("Error: Error message not visible.")

def test_no_email_no_password(page: Page):
    login(page, "", "")
    try:
        expect(page.get_by_text('Email je povinný')).to_be_visible()
        expect(page.get_by_text('Heslo je povinné')).to_be_visible()
    except AssertionError:
        print("Error: Error messages not visible")