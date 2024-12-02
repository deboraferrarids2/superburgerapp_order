Feature: Order Management

  Scenario: Create an order without a user and add items to it
    Given I create an order without a user
    Then I should receive an order ID and a session token
    When I add an item to the order with session token
    When I attempt to create a payment link for the order
