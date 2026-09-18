Feature: Invoice generation for a booking
  As hotel staff
  I want an invoice to be generated for a booking with the correct amount
  So that the guest can be billed for the stay

  # Source: nl-requirements/requirements.md, "Things a booking can do" and "Billing" —
  # "It can produce the bill for the stay." / "A booking may have a bill raised
  # against it, but never more than one, and it may go without one entirely."

  Background:
    Given the hotel booking application is running and the database is empty
    And a guest exists with email "jane.doe@example.com"
    And an employee exists with email "mario.rossi@hotel.com"
    And a room numbered 101 exists with price 100.0
    And a booking exists for guest "jane.doe@example.com" in room 101 with agreed price 100.0 and no additional charges, from 2026-10-01 to 2026-10-04

  @complex-behavior @correctness @completeness @invoice
  Scenario: Generating an invoice for a booking that has none yet
    Given that booking has no invoice
    When I generate an invoice for that booking
    Then the operation should succeed
    And that booking should now have an invoice
    And the invoice amount should equal the booking's calculated price
    And the invoice should be marked as unpaid
    And the invoice's issued date should be today

  @complex-behavior @correctness @completeness @invoice
  Scenario: Generating an invoice for a booking that already has one is rejected
    Given an invoice has already been generated for that booking
    When I try to generate another invoice for that booking
    Then the operation should fail
    And I should see an error indicating the booking already has an invoice
