Feature: Structural constraints on booking associations
  As the system
  I want to enforce the cardinalities defined for a booking's relationships
  So that every booking remains a structurally valid record

  # Source: nl-requirements/requirements.md, "Bookings" and "Billing" — "At least one
  # guest must be listed, and there may be more. ... A booking covers at least one
  # room and may cover several. Each room is tied to zero or multiple booking
  # records. ... Each booking has one person acting as its contact ... Each booking
  # is also handled by exactly one employee" and "A booking may have a bill raised
  # against it, but never more than one, and it may go without one entirely."

  Background:
    Given the hotel booking application is running and the database is empty
    And a guest exists with email "jane.doe@example.com"
    And an employee exists with email "mario.rossi@hotel.com"
    And a room numbered 101 exists with max_people 2

  @constraints @correctness @completeness @booking
  Scenario: A booking cannot be created without at least one guest
    When I try to create a booking with no guests, room 101, contact "jane.doe@example.com" and manager "mario.rossi@hotel.com"
    Then the operation should fail
    And I should see an error indicating a booking must have at least one guest

  @constraints @correctness @completeness @booking
  Scenario: A booking cannot be created without at least one room
    When I try to create a booking with guest "jane.doe@example.com", no rooms, contact "jane.doe@example.com" and manager "mario.rossi@hotel.com"
    Then the operation should fail
    And I should see an error indicating a booking must have at least one room

  @constraints @correctness @completeness @booking
  Scenario: A booking cannot be created without a booking contact
    When I try to create a booking with guest "jane.doe@example.com", room 101, no booking contact and manager "mario.rossi@hotel.com"
    Then the operation should fail
    And I should see an error indicating a booking contact is required

  @constraints @correctness @completeness @booking
  Scenario: A booking cannot be created without a managing employee
    When I try to create a booking with guest "jane.doe@example.com", room 101, contact "jane.doe@example.com" and no manager
    Then the operation should fail
    And I should see an error indicating a managing employee is required

  @constraints @correctness @completeness @booking @invoice
  Scenario: A booking cannot have more than one invoice
    Given a booking exists with an invoice
    When I try to generate a second invoice for that booking
    Then the operation should fail
    And I should see an error indicating the booking already has an invoice

  @constraints @correctness @completeness @room @booking
  Scenario: The same room can be part of more than one booking
    Given a booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    When I create another booking for guest "jane.doe@example.com" in room 101 from 2026-11-01 to 2026-11-05
    Then the operation should succeed
    And room 101 should be part of 2 bookings

  @constraints @correctness @completeness @room
  Scenario: A room can exist without being part of any booking
    When I create a room with the following details:
      | number | max_people | description | price |
      | 104    | 2          | Single room | 70.0  |
    Then the operation should succeed
    And room 104 should be part of 0 bookings
