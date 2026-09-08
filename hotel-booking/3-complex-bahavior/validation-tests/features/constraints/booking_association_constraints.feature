Feature: Structural constraints on booking associations
  As the system
  I want to enforce the cardinalities defined for a booking's relationships
  So that every booking remains a structurally valid record

  # Traceability: association multiplicities in the class model:
  #   Booking.guests           : Guest     [1..*]
  #   Booking.rooms             : Room      [1..*]  (a booking has at least one room)
  #   Room -> Booking           : Booking   [0..*]  (a room may be part of zero, one, or many bookings)
  #   Booking.booking_contact   : Person    [1]
  #   Booking.managed_by        : Employee  [1]
  #   Booking.invoice           : Invoice   [0..1]

  Background:
    Given the hotel booking application is running and the database is empty
    And a guest exists with email "jane.doe@example.com"
    And an employee exists with email "mario.rossi@hotel.com"
    And a room numbered 101 exists with max_people 2

  @constraints @correctness @conformance @booking
  Scenario: A booking cannot be created without at least one guest
    When I try to create a booking with no guests, room 101, contact "jane.doe@example.com" and manager "mario.rossi@hotel.com"
    Then the operation should fail
    And I should see an error indicating a booking must have at least one guest

  @constraints @correctness @conformance @booking
  Scenario: A booking cannot be created without at least one room
    When I try to create a booking with guest "jane.doe@example.com", no rooms, contact "jane.doe@example.com" and manager "mario.rossi@hotel.com"
    Then the operation should fail
    And I should see an error indicating a booking must have at least one room

  @constraints @correctness @conformance @booking
  Scenario: A booking cannot be created without a booking contact
    When I try to create a booking with guest "jane.doe@example.com", room 101, no booking contact and manager "mario.rossi@hotel.com"
    Then the operation should fail
    And I should see an error indicating a booking contact is required

  @constraints @correctness @conformance @booking
  Scenario: A booking cannot be created without a managing employee
    When I try to create a booking with guest "jane.doe@example.com", room 101, contact "jane.doe@example.com" and no manager
    Then the operation should fail
    And I should see an error indicating a managing employee is required

  @constraints @correctness @conformance @booking @invoice
  Scenario: A booking cannot have more than one invoice
    Given a booking exists with an invoice
    When I try to generate a second invoice for that booking
    Then the operation should fail
    And I should see an error indicating the booking already has an invoice

  @constraints @correctness @conformance @room @booking
  Scenario: The same room can be part of more than one booking
    Given a booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    When I create another booking for guest "jane.doe@example.com" in room 101 from 2026-11-01 to 2026-11-05
    Then the operation should succeed
    And room 101 should be part of 2 bookings

  @constraints @correctness @conformance @room
  Scenario: A room can exist without being part of any booking
    When I create a room with the following details:
      | number | max_people | description | price |
      | 104    | 2          | Single room | 70.0  |
    Then the operation should succeed
    And room 104 should be part of 0 bookings
