"""Step definitions for the booking constraint features: which relationships a
booking must have, how many guests its rooms can hold, and its date order."""
from behave import given, then, when

from steps.basic_functionality.guest_and_employee_steps import (
    create_employee_via_api,
    create_guest_via_api,
)
from steps.basic_functionality.helpers import api_get
from steps.basic_functionality.room_steps import create_room_via_api
from steps.support.ui import (
    BOOKING_TABLE,
    create_booking_via_ui,
    edit_booking,
    save_dialog,
    tick_option,
    untick_option,
    fill_link_attribute,
)

DEFAULT_GUEST = "jane.doe@example.com"
DEFAULT_EMPLOYEE = "mario.rossi@hotel.com"


def _guest(context, email):
    return context.guests.get(email) or create_guest_via_api(context, email=email)


def _employee(context, email=DEFAULT_EMPLOYEE):
    return context.employees.get(email) or create_employee_via_api(context, email=email)


def _split(value):
    return [part.strip() for part in value.split(",") if part.strip()]


# ---------------------------------------------------------------------------
# Background pieces the constraint features add
# ---------------------------------------------------------------------------

@given("a room numbered {number:d} exists with max_people {max_people:d}")
def step_room_with_capacity(context, number, max_people):
    create_room_via_api(context, number=number, max_people=max_people)


# ---------------------------------------------------------------------------
# booking_association_constraints.feature
# ---------------------------------------------------------------------------

@when('I try to create a booking with no guests, room {room:d}, contact "{contact}" and manager "{manager}"')
def step_booking_without_guests(context, room, contact, manager):
    _guest(context, contact)
    _employee(context, manager)
    create_booking_via_ui(
        context, guests=[], rooms=[room], contact=contact, manager=manager,
        agreed_prices={str(room): "90"},
    )


@when('I try to create a booking with guest "{guest}", no rooms, contact "{contact}" and manager "{manager}"')
def step_booking_without_rooms(context, guest, contact, manager):
    _guest(context, guest)
    _guest(context, contact)
    _employee(context, manager)
    create_booking_via_ui(context, guests=[guest], rooms=[], contact=contact, manager=manager)


@when('I try to create a booking with guest "{guest}", room {room:d}, no booking contact and manager "{manager}"')
def step_booking_without_contact(context, guest, room, manager):
    _guest(context, guest)
    _employee(context, manager)
    create_booking_via_ui(
        context, guests=[guest], rooms=[room], contact=None, manager=manager,
        agreed_prices={str(room): "90"},
    )


@when('I try to create a booking with guest "{guest}", room {room:d}, contact "{contact}" and no manager')
def step_booking_without_manager(context, guest, room, contact):
    _guest(context, guest)
    _guest(context, contact)
    create_booking_via_ui(
        context, guests=[guest], rooms=[room], contact=contact, manager=None,
        agreed_prices={str(room): "90"},
    )


@then("I should see an error indicating a booking must have at least one guest")
def step_error_needs_guest(context):
    _assert_error_mentions(context, "guest")


@then("I should see an error indicating a booking must have at least one room")
def step_error_needs_room(context):
    _assert_error_mentions(context, "room")


@then("I should see an error indicating a booking contact is required")
def step_error_needs_contact(context):
    _assert_error_mentions(context, "contact", "person", "required")


@then("I should see an error indicating a managing employee is required")
def step_error_needs_manager(context):
    _assert_error_mentions(context, "managed", "employee", "required")


def _assert_error_mentions(context, *words):
    assert context.operation_error, "Expected an error message but the dialog showed none"
    lowered = context.operation_error.lower()
    assert any(word in lowered for word in words), (
        f"Expected the error to mention one of {words}, got {context.operation_error!r}"
    )


@given("a booking exists with an invoice")
def step_booking_with_invoice(context):
    from steps.support.ui import run_method

    guest = _guest(context, DEFAULT_GUEST)
    employee = _employee(context)
    create_room_via_api(context, number=101)
    create_booking_via_ui(
        context, guests=[DEFAULT_GUEST], rooms=[101], contact=DEFAULT_GUEST,
        manager=DEFAULT_EMPLOYEE, agreed_prices={"101": "100"},
    )
    assert context.operation_succeeded, f"Could not create the booking: {context.operation_error}"
    run_method(context, "/booking", BOOKING_TABLE, context.current_booking["id"], "generate_invoice")
    del guest, employee


