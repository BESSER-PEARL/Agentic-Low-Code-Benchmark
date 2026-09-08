Feature: Booking management
  As hotel staff
  I want to create, view, update and list bookings
  So that stays can be organized for guests

  # Source: nl-requirements/requirements.md, "Bookings" — "A booking is identified by
  # its own number and records an arrival date and a departure date. ... Each booking
  # has one person acting as its contact ... each booking lists the guests who will
  # actually stay ... each booking is also handled by exactly one employee ... A
  # booking covers at least one room and may cover several."

  Background:
    Given the hotel booking application is running and the database is empty
    And a guest exists with email "jane.doe@example.com"
    And an employee exists with email "mario.rossi@hotel.com"
    And a room numbered 101 exists with max_people 2 and price 90.0

  @correctness @completeness @booking @crud
  Scenario: Create a new booking
    When I create a booking with the following details:
      | check_in   | check_out  | booking_contact       | guests                | rooms | managed_by             |
      | 2026-11-01 | 2026-11-05 | jane.doe@example.com  | jane.doe@example.com  | 101   | mario.rossi@hotel.com  |
    Then the operation should succeed
    And the booking should exist with check-in date 2026-10-01 and check-out date 2026-10-05
    And the new booking's status should be "pending_payment"
    And the new booking's stay status should be "not_arrived"

  @correctness @completeness @booking @crud
  Scenario: Retrieve booking details
    Given a booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    When I request the details of that booking
    Then I should see the check-in date 2026-10-01
    And I should see the check-out date 2026-10-05
    And I should see that the booking contact is "jane.doe@example.com"
    And I should see that room 101 is included in the booking

  @correctness @completeness @booking @crud
  Scenario: List all bookings managed by an employee
    Given a booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05 managed by "mario.rossi@hotel.com"
    When I request the bookings managed by employee "mario.rossi@hotel.com"
    Then the list should contain 1 booking

  @correctness @completeness @booking @crud
  Scenario: List all bookings for a guest
    Given a booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    When I request the bookings where "jane.doe@example.com" is a guest
    Then the list should contain 1 booking

  @correctness @completeness @booking @crud
  Scenario: Update the check-in and check-out dates of a booking
    Given a booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    When I update that booking's check-in date to 2026-10-02 and check-out date to 2026-10-06
    Then the operation should succeed
    And the booking should exist with check-in date 2026-10-02 and check-out date 2026-10-06
