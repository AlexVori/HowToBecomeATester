import re
from playwright.sync_api import Playwright, sync_playwright, expect


def launch_browser(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    return browser, context, page


def add_task(page, task):
    textbox = page.get_by_role("textbox", name="What needs to be done?")
    textbox.click()
    textbox.fill(task)
    textbox.press("Enter")


def assert_task_added(page, task):
    expect(page.get_by_role("listitem").filter(has_text=task), f"item {task} was not added to the list").to_be_visible()

def delete_task(page, task):
    list_item = page.get_by_role("listitem").filter(has_text=task)
    list_item.locator("button.destroy").click()

def edit_task(page, old_task, new_task):
    list_item = page.get_by_role("listitem").filter(has_text=old_task)
    list_item.locator("label").dblclick()  # Double-click to edit
    input_field = list_item.locator("input.edit")
    input_field.fill(new_task)
    input_field.press("Enter")

def assert_total_items_count(page, expected_count):
    total_items = page.locator("ul.todo-list > li")
    expect(total_items, f"List doesn't have {expected_count} items").to_have_count(expected_count)

def mark_task_as_completed(page, task):
    page.get_by_role("listitem").filter(has_text=task).get_by_label("Toggle Todo").check()

def mark_task_as_active(page, task):
    page.get_by_role("listitem").filter(has_text=task).get_by_label("Toggle Todo").uncheck()

def clear_completed_tasks(page):
    page.get_by_role("button", name="Clear completed").click()

def assert_no_completed_tasks(page):
    completed_items = page.locator("ul.todo-list > li.completed")
    expect(completed_items).to_have_count(0)

def assert_task_not_in_list(page, task):
    expect(page.locator("ul.todo-list"), f"List contains item {task}").not_to_contain_text(task)

def assert_task_in_list(page, task):
    expect(page.locator("ul.todo-list"), f"List doesn't contain item {task}").to_contain_text(task)

def filter_tasks_by_status(page, status):
    page.get_by_role("link", name=status).click()


def test_add_task(playwright: Playwright) -> None:
    # Launch browser and navigate to the page
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc#/")

    # Define a list of tasks to add to the list
    tasks = ["a1", "a2", "a3"]

    # Add tasks to the list
    for task in tasks:
        add_task(page, task)
        assert_task_added(page, task)

    # Verify total items count after adding tasks
    assert_total_items_count(page, 3)

    # Close the browser and context
    context.close()
    browser.close()

def test_filter_active_tasks(playwright: Playwright) -> None:
    # Launch browser and navigate to the page
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc#/")

    # Define a list of tasks to add to the list
    tasks = ["a1", "a2", "a3"]

    # Add tasks to the list
    for task in tasks:
        add_task(page, task)
        assert_task_added(page, task)

    # Mark "a1" as completed
    mark_task_as_completed(page, "a1")

    # Filter active tasks and assert visibility
    filter_tasks_by_status(page, "Active")
    assert_task_not_in_list(page, "a1")
    assert_task_in_list(page, "a2")
    assert_task_in_list(page, "a3")

    # Verify total items count for active tasks
    assert_total_items_count(page, 2)

    # Close the browser and context
    context.close()
    browser.close()

def test_filter_completed_tasks(playwright: Playwright) -> None:
    # Launch browser and navigate to the page
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc#/")

    # Define a list of tasks to add to the list
    tasks = ["a1", "a2", "a3"]

    # Add tasks to the list
    for task in tasks:
        add_task(page, task)
        assert_task_added(page, task)

    # Mark "a1" as completed
    mark_task_as_completed(page, "a1")

    # Filter completed tasks and assert visibility
    filter_tasks_by_status(page, "Completed")
    assert_task_in_list(page, "a1")
    assert_task_not_in_list(page, "a2")
    assert_task_not_in_list(page, "a3")

    # Verify total items count for completed tasks
    assert_total_items_count(page, 1)

    # Close the browser and context
    context.close()
    browser.close()

def test_clear_completed_tasks(playwright: Playwright) -> None:
    # Launch browser and navigate to the page
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc#/")

    # Add tasks to the list
    tasks = ["a1", "a2", "a3"]
    for task in tasks:
        add_task(page, task)
        assert_task_added(page, task)

    # Mark tasks "a1" and "a2" as completed
    mark_task_as_completed(page, "a1")
    mark_task_as_completed(page, "a2")

    # Clear completed tasks
    clear_completed_tasks(page)

    # Assert that no completed tasks remain
    assert_no_completed_tasks(page)

    # Verify the total items count after clearing
    assert_total_items_count(page, 1)  # Only "a3" should remain

    # Close the browser and context
    context.close()
    browser.close()

# unedited item still visible after editing..why?
def test_edit_task(playwright: Playwright) -> None:
    # Launch browser and navigate to the page
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc#/")

    # Add a task to the list
    add_task(page, "a1")
    assert_task_added(page, "a1")

    # Edit task "a1" to "a1 updated"
    edit_task(page, "a1", "updated")

    # Assert that "a1 updated" appears
    assert_task_in_list(page, "updated")

    # Assert that "a1 updated" disappeared
    assert_task_not_in_list(page, "a1")

    # Verify total items count remains the same
    assert_total_items_count(page, 1)

    # Close the browser and context
    context.close()
    browser.close()

def test_filter_links_visible(playwright: Playwright) -> None:
    # Launch browser and navigate to the page
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc#/")

    # Add tasks to the list
    tasks = ["a1", "a2", "a3"]
    for task in tasks:
        add_task(page, task)
        assert_task_added(page, task)

    # Assert that filter links are visible
    filters = page.locator("ul.filters > li > a")
    expect(filters).to_have_count(3)
    expect(filters.nth(0)).to_have_text("All")
    expect(filters.nth(1)).to_have_text("Active")
    expect(filters.nth(2)).to_have_text("Completed")

    # Close the browser and context
    context.close()
    browser.close()

def test_delete_task(playwright: Playwright) -> None:
    # Launch browser and navigate to the page
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc#/")

    # Add tasks to the list
    tasks = ["a1", "a2", "a3"]
    for task in tasks:
        add_task(page, task)
        assert_task_added(page, task)

    # Delete task "a2"
    page.get_by_role("button", name="Delete").click()
    page.get_by_role("button", name="Delete").click()
    page.get_by_role("button", name="Delete").click()

    # Assert that "a2" is no longer in the list
    assert_task_not_in_list(page, "a1")
    assert_task_not_in_list(page, "a2")
    assert_task_not_in_list(page, "a3")

    # Verify total items count after deletion
    assert_total_items_count(page, 0)

    # Close the browser and context
    context.close()
    browser.close()

def test_mark_task_as_active(playwright: Playwright) -> None:
    # Launch browser and navigate to the page
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc#/")

    # Add tasks to the list
    tasks = ["a1", "a2", "a3"]
    for task in tasks:
        add_task(page, task)
        assert_task_added(page, task)

    # Mark "a1" as completed
    mark_task_as_completed(page, "a1")

    # Mark "a1" as active again
    mark_task_as_active(page, "a1")

    # Assert that "a1" is in the Active filter
    filter_tasks_by_status(page, "Active")
    assert_task_in_list(page, "a1")

    # Verify total items count for active tasks
    assert_total_items_count(page, 3)

    # Close the browser and context
    context.close()
    browser.close()