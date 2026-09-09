Feature: Invoice payment
  As a guest or hotel staff member
  I want to pay an invoice
  So that the corresponding booking is confirmed

  # Source: nl-requirements/requirements.md, "Billing" — "A bill offers a single
  # action: registering its payment, which reports back whether the payment went
  # through. Settling the bill is what moves the corresponding booking from
  # awaiting payment to confirmed."

  Background:
    Given the hotel booking application is running and the database is empty
    And a guest exists with email "jane.doe@example.com"
    And an employee exists with email "mario.rossi@hotel.com"
    And a room numbered 101 exists with price 100.0
    And a booking exists for guest "jane.doe@example.com" in room 101 with agreed price 100.0 and no additional charges, from 2026-10-01 to 2026-10-04
    And an invoice has been generated for that booking

  @complex-behavior @correctness @completeness @invoice
  Scenario: Paying an unpaid invoice in full succeeds
    When I pay that invoice
    Then the operation should succeed
    And the invoice should be marked as paid
    And the booking's status should be "confirmed"

  @complex-behavior @correctness @completeness @invoice
  Scenario: Paying an invoice that has already been paid is rejected
    Given that invoice has already been paid
    When I try to pay that invoice again
    Then the operation should fail
    And I should see an error indicating the invoice is already paid
