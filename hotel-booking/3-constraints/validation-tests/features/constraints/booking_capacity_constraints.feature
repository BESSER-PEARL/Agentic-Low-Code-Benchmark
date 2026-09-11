Feature: Booking occupancy does not exceed room capacity
  As the system
  I want to guarantee that the number of guests in a booking never exceeds
  the combined maximum occupancy of the rooms reserved in that booking
  So that rooms are never overbooked beyond their capacity

  # Source: nl-requirements/requirements.md, "Bookings" — "The total number of guests
  # listed on a booking may never be greater than the combined capacity of all the
  # rooms it covers, obtained by adding up the maximum occupancy of each of those rooms."

  Background:
    Given the hotel booking application is running and the database is empty
    And a room numbered 101 exists with max_people 2
    And a room numbered 102 exists with max_people 3
    And the following guests exist:
      | email               |
      | guest1@example.com  |
      | guest2@example.com  |
      | guest3@example.com  |
      | guest4@example.com  |
      | guest5@example.com  |
      | guest6@example.com  |

  @constraints @correctness @completeness @booking
  Scenario: Number of guests exactly equal to a single room's capacity is accepted
    When I create a booking with rooms "101" and guests "guest1@example.com, guest2@example.com"
    Then the operation should succeed

  @constraints @correctness @completeness @booking
  Scenario: Number of guests exactly equal to the combined capacity of multiple rooms is accepted
    When I create a booking with rooms "101, 102" and guests "guest1@example.com, guest2@example.com, guest3@example.com, guest4@example.com, guest5@example.com"
    Then the operation should succeed

  @constraints @correctness @completeness @booking
  Scenario: Number of guests exceeding the combined capacity of multiple rooms is rejected
    When I create a booking with rooms "101, 102" and guests "guest1@example.com, guest2@example.com, guest3@example.com, guest4@example.com, guest5@example.com, guest6@example.com"
    Then the operation should fail
    And I should see an error indicating the number of guests exceeds room capacity

  @constraints @correctness @completeness @booking
  Scenario: Adding an extra room to a booking increases its allowed guest capacity
    Given a booking exists with room "101" and guests "guest1@example.com, guest2@example.com"
    When I add room "102" to that booking
    And I add guest "guest3@example.com" to that booking
    Then the operation should succeed
