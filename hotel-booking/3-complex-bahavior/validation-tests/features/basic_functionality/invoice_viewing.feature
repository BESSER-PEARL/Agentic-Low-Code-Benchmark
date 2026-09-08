Feature: Invoice viewing and listing
  As hotel staff
  I want to view and list invoices
  So that I can track billing for bookings

  # Traceability: class Invoice (id, issued_date, amount, paid) and its
  # 1 -- 0..1 association with Booking

  Background:
    Given the hotel booking application is running and the database is empty
    And a booking exists with an invoice for amount 360.0 that is not paid

  @requirements-coverage @correctness @conformance @invoice @crud
  Scenario: Retrieve the invoice of a booking
    When I request the invoice for that booking
    Then I should see an invoice with amount 360.0
    And I should see that the invoice is not paid
    And I should see the invoice's issued date

  @requirements-coverage @correctness @invoice @crud
  Scenario: List all unpaid invoices
    When I request the list of unpaid invoices
    Then the list should include the invoice for that booking

  @requirements-coverage @correctness @invoice @crud
  Scenario: A booking without an invoice yet has no invoice to retrieve
    Given a booking exists with no invoice
    When I request the invoice for that booking
    Then I should be informed that the booking has no invoice
