Feature: Google Search
  Auto-generated test for Google Search



  Background:

    Given I open a browser

    And I navigate to Google




  Scenario: Search for rain news


    When I search for rain news

    Then I should see results



  Scenario: Search for weather


    When I search for weather

    Then I should see forecast

