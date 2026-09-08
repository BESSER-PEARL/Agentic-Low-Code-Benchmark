Feature: Guest and employee management
  As a hotel staff member
  I want to create, view, update and delete guest and employee records
  So that the hotel keeps accurate records of the people it deals with

  # Traceability: classes Person, Guest, Employee
  # (attributes: id, name, last_name, phone_number, email)

  Background:
    Given the hotel booking application is running and the database is empty

  @requirements-coverage @correctness @conformance @guest @crud
  Scenario: Create a new guest with valid data
    When I create a guest with the following details:
      | name | last_name | phone_number | email                 |
      | Jane | Doe       | +15551234567 | jane.doe@example.com  |
    Then the operation should succeed
    And a guest with email "jane.doe@example.com" should exist
    And that guest's name should be "Jane"
    And that guest's last name should be "Doe"
    And that guest's phone number should be "+15551234567"

  @requirements-coverage @correctness @guest @crud
  Scenario: Retrieve an existing guest's details
    Given a guest exists with the following details:
      | name | last_name | phone_number | email                 |
      | Jane | Doe       | +15551234567 | jane.doe@example.com  |
    When I request the guest with email "jane.doe@example.com"
    Then I should see a guest with name "Jane", last name "Doe", phone number "+15551234567" and email "jane.doe@example.com"

  @requirements-coverage @correctness @guest @crud
  Scenario: List all registered guests
    Given the following guests exist:
      | name | last_name | email                   |
      | Jane | Doe       | jane.doe@example.com    |
      | John | Smith     | john.smith@example.com  |
    When I request the list of all guests
    Then the list should contain 2 guests
    And the list should include a guest with email "jane.doe@example.com"
    And the list should include a guest with email "john.smith@example.com"

  @requirements-coverage @correctness @guest @crud
  Scenario: Update a guest's contact information
    Given a guest exists with email "jane.doe@example.com" and phone number "+15551234567"
    When I update that guest's phone number to "+15559876543"
    Then the operation should succeed
    And that guest's phone number should be "+15559876543"

  @requirements-coverage @correctness @guest @crud
  Scenario: Delete a guest with no associated bookings
    Given a guest exists with email "jane.doe@example.com"
    And that guest has no bookings
    When I delete the guest with email "jane.doe@example.com"
    Then the operation should succeed
    And a guest with email "jane.doe@example.com" should no longer exist

  # --- Employee ---

  @requirements-coverage @correctness @conformance @employee @crud
  Scenario: Create a new employee with valid data
    When I create an employee with the following details:
      | name  | last_name | phone_number | email                 |
      | Mario | Rossi     | +15552223333 | mario.rossi@hotel.com |
    Then the operation should succeed
    And an employee with email "mario.rossi@hotel.com" should exist

  @requirements-coverage @correctness @employee @crud
  Scenario: Retrieve an existing employee's details
    Given an employee exists with the following details:
      | name  | last_name | phone_number | email                 |
      | Mario | Rossi     | +15552223333 | mario.rossi@hotel.com |
    When I request the employee with email "mario.rossi@hotel.com"
    Then I should see an employee with name "Mario", last name "Rossi" and email "mario.rossi@hotel.com"

  @requirements-coverage @correctness @employee @crud
  Scenario: Update an employee's information
    Given an employee exists with email "mario.rossi@hotel.com"
    When I update that employee's last name to "Bianchi"
    Then that employee's last name should be "Bianchi"

  @requirements-coverage @correctness @employee @crud
  Scenario: Delete an employee who manages no bookings
    Given an employee exists with email "mario.rossi@hotel.com"
    And that employee manages no bookings
    When I delete the employee with email "mario.rossi@hotel.com"
    Then the operation should succeed
    And an employee with email "mario.rossi@hotel.com" should no longer exist
