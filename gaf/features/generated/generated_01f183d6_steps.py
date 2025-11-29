"""
Step definitions for Google
Auto-generated on 2025-11-29T23:35:59.874910
"""
from behave import given, when, then, step
from automation.google_search import GoogleSearchAutomation
import time


# Initialize automation
automation = GoogleSearchAutomation()


@given('I am on Google')
def step_impl(context):
    """Step: Given I am on Google"""
    automation.start_browser()
    automation.page.goto('https://www.google.com')
    context.automation = automation


@when('I search for weather')
def step_impl(context):
    """Step: When I search for weather"""
    query = "weather"
    search_box = automation.page.locator('textarea[name="q"], input[name="q"]').first
    search_box.fill(query)
    search_box.press('Enter')
    automation.page.wait_for_load_state('networkidle')
    time.sleep(2)


@then('I should see results')
def step_impl(context):
    """Step: Then I should see results"""
    results = automation.page.locator('#search, #rso').first
    assert results.is_visible(), "Search results not visible"
    automation.take_screenshot('test_results')

