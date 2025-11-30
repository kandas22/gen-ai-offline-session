"""
End-to-End Test: BDD Generator API + Playwright Validation
Tests the complete flow: API call -> Generate BDD -> Execute with Playwright
"""
import requests
import json
import time
import yaml
from playwright.sync_api import sync_playwright

# Configuration
API_BASE_URL = "http://localhost:5001"
TEST_TIMEOUT = 30000  # 30 seconds


def test_bdd_generation_and_execution():
    """
    Complete E2E test:
    1. Call /api/bdd/generate to create a test
    2. Validate the generated feature file
    3. Execute the test scenario with Playwright
    """
    print("=" * 60)
    print("E2E Test: BDD Generation + Playwright Validation")
    print("=" * 60)
    
    # Step 1: Generate BDD test using YAML format
    print("\n[Step 1] Generating BDD test via API...")
    
    yaml_spec = """
feature: Google Search Real Scenario
description: Test actual Google search with Playwright validation

background:
  - Given I have a browser configured
  - And I navigate to Google

scenarios:
  - name: Search for rain news and validate results
    tags:
      - "@smoke"
      - "@e2e"
    steps:
      - When I search for "rain news today"
      - And I wait for results to load
      - Then I should see search results
      - And results should contain relevant titles
"""
    
    # Call the generate API
    response = requests.post(
        f"{API_BASE_URL}/api/bdd/generate",
        json={"specification": yaml_spec},
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 200, f"API call failed: {response.status_code}"
    result = response.json()
    
    print(f"✅ BDD test generated successfully")
    print(f"   Test ID: {result['data']['test_id']}")
    print(f"   Feature: {result['data']['feature_name']}")
    print(f"   Scenarios: {result['data']['scenarios_count']}")
    print(f"   Background: {result['data']['has_background']}")
    
    # Step 2: Validate the generated feature file exists
    print("\n[Step 2] Validating generated feature file...")
    
    feature_file = result['data']['feature_file']
    with open(feature_file, 'r') as f:
        feature_content = f.read()
    
    print(f"✅ Feature file exists: {feature_file}")
    print(f"   Content preview:\n{feature_content[:200]}...")
    
    # Validate feature file contains expected keywords
    assert "Feature: Google Search Real Scenario" in feature_content
    assert "Background:" in feature_content
    assert "Scenario: Search for rain news and validate results" in feature_content
    assert "@smoke" in feature_content
    assert "@e2e" in feature_content
    
    print("✅ Feature file validation passed")
    
    # Step 3: Execute the scenario with Playwright
    print("\n[Step 3] Executing scenario with Playwright...")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()
        page.set_default_timeout(TEST_TIMEOUT)
        
        try:
            # Background: Navigate to Google
            print("   🔹 Background: Navigating to Google...")
            page.goto("https://www.google.com")
            time.sleep(2)
            print("   ✅ Background completed")
            
            # Scenario Step 1: Search for "rain news today"
            print("   🔹 When I search for 'rain news today'...")
            search_box = page.locator('textarea[name="q"], input[name="q"]').first
            search_box.wait_for(state='visible', timeout=10000)
            search_box.fill("rain news today")
            search_box.press('Enter')
            print("   ✅ Search executed")
            
            # Scenario Step 2: Wait for results to load
            print("   🔹 And I wait for results to load...")
            page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(2)
            print("   ✅ Results loaded")
            
            # Scenario Step 3: Validate search results are visible
            print("   🔹 Then I should see search results...")
            results_container = page.locator('#search, #rso').first
            assert results_container.is_visible(), "Search results not visible"
            print("   ✅ Search results visible")
            
            # Scenario Step 4: Validate results contain relevant titles
            print("   🔹 And results should contain relevant titles...")
            
            # Get all result titles
            result_items = page.locator('h3').all()
            titles = [item.inner_text() for item in result_items[:5] if item.is_visible()]
            
            assert len(titles) > 0, "No result titles found"
            print(f"   ✅ Found {len(titles)} result titles")
            
            # Validate at least one title contains relevant keywords
            relevant_keywords = ['rain', 'weather', 'news', 'forecast', 'storm']
            has_relevant = any(
                any(keyword.lower() in title.lower() for keyword in relevant_keywords)
                for title in titles
            )
            
            assert has_relevant, "No relevant titles found"
            print("   ✅ Results contain relevant titles")
            
            # Print sample titles
            print("\n   Sample titles found:")
            for i, title in enumerate(titles[:3], 1):
                print(f"      {i}. {title[:60]}...")
            
            # Take screenshot
            screenshot_path = f"screenshots/e2e_test_{result['data']['test_id']}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n   📸 Screenshot saved: {screenshot_path}")
            
        finally:
            browser.close()
    
    print("\n" + "=" * 60)
    print("✅ E2E TEST PASSED")
    print("=" * 60)
    print("\nTest Summary:")
    print(f"  • API Generation: ✅ PASSED")
    print(f"  • Feature File Validation: ✅ PASSED")
    print(f"  • Playwright Execution: ✅ PASSED")
    print(f"  • Search Results: ✅ PASSED")
    print(f"  • Title Validation: ✅ PASSED")
    print("\nGenerated Files:")
    print(f"  • Feature: {feature_file}")
    print(f"  • Screenshot: {screenshot_path}")
    

def test_json_format():
    """Test with JSON format"""
    print("\n" + "=" * 60)
    print("Testing JSON Format")
    print("=" * 60)
    
    json_spec = {
        "feature": "Google Search JSON Test",
        "description": "Test using JSON format",
        "scenarios": [
            {
                "name": "Quick search test",
                "steps": [
                    "When I search for weather",
                    "Then I should see results"
                ]
            }
        ]
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/bdd/generate",
        json={"specification": json_spec}
    )
    
    assert response.status_code == 200
    result = response.json()
    print(f"✅ JSON format test passed")
    print(f"   Feature: {result['data']['feature_name']}")


def test_natural_language_format():
    """Test with natural language format"""
    print("\n" + "=" * 60)
    print("Testing Natural Language Format")
    print("=" * 60)
    
    nl_spec = """
Feature: Google Search Natural Language
Scenario: Simple search
  When I search for news
  Then I see results
"""
    
    response = requests.post(
        f"{API_BASE_URL}/api/bdd/generate",
        json={"specification": nl_spec}
    )
    
    assert response.status_code == 200
    result = response.json()
    print(f"✅ Natural language format test passed")
    print(f"   Feature: {result['data']['feature_name']}")


if __name__ == "__main__":
    print("\n🚀 Starting E2E Tests...\n")
    
    try:
        # Main E2E test with Playwright validation
        test_bdd_generation_and_execution()
        
        # Additional format tests
        test_json_format()
        test_natural_language_format()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise
