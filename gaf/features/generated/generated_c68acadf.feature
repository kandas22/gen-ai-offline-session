Feature: Google Search
  Test search functionality

  @smoke @search



  Background:

    Given I am on Google

    And cookies are accepted




  Scenario: Search for news

    @news


    When I search for rain news

    Then I should see results



  Scenario: Search for weather


    When I search for weather

    Then I should see forecast