@when("I try to generate a second invoice for that booking")
def step_second_invoice(context):
    from steps.support.ui import run_method

    run_method(context, "/booking", BOOKING_TABLE, context.current_booking["id"], "generate_invoice")


@then("I should see an error indicating the booking already has an invoice")
def step_error_already_invoiced(context):
    invoices = [i for i in api_get(context, "/invoice/")
                if i.get("booking_id") == context.current_booking["id"]]
    assert len(invoices) <= 1, f"The booking ended up with {len(invoices)} invoices"
    assert context.operation_error, (
        "The second invoice was correctly refused - the booking still has "
        f"{len(invoices)} - but the application never said so: the method returned"
        " False and the page reported a successful execution, so nothing tells the"
        " user why no invoice appeared"
    )


@when('I create another booking for guest "{guest}" in room {room:d} from {check_in} to {check_out}')
def step_another_booking(context, guest, room, check_in, check_out):
    _guest(context, guest)
    _employee(context)
    create_booking_via_ui(
        context, guests=[guest], rooms=[room], contact=guest, manager=DEFAULT_EMPLOYEE,
        check_in=check_in, check_out=check_out, agreed_prices={str(room): "90"},
    )


@then("room {room:d} should be part of {count:d} bookings")
def step_room_booking_count(context, room, count):
    links = [link for link in api_get(context, "/reservedroom/") if link.get("rooms_id") == room]
    assert len(links) == count, f"Expected room {room} in {count} bookings, found {len(links)}"


# ---------------------------------------------------------------------------
# booking_capacity_constraints.feature
# ---------------------------------------------------------------------------

@when('I create a booking with rooms "{rooms}" and guests "{guests}"')
def step_booking_with_rooms_and_guests(context, rooms, guests):
    guest_emails = _split(guests)
    room_numbers = _split(rooms)
    for email in guest_emails:
        _guest(context, email)
    _employee(context)
    create_booking_via_ui(
        context,
        guests=guest_emails,
        rooms=room_numbers,
        contact=guest_emails[0],
        manager=DEFAULT_EMPLOYEE,
        agreed_prices={room: "90" for room in room_numbers},
    )


@given('a booking exists with room "{rooms}" and guests "{guests}"')
@given('a booking exists with rooms "{rooms}" and guests "{guests}"')
def step_given_booking_with_rooms_and_guests(context, rooms, guests):
    step_booking_with_rooms_and_guests(context, rooms, guests)
    assert context.operation_succeeded, f"Could not create the booking: {context.operation_error}"


@when('I add room "{room}" to that booking')
def step_add_room(context, room):
    edit_booking(context)
    tick_option(context, room)
    fill_link_attribute(context, "rooms", room, "agreed_price", "90")
    save_dialog(context)


@when('I add guest "{email}" to that booking')
def step_add_guest(context, email):
    _guest(context, email)
    edit_booking(context)
    tick_option(context, email)
    save_dialog(context)


@when('I try to remove room "{room}" from that booking')
def step_remove_room(context, room):
    edit_booking(context)
    untick_option(context, room)
    save_dialog(context)


@then("I should see an error indicating the number of guests exceeds room capacity")
def step_error_over_capacity(context):
    _assert_error_mentions(context, "capacity", "guests", "exceed")


# ---------------------------------------------------------------------------
# booking_date_constraints.feature
# ---------------------------------------------------------------------------

@when('I create a booking for guest "{guest}" in room {room:d} with check-in date {check_in} and check-out date {check_out}')
def step_create_booking_with_dates(context, guest, room, check_in, check_out):
    _guest(context, guest)
    _employee(context)
    create_booking_via_ui(
        context, guests=[guest], rooms=[room], contact=guest, manager=DEFAULT_EMPLOYEE,
        check_in=check_in, check_out=check_out, agreed_prices={str(room): "90"},
    )


@when("I update that booking's check-in date to {check_in}")
def step_update_check_in(context, check_in):
    from steps.basic_functionality.helpers import fill_text_input

    edit_booking(context)
    fill_text_input(context, "check_in", check_in)
    save_dialog(context)


@then("I should see an error indicating the check-in date must not be after the check-out date")
def step_error_dates(context):
    _assert_error_mentions(context, "check_in", "check-in", "checkinbeforecheckout", "date")
