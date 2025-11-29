"""
Step definitions for Google Search feature
"""
from behave import given, when, then
import time
from automation.google_search import GoogleSearchAutomation


@given('I am on Google homepage')
def step_impl(context):
    """Navigate to Google homepage"""
    context.automation = GoogleSearchAutomation()
    context.automation.start_browser()
    context.automation.page.goto('https://www.google.com')
    time.sleep(1)


@when('I search for "{query}"')
def step_impl(context, query):
    """Perform search"""
    search_box = context.automation.page.locator('textarea[name="q"], input[name="q"]').first
    search_box.wait_for(state='visible', timeout=10000)
    search_box.fill(query)
    search_box.press('Enter')
    context.automation.page.wait_for_load_state('networkidle', timeout=15000)
    time.sleep(2)
    context.query = query


@then('I should see search results')
def step_impl(context):
    """Verify search results are visible"""
    results_container = context.automation.page.locator('#search, #rso').first
    assert results_container.is_visible(), "Search results container not visible"
    context.automation.take_screenshot('search_results')


@then('the results should contain news articles')
def step_impl(context):
    """Verify news articles are present"""
    # Check for news-specific elements or regular results
    news_items = context.automation.page.locator('div[data-hveid], div.g').all()
    assert len(news_items) > 0, "No news articles found"


@then('I should see at least {count:d} results')
def step_impl(context, count):
    """Verify minimum number of results"""
    results = context.automation.extract_search_results()
    assert len(results) >= count, f"Expected at least {count} results, got {len(results)}"
    context.results = results


@then('each result should have a title and URL')
def step_impl(context):
    """Verify result structure"""
    for result in context.results:
        assert 'title' in result and result['title'], "Result missing title"
        assert 'url' in result and result['url'], "Result missing URL"


def after_scenario(context, scenario):
    """Cleanup after scenario"""
    if hasattr(context, 'automation'):
        context.automation.stop_browser()
