import re
from playwright.sync_api import Playwright, sync_playwright, expect


# Define the ShoppingItem class to represent each item in the shopping list
class ShoppingItem:
    def __init__(self, name, quantity):
        self.name = name  # Name of the item
        self.quantity = quantity  # Quantity of the item to be added to the cart

    def add_to_cart(self, page):
        # Wait for the page to fully load before interacting with it
        page.wait_for_load_state('load')

        # Locate the exact heading by matching the full text of the item name
        item_heading_locator = page.locator(f"role=heading[name='{self.name}']")

        # Click the item heading to go to the product page
        item_heading_locator.click()

        # Locate the "Add to cart" button on the product page
        add_to_cart_button = page.get_by_role("button", name="Add to cart")

        # Locate the "+" button that increases quantity
        increase_quantity_button = page.get_by_role("button", name="Increase quantity")

        # Check if the "Add to cart" button is enabled and visible
        if add_to_cart_button.is_enabled() and add_to_cart_button.is_visible():
            #Increase quantity to self.quantity value
            for i in range(self.quantity):
                if i == self.quantity-1:
                    add_to_cart_button.click()  # Click the add-to-cart button when the required number of items has been set
                    #Special case Thor Hammer
                    if self.name == "Thor Hammer" and self.quantity > 1:
                        page.wait_for_timeout(500)
                        expect(page.locator("[aria-label='You can only have one Thor Hammer in the cart.']")).to_be_visible()
                        print("You can only have one Thor Hammer, don't be greedy!")
                    else:
                        page.wait_for_timeout(500)  # Add a 500ms delay between each click to mimic human behavior
                        expect(page.locator("[aria-label='Product added to shopping cart.']")).to_be_visible()
                        print(f"Added {self.name} to cart {self.quantity} times.")
                else:
                    increase_quantity_button.click()  # Click the "+" button to increase quantity of items to be added to cart
                    print(f"Increased quantity of {self.name} to add to cart to {i+2}.")

        else:
            # If the item is not available in stock or the button is not visible, print a message
            print(f"Item {self.name} not in stock")

        # Navigate to the first page of products after adding the item to the cart
        page.go_back()  # Go back to the previous page
        first_page_button = page.get_by_role("button", name="Page-1")
        first_page_button.click()  # Click the button to go to the first page

    def search_item_on_pages(self, page):
        # Start from the first page
        current_page = 1
        page.wait_for_timeout(500)
        # Get the number of pages by counting the list items in the pagination
        # Subtract 2 to account for the "Previous" and "Next" buttons
        number_of_pages = page.locator('ul.pagination').locator('li.page-item').count() - 2
        print("\n")
        while True:
            print(f"Searching for {self.name} on page {current_page}...")

            # Wait for the page to fully load before searching for the item
            page.wait_for_load_state('load')  # Ensure the page is fully loaded before proceeding

            # Look for the product name on the current page
            item_locator = page.locator(f"role=heading[name='{self.name}']")

            # Check if the item exists on the current page
            if item_locator.is_visible():
                print(f"{self.name} found on page number {current_page}.")
                self.add_to_cart(page)  # Item found, add it to the cart
                return

            # Define locators for next page, and first page buttons
            next_page_button = page.get_by_role("button", name="Next")
            first_page_button = page.get_by_role("button", name="Page-1")

            # If we haven't reached the last page
            if current_page < number_of_pages:
                next_page_button.click()  # Go to the next page
                page.wait_for_load_state('load')  # Wait for the page to fully load
                current_page += 1
                page.wait_for_timeout(500)  # Add a 500ms delay between each click to mimic human behavior
            else:
                # If we reached the last page, click the "First Page" button
                first_page_button.click()
                print(f"Item {self.name} not found on any page.")
                return

#prints out contents of cart including total price
def cart_contents(page):
    # Locate the cart icon using its data-test attribute and aria-label
    cart_icon = page.locator('a[data-test="nav-cart"][aria-label="cart"]')

    # Check if the cart icon is visible on the page before attempting to click it
    if cart_icon.is_visible():
        cart_icon.click()

    # Wait for the page to load completely after the click (this ensures that the cart page is fully loaded)
    page.wait_for_load_state('load')

    # Optional: Wait for 500 milliseconds to ensure everything is properly rendered
    page.wait_for_timeout(500)

    # Wait for the table to load
    page.wait_for_selector('tbody tr', timeout=5000)

    # Locate all rows in the table body
    rows = page.locator('tbody tr')

    # Count the number of rows
    num_rows = rows.count()

    print("\nCART CONTENTS:\n")

    for i in range(num_rows):
        row = rows.nth(i)  # Get the i-th row
        product_name = row.locator('span[data-test="product-title"]').inner_text()          #Get product name
        price_value = row.locator('span[data-test="product-price"]').inner_text()           #Get value of one product
        total_price_value = row.locator('span[data-test="line-price"]').inner_text()        #Get total price of number of products
        quantity_value = row.locator('input[data-test="product-quantity"]').input_value()   #Get number of products

        # Check if the quantity is 1 or more to display the respective information
        if int(quantity_value) == 1:
            print(f"{product_name}: Quantity = {quantity_value}, Cost of 1 = {price_value}")
        else:
            print(f"{product_name}: Quantity = {quantity_value}, Cost of 1 = {price_value}, Cost of {quantity_value} = {total_price_value}")

    # Locate the element containing the cart total price using its data-test attribute and extract its inner text
    cart_price = page.locator('td[data-test="cart-total"]').inner_text()

    # Print the cart total price
    print("\nCart total:", cart_price)

# Test function to automate the shopping item search and adding process
def test_add_items_to_cart(playwright: Playwright) -> None:
    # Launch the browser in non-headless mode so we can see the automation process
    browser = playwright.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://practicesoftwaretesting.com/")  # Navigate to the website

    # Ensure the page is fully loaded before proceeding
    page.wait_for_load_state('load')
    page.wait_for_timeout(500)

    # Create shopping list items using the ShoppingItem class
    shopping_list = [
        ShoppingItem("Bolt", 2),  # Bolt not available, but items including "Bolt" string are
        ShoppingItem("Pliers", 2),
        ShoppingItem("Long Nose Pliers", 2), #Not in stock test
        ShoppingItem("Plieasdrs", 2),  # Misspelled, just for testing
        ShoppingItem("Thor Hammer", 12),  # Max Thor Hammer quantity is 1
        ShoppingItem("Claw Hammer with Shock Reduction Grip", 4),
        ShoppingItem("Mini Screwdriver", 4),
        ShoppingItem("Cordless Drill 24V", 1)
    ]

    # Iterate over the shopping list and add each item to the cart
    for item in shopping_list:
        item.search_item_on_pages(page)  # Search the item across all pages and add it to the cart

    # Print cart contents with total price
    cart_contents(page)


    # Close the context and browser after the operation
    context.close()
    browser.close()