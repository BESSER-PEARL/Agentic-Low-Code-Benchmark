Feature: Booking check-in and check-out date consistency
  As the system
  I want to guarantee that a booking's check-in date is never after its check-out date
  So that stays always represent a valid time interval

  # Traceability: OCL invariant "CheckInBeforeCheckOut" on class Booking
  #   context Booking inv CheckInBeforeCheckOut: self.check_in <= self.check_out

  Background:
    Given the hotel booking application is running and the database is empty
    And a guest exists with email "jane.doe@example.com"
    And a room numbered 101 exists with max_people 2

  @constraints @correctness @conformance @booking
  Scenario: Check-in date before check-out date is accepted
    When I create a booking for guest "jane.doe@example.com" in room 101 with check-in date 2026-10-01 and check-out date 2026-10-05
    Then the operation should succeed

  @constraints @correctness @conformance @booking
  Scenario: Check-in date equal to check-out date is accepted
    When I create a booking for guest "jane.doe@example.com" in room 101 with check-in date 2026-10-01 and check-out date 2026-10-01
    Then the operation should succeed

  @constraints @correctness @conformance @booking
  Scenario: Check-in date after check-out date is rejected
    When I create a booking for guest "jane.doe@example.com" in room 101 with check-in date 2026-10-05 and check-out date 2026-10-01
    Then the operation should fail
    And I should see an error indicating the check-in date must not be after the check-out date

  @constraints @correctness @conformance @booking
  Scenario: Updating a booking so its check-in date becomes after its check-out date is rejected
    Given a booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    When I update that booking's check-in date to 2026-10-06
    Then the operation should fail
    And I should see an error indicating the check-in date must not be after the check-out date
