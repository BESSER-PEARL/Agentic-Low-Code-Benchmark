Feature: Contact information validation for people
  As the system
  I want to enforce that guests and employees have valid contact details
  So that the hotel can reliably reach the people it deals with

  # Traceability: OCL invariants "ValidEmail" and "ValidPhoneNumber" on class Person,
  # inherited by both Guest and Employee
  #   context Person inv ValidEmail: self.email.matches('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
  #   context Person inv ValidPhoneNumber: self.phone_number.matches('^\+?[0-9]{7,15}$')

  Background:
    Given the hotel booking application is running and the database is empty

  @constraints @correctness @conformance @person
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

  @constraints @correctness @conformance @person
  Scenario Outline: Accepting valid email addresses
    When I try to create a "<person_type>" with email "<email>"
    Then the operation should succeed

    Examples:
      | person_type | email                     |
      | guest       | jane.doe@example.com      |
      | guest       | j.doe+bookings@example.co |
      | employee    | mario.rossi@hotel.com     |

  @constraints @correctness @conformance @person
  Scenario Outline: Rejecting invalid phone numbers
    When I try to create a "<person_type>" with phone number "<phone_number>"
    Then the operation should fail
    And I should see an error indicating the phone number is invalid

    Examples:
      | person_type | phone_number   |
      | guest       | 12345          |
      | guest       | abcdefghij     |
      | employee    | +1-555-123-456 |

  @constraints @correctness @conformance @person
  Scenario Outline: Accepting valid phone numbers
    When I try to create a "<person_type>" with phone number "<phone_number>"
    Then the operation should succeed

    Examples:
      | person_type | phone_number  |
      | guest       | +15551234567  |
      | guest       | 5551234567    |
      | employee    | +447911123456 |
