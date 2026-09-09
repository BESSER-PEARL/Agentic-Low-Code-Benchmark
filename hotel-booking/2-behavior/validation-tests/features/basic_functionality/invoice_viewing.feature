Feature: Invoice viewing and listing
  As hotel staff
  I want to view and list invoices
  So that I can track billing for bookings

  # Source: nl-requirements/requirements.md, "Billing" — "A booking may have a bill
  # raised against it, but never more than one, and it may go without one entirely.
  # ... Each bill carries its own identifying number, the date it was issued, the
  # total amount due, and an indication of whether it has been settled."

  Background:
    Given the hotel booking application is running and the database is empty
    And a booking exists with an invoice for amount 360.0 that is not paid

  @correctness @completeness @invoice @crud
  Scenario: Retrieve the invoice of a booking
    When I request the invoice for that booking
    Then I should see an invoice with amount 360.0
    And I should see that the invoice is not paid
    And I should see the invoice's issued date

  @correctness @completeness @invoice @crud
  Scenario: List all unpaid invoices
    When I request the list of unpaid invoices
    Then the list should include the invoice for that booking

  @correctness @completeness @invoice @crud
  Scenario: A booking without an invoice yet has no invoice to retrieve
    Given a booking exists with no invoice
    When I request the invoice for that booking
    Then I should be informed that the booking has no invoice
