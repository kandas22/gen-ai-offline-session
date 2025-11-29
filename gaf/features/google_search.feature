Feature: Google Search for Rain News
  As a user
  I want to search for rain news on Google
  So that I can get the latest rain-related news

  Scenario: Search for rain news today
    Given I am on Google homepage
    When I search for "rain news today"
    Then I should see search results
    And the results should contain news articles

  Scenario: Verify search results contain relevant content
    Given I am on Google homepage
    When I search for "rain news today"
    Then I should see at least 5 results
    And each result should have a title and URL
