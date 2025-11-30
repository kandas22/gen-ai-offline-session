Feature: Google Search
  Search functionality tests



  Background:

    Given I am on Google




  Scenario: Search for news


    When I search for rain news

    Then I should see results

