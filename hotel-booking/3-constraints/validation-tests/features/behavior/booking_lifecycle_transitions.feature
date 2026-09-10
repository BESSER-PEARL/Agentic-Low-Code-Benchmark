Feature: Booking lifecycle: check-in, check-out and cancellation
  As hotel staff
  I want the booking and stay status to change correctly as guests arrive, stay and leave,
  or as a booking is canceled
  So that the state of every booking always reflects reality

  # Source: nl-requirements/requirements.md, "Things a booking can do" and "How a
  # booking's state is tracked" — "It can register the arrival of the guests, which
  # moves the stay from not-yet-arrived to checked in. It can register their
  # departure ... It can be cancelled..." Both the commercial state (awaiting
  # payment / confirmed / cancelled) and the stay state (not arrived / checked in /
  # checked out) are worked out automatically, never set by hand.

  Background:
    Given the hotel booking application is running and the database is empty
    And a guest exists with email "jane.doe@example.com"
    And an employee exists with email "mario.rossi@hotel.com"
    And a room numbered 101 exists with max_people 2

  @complex-behavior @correctness @completeness @booking @lifecycle
  Scenario: A newly created booking starts as pending payment and not arrived
    When a booking is created for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    Then the booking's status should be "pending_payment"
    And the booking's stay status should be "not_arrived"

  @complex-behavior @correctness @completeness @booking @lifecycle @invoice
  Scenario: A booking becomes confirmed once its invoice is paid
    Given a booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    And an invoice has been generated for that booking
    When the invoice is paid in full
    Then the booking's status should be "confirmed"

  @complex-behavior @correctness @completeness @booking @lifecycle
  Scenario: Checking in a confirmed booking succeeds
    Given a confirmed booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    When the guest checks in to that booking
    Then the operation should succeed
    And the booking's stay status should be "checked_in"

  @complex-behavior @correctness @completeness @booking @lifecycle
  Scenario: Checking out a booking that has checked in succeeds
    Given a checked-in booking exists for guest "jane.doe@example.com" in room 101
    When the guest checks out of that booking
    Then the operation should succeed
    And the booking's stay status should be "checked_out"

  @complex-behavior @correctness @completeness @booking @lifecycle
  Scenario: Checking out a booking that never checked in is rejected
    Given a confirmed booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    When I try to check out that booking
    Then the operation should fail
    And I should see an error indicating the booking must be checked in before check-out

  @complex-behavior @correctness @completeness @booking @lifecycle
  Scenario: Cancelling a booking before the guest has arrived succeeds
    Given a booking exists for guest "jane.doe@example.com" in room 101 from 2026-10-01 to 2026-10-05
    When I cancel that booking
    Then the operation should succeed
    And the booking's status should be "canceled"
