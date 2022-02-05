Feature: Todos

  Scenario: User can add todo to the list
    Given todos page is opened
    When user adds a new todo item
    Then todo item is displayed in the list

  Scenario: User can delete todo from the list
    Given todos page is opened
    And user has a todo in the list
    When user hovers over todo and clicks the cross icon
    Then todo item is not displayed in the list

  Scenario: User can modify todo title
    Given todos page is opened
    And user has a todo in the list
    When user modifies the todo title
    Then todo title is changed

  Scenario: User can mark todo as completed
    Given todos page is opened
    And user has a todo in the list
    When user marks the todo as completed
    Then todo title is displayed as completed