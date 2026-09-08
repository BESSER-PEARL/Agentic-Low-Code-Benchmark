Feature: Booking price calculation
  As the system
  I want to compute the total price of a booking from its reserved rooms
  So that guests and staff see an accurate cost for the stay

  # Source: nl-requirements/requirements.md, "Things a booking can do" — "it can
  # compute and return the amount owed, adding up the agreed room prices over the
  # nights booked together with the extra charges recorded."
  # Assumed formula: price = sum over reserved rooms of (agreed_price * nights + additional_charges)

  Background:
    Given the hotel booking application is running and the database is empty
    And a guest exists with email "jane.doe@example.com"
    And an employee exists with email "mario.rossi@hotel.com"

  @complex-behavior @correctness @completeness @booking @pricing
  Scenario: Price of a booking with a single room and no additional charges
    Given a room numbered 101 exists with price 100.0
    And a booking exists for guest "jane.doe@example.com" in room 101 with agreed price 100.0 and no additional charges, from 2026-10-01 to 2026-10-04
    When the booking's price is calculated
    Then the resulting price should be 300.0

  @complex-behavior @correctness @completeness @booking @pricing
  Scenario: Price of a booking with a single room and additional charges
    Given a room numbered 101 exists with price 100.0
    And a booking exists for guest "jane.doe@example.com" in room 101 with agreed price 100.0 and additional charges 25.0, from 2026-10-01 to 2026-10-04
    When the booking's price is calculated
    Then the resulting price should be 325.0

  @complex-behavior @correctness @completeness @booking @pricing
  Scenario: Price of a booking with multiple rooms
    Given a room numbered 101 exists with price 100.0
    And a room numbered 102 exists with price 150.0
    And a booking exists for guest "jane.doe@example.com" in rooms 101 and 102 from 2026-10-01 to 2026-10-03
    And room 101 is reserved in that booking at agreed price 100.0 with no additional charges
    And room 102 is reserved in that booking at agreed price 150.0 with additional charges 20.0
    When the booking's price is calculated
    Then the resulting price should be 520.0

  @complex-behavior @correctness @completeness @booking @pricing
  Scenario: The booking's stored price is kept up to date after calculation
    Given a room numbered 101 exists with price 100.0
    And a booking exists for guest "jane.doe@example.com" in room 101 with agreed price 100.0 and no additional charges, from 2026-10-01 to 2026-10-04
    When the booking's price is calculated
    Then the booking's stored price should equal the calculated price
