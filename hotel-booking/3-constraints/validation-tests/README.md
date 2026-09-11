# Acceptance Tests

This directory contains the acceptance tests for the hotel booking application
described in `../nl-requirements/requirements.md`.

The tests are derived from those natural-language requirements and describe the
expected observable behavior of the application. They are expressed using the
Gherkin/Behave approach and are used to evaluate whether a generated application
conforms to the specified requirements.

## Requirements summary

The requirements describe a hotel booking and stay management system:

- **People**: one uniform record for every person (a unique id, first name, family
  name, phone number, email). Employees and guests are both people, with the same
  contact rules. Email addresses and phone numbers must follow a specific format.
- **Rooms**: identified by room number, with a maximum occupancy, a description and
  a standard nightly price.
- **Bookings**: identified by their own number, with an arrival date and a departure
  date (arrival never after departure). Each booking has one contact person, at
  least one guest actually staying, exactly one responsible employee, and at least
  one room (a room may belong to any number of bookings, or none). The total number
  of guests may never exceed the combined capacity of the booked rooms.
- **Booking state**: two states are tracked automatically, never set by hand — a
  commercial state (awaiting payment / confirmed / cancelled) and a stay state (not
  arrived / checked in / checked out). A booking can produce its bill, register
  arrival, register departure, be cancelled, and compute the amount owed.
- **Billing**: a booking may have at most one bill, and may have none. A bill has an
  id, an issue date, a total amount and a paid/unpaid status, and offers a single
  action to register its payment — which is what moves the booking from awaiting
  payment to confirmed.

## Organization

Scenarios are grouped by **what kind of behavior they exercise**, under
`features/`:

```
features/
├── basic_functionality/    Plain CRUD on the system's records
│   ├── guest_and_employee_management.feature
│   ├── room_management.feature
│   ├── booking_management.feature
│   └── invoice_viewing.feature
├── constraints/             Rules a record must always satisfy
│   ├── person_contact_validation.feature       (email / phone format)
│   ├── booking_date_constraints.feature         (arrival never after departure)
│   ├── booking_capacity_constraints.feature      (guests never exceed room capacity)
│   └── booking_association_constraints.feature   (who/what a booking must have, and how many)
└── complex_behavior/        The actions a booking or bill can perform
    ├── booking_price_calculation.feature   (computing the amount owed)
    ├── booking_lifecycle_transitions.feature (arrival / departure / cancellation + state)
    ├── invoice_generation.feature           (producing a bill)
    └── invoice_payment.feature              (registering a bill's payment)
```

## What is tested, by category

### `basic_functionality/` — plain CRUD, no business rules
- **Guests & employees**: create, read, update, delete, list
- **Rooms**: create, read, update, delete, list, uniqueness of room number
- **Bookings**: create, read, update dates, list by employee / by guest
- **Invoices**: view a booking's bill, list unpaid bills, handle "no bill yet"

### `behavior/` — the actions a booking or bill can perform
- **Price calculation**: computing the amount owed across single/multiple rooms,
  with/without additional charges
- **Booking lifecycle**: initial state, registering arrival/departure, cancelling a
  booking and its preconditions, how the commercial and stay states change over time
- **Invoice generation**: producing a bill for a booking, rejecting a second one
- **Invoice payment**: registering a bill's payment, confirming the booking,
  rejecting a duplicate payment

### `constraints/` — rules a record must always satisfy
- **Person contact validation**: valid/invalid email and phone formats
- **Booking dates**: arrival must never fall after departure
- **Booking capacity**: guest count must never exceed the combined capacity of the
  booked rooms, including when rooms are added or removed
- **Booking associations**: at least one guest, at least one room, exactly one
  contact, exactly one responsible employee, at most one bill, and a room may
  belong to any number of bookings, or none

## Notes on assumptions

`requirements.md` is treated as authoritative and complete: every scenario below is
derived directly from a sentence in that document, and each feature file's header
comment quotes the requirement it comes from. Where the requirements describe a rule
in prose but leave the exact algorithm or precondition unstated (e.g. the precise
pricing formula, or what "released" means when a booking is cancelled), a reasonable,
explicit assumption is stated in a comment at the top of the relevant feature file so
it can be adjusted if the intended behavior differs.

## Running the tests

The scenarios drive the **generated interface** with a real browser, so the
application under test has to be running first — backend and frontend both.
`BENCH_API` and `BENCH_UI` point the suite at them (default
`http://localhost:8000` and `http://localhost:3000`). Start from an empty
database: several scenarios say so in their background and assert on counts.

```bash
behave features/                      # everything
behave features/basic_functionality/  # one group
```

Needs `behave`, `playwright` and `requests`, plus `playwright install chromium`.

## Recorded results

Every number this benchmark reports is backed by a stored run under `runs/`:
the raw `behave` output for each feature folder, next to a `manifest.json`
recording the versions it ran against and totals parsed from those same logs.
`python record_run.py --help` shows how to record one. See `runs/README.md` for
how to read them, including why a failing scenario is not automatically a defect.
