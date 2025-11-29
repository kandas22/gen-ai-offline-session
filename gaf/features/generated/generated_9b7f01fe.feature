Feature: Google Search Automation
  Test search with different queries

  @smoke @search



  Background:

    Given I have a browser open

    And I am on Google




  Scenario: Search for news

    @news


    When I search for rain news

    And I press Enter

    Then I should see results



  Scenario: Search for weather


    When I search for weather

    Then I should see forecast

