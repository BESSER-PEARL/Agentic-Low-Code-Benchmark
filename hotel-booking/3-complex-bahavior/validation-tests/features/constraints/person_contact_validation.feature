Feature: Contact information validation for people
  As the system
  I want to enforce that guests and employees have valid contact details
  So that the hotel can reliably reach the people it deals with

  # Source: nl-requirements/requirements.md, "People involved" — "An email address
  # must have the usual shape of a mailbox name, an at sign, a domain name and a final
  # domain suffix of at least two letters. A phone number must consist of an optional
  # leading plus sign followed by between seven and fifteen digits, with nothing else
  # in it." These rules apply to both employees and guests.

  Background:
    Given the hotel booking application is running and the database is empty

  @constraints @correctness @completeness @person
  Scenario Outline: Rejecting invalid email addresses
    When I try to create a "<person_type>" with email "<email>"
    Then the operation should fail
    And I should see an error indicating the email is invalid

    Examples:
      | person_type | email                |
      | guest       | not-an-email         |
      | guest       | missing-at-sign.com  |
      | guest       | @missingusername.com |
      | guest       | spaces in@email.com  |
      | employee    | no-domain@           |

  @constraints @correctness @completeness @person
  Scenario Outline: Accepting valid email addresses
    When I try to create a "<person_type>" with email "<email>"
    Then the operation should succeed

    Examples:
      | person_type | email                     |
      | guest       | jane.doe@example.com      |
      | guest       | j.doe+bookings@example.co |
      | employee    | mario.rossi@hotel.com     |

  @constraints @correctness @completeness @person
  Scenario Outline: Rejecting invalid phone numbers
    When I try to create a "<person_type>" with phone number "<phone_number>"
    Then the operation should fail
    And I should see an error indicating the phone number is invalid

    Examples:
      | person_type | phone_number   |
      | guest       | 12345          |
      | guest       | abcdefghij     |
      | employee    | +1-555-123-456 |

  @constraints @correctness @completeness @person
  Scenario Outline: Accepting valid phone numbers
    When I try to create a "<person_type>" with phone number "<phone_number>"
    Then the operation should succeed

    Examples:
      | person_type | phone_number  |
      | guest       | +15551234567  |
      | guest       | 5551234567    |
      | employee    | +447911123456 |
