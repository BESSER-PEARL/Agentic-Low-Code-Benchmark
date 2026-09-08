Feature: Room management
  As a hotel staff member
  I want to create, view, update and delete rooms
  So that the hotel can manage its room inventory

  # Traceability: class Room (number, max_people, description, price)

  Background:
    Given the hotel booking application is running and the database is empty

  @requirements-coverage @correctness @conformance @room @crud
  Scenario: Create a new room
    When I create a room with the following details:
      | number | max_people | description            | price |
      | 101    | 2          | Double room, sea view  | 90.0  |
    Then the operation should succeed
    And a room numbered 101 should exist
    And that room's maximum occupancy should be 2
    And that room's price should be 90.0

  @requirements-coverage @correctness @conformance @room @crud
  Scenario: Room numbers are unique
    Given a room numbered 101 already exists
    When I try to create another room numbered 101
    Then the operation should fail
    And I should see an error indicating the room number is already in use

  @requirements-coverage @correctness @room @crud
  Scenario: List all rooms
    Given the following rooms exist:
      | number | max_people | price |
      | 101    | 2          | 90.0  |
      | 102    | 4          | 140.0 |
    When I request the list of all rooms
    Then the list should contain 2 rooms

  @requirements-coverage @correctness @room @crud
  Scenario: Update a room's price and description
    Given a room numbered 101 exists with price 90.0
    When I update that room's price to 99.0
    And I update that room's description to "Renovated double room, sea view"
    Then that room's price should be 99.0
    And that room's description should be "Renovated double room, sea view"

  @requirements-coverage @correctness @room @crud
  Scenario: Delete a room that is not part of any booking
    Given a room numbered 103 exists
    And that room is not part of any booking
    When I delete the room numbered 103
    Then the operation should succeed
    And a room numbered 103 should no longer exist
