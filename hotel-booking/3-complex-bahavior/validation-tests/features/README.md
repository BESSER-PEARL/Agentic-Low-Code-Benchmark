# Feature overview

Quick reference for what each category tests and what the tags mean. See the parent
`validation-tests/README.md` for the model summary and folder layout.

## What is tested, by category

### `basic_functionality/` — plain CRUD, no business rules
- **Guests & employees**: create, read, update, delete, list
- **Rooms**: create, read, update, delete, list, uniqueness of room number
- **Bookings**: create, read, update dates, list by employee / by guest
- **Invoices**: view a booking's invoice, list unpaid invoices, handle "no invoice yet"

### `constraints/` — the model's OCL invariants and association multiplicities
- **Person contact validation**: valid/invalid email and phone formats
  (`ValidEmail`, `ValidPhoneNumber`)
- **Booking dates**: check-in ≤ check-out (`CheckInBeforeCheckOut`)
- **Booking capacity**: guest count ≤ sum of room capacities
  (`NumberOfGuestsDoesNotExceedRoomCapacity`), including adding/removing rooms
- **Booking associations**: at least 1 guest, at least 1 room, exactly 1 contact,
  exactly 1 manager, at most 1 invoice, and a room may belong to `0..*` bookings

### `complex_behavior/` — class methods and multi-step behavior
- **Price calculation**: `calculate_price()` across single/multiple rooms, with/without
  additional charges
- **Booking lifecycle**: initial status defaults, `check_in()` / `check_out()` /
  `cancel()` and their preconditions, status transitions
  (`pending_payment` → `confirmed` → ...)
- **Invoice generation**: `generate_invoice()`, rejecting a second invoice
- **Invoice payment**: `pay_invoice()`, confirming the booking, rejecting double payment

## What the tags mean

- **`@requirements-coverage`** — breadth: does *some* scenario exist for this
  capability. Asks "did we forget to test something?", not "is the answer right?"
- **`@correctness`** — the produced value/state is actually right (right price, right
  status, right stored data) — not just "didn't crash."
- **`@conformance`** — behavior traces to a *specific, named model element* (an OCL
  invariant, a multiplicity, a method signature). Asks "does the app implement exactly
  what the model says?" — distinct from correctness because a result can be "sensible"
  but still violate what the model literally specifies.

Rule of thumb applied when tagging: plain CRUD scenarios get `@requirements-coverage` +
`@correctness` (there is no specific model element to conform to beyond "CRUD works");
anything tied to an OCL invariant, a multiplicity, or a method gets all three.
