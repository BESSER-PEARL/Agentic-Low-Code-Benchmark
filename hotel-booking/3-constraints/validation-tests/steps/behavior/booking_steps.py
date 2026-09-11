"""Step definitions for the behavior features: what a booking and a bill can do.

Every action here goes through the method buttons the generated page places
beside the booking and invoice tables, which is how a user reaches these
operations - there is no form for "check in".
"""
import datetime

from behave import given, then, when

from steps.basic_functionality.guest_and_employee_steps import (
    create_employee_via_api,
    create_guest_via_api,
)
from steps.basic_functionality.helpers import api_get
from steps.basic_functionality.room_steps import create_room_via_api
from steps.support.ui import (
    BOOKING_TABLE,
    INVOICE_TABLE,
    booking_cell,
    create_booking_via_ui,
    invoice_of,
    refresh_current_booking,
    run_method,
)

# What the application does not do, stated once so the failures read the same way.
GAP = (
    "the application refused the operation but never said so: the method returned"
    " False and the page reported a successful execution, so nothing tells the"
    " user why nothing happened"
)

DEFAULT_GUEST = "jane.doe@example.com"
DEFAULT_EMPLOYEE = "mario.rossi@hotel.com"


def _guest(context, email=DEFAULT_GUEST):
    return context.guests.get(email) or create_guest_via_api(context, email=email)


def _employee(context, email=DEFAULT_EMPLOYEE):
    return context.employees.get(email) or create_employee_via_api(context, email=email)


def _booking(context, room=101, check_in="2026-10-01", check_out="2026-10-05", agreed="100"):
    _guest(context)
    _employee(context)
    create_room_via_api(context, number=room)
    create_booking_via_ui(
        context,
        guests=[DEFAULT_GUEST],
        rooms=[room],
        contact=DEFAULT_GUEST,
        manager=DEFAULT_EMPLOYEE,
        check_in=check_in,
        check_out=check_out,
        agreed_prices={str(room): agreed},
    )
    assert context.operation_succeeded, f"Could not create the booking: {context.operation_error}"
    return context.current_booking


def _run(context, method):
    return run_method(context, "/booking", BOOKING_TABLE, context.current_booking["id"], method)


# ---------------------------------------------------------------------------
# Bookings with reserved-room details
# ---------------------------------------------------------------------------

@given('a booking exists for guest "{guest}" in room {room:d} with agreed price {agreed:f} and no additional charges, from {check_in} to {check_out}')
def step_booking_with_agreed_price(context, guest, room, agreed, check_in, check_out):
    _guest(context, guest)
    _employee(context)
    create_room_via_api(context, number=room)
    create_booking_via_ui(
        context, guests=[guest], rooms=[room], contact=guest, manager=DEFAULT_EMPLOYEE,
        check_in=check_in, check_out=check_out, agreed_prices={str(room): str(agreed)},
    )
    assert context.operation_succeeded, f"Could not create the booking: {context.operation_error}"


@given('a booking exists for guest "{guest}" in room {room:d} with agreed price {agreed:f} and additional charges {charges:f}, from {check_in} to {check_out}')
def step_booking_with_charges(context, guest, room, agreed, charges, check_in, check_out):
    step_booking_with_agreed_price(context, guest, room, agreed, check_in, check_out)
    _set_link_attribute(context, room, "additional_charges", charges)


@given('a booking exists for guest "{guest}" in rooms {first:d} and {second:d} from {check_in} to {check_out}')
def step_booking_with_two_rooms(context, guest, first, second, check_in, check_out):
    _guest(context, guest)
    _employee(context)
    for number in (first, second):
        create_room_via_api(context, number=number)
    create_booking_via_ui(
        context, guests=[guest], rooms=[first, second], contact=guest,
        manager=DEFAULT_EMPLOYEE, check_in=check_in, check_out=check_out,
        agreed_prices={str(first): "0", str(second): "0"},
    )
    assert context.operation_succeeded, f"Could not create the booking: {context.operation_error}"


@given("room {room:d} is reserved in that booking at agreed price {agreed:f} with no additional charges")
def step_room_reserved_at(context, room, agreed):
    _set_link_attribute(context, room, "agreed_price", agreed)


@given("room {room:d} is reserved in that booking at agreed price {agreed:f} with additional charges {charges:f}")
def step_room_reserved_at_with_charges(context, room, agreed, charges):
    _set_link_attribute(context, room, "agreed_price", agreed)
    _set_link_attribute(context, room, "additional_charges", charges)


def _set_link_attribute(context, room, attribute, value):
    """Record one value against the room reserved in this booking."""
    from steps.support.ui import edit_booking, fill_link_attribute, save_dialog

    edit_booking(context)
    fill_link_attribute(context, "rooms", room, attribute, str(value))
    save_dialog(context)
    assert context.operation_succeeded, (
        f"Could not set {attribute} on room {room}: {context.operation_error}"
    )


# ---------------------------------------------------------------------------
# booking_price_calculation.feature
# ---------------------------------------------------------------------------

@when("the booking's price is calculated")
def step_calculate_price(context):
    _run(context, "calculate_price")


@then("the resulting price should be {expected:f}")
def step_resulting_price(context, expected):
    assert context.operation_succeeded, f"calculate_price failed: {context.operation_error}"
    actual = float(refresh_current_booking(context)["price"])
    assert actual == expected, f"Expected the price to be {expected}, got {actual}"


@then("the booking's stored price should equal the calculated price")
def step_stored_price(context):
    assert context.operation_succeeded, f"calculate_price failed: {context.operation_error}"
    shown = float(booking_cell(context, "price"))
    stored = float(refresh_current_booking(context)["price"])
    assert shown == stored, f"The table shows {shown} while the booking holds {stored}"
    assert stored != 0.0, "calculate_price left the stored price at 0"


# ---------------------------------------------------------------------------
# booking_lifecycle_transitions.feature
# ---------------------------------------------------------------------------

@when('a booking is created for guest "{guest}" in room {room:d} from {check_in} to {check_out}')
def step_booking_created(context, guest, room, check_in, check_out):
    step_booking_with_agreed_price(context, guest, room, 100.0, check_in, check_out)


@given('a confirmed booking exists for guest "{guest}" in room {room:d} from {check_in} to {check_out}')
def step_confirmed_booking(context, guest, room, check_in, check_out):
    step_booking_with_agreed_price(context, guest, room, 100.0, check_in, check_out)
    _run(context, "generate_invoice")
    invoices = invoice_of(context)
    assert invoices, "No invoice was generated, so the booking cannot be confirmed"
    run_method(context, "/invoice", INVOICE_TABLE, invoices[0]["id"], "pay_invoice")


@given('a checked-in booking exists for guest "{guest}" in room {room:d}')
def step_checked_in_booking(context, guest, room):
    step_confirmed_booking(context, guest, room, "2026-10-01", "2026-10-05")
    _run(context, "register_arrival")


@when("the guest checks in to that booking")
def step_check_in(context):
    _run(context, "register_arrival")


@when("the guest checks out of that booking")
@when("I try to check out that booking")
def step_check_out(context):
    _run(context, "register_departure")


@when("I cancel that booking")
def step_cancel(context):
    _run(context, "cancel")


@then('the booking\'s status should be "{status}"')
def step_booking_status(context, status):
    actual = booking_cell(context, "booking_status")
    assert actual == status, f"Expected the booking status to be {status!r}, the table shows {actual!r}"


@then('the booking\'s stay status should be "{status}"')
def step_stay_status(context, status):
    actual = booking_cell(context, "stay_status")
    assert actual == status, f"Expected the stay status to be {status!r}, the table shows {actual!r}"


@then("I should see an error indicating the booking must be checked in before check-out")
def step_error_not_checked_in(context):
    stay = booking_cell(context, "stay_status")
    assert stay != "checked_out", "The booking checked out without ever checking in"
    assert context.operation_error, (
        f"Departure was correctly refused - the stay is still {stay!r} - but " + GAP
    )


# ---------------------------------------------------------------------------
# invoice_generation.feature and invoice_payment.feature
# ---------------------------------------------------------------------------

@given("that booking has no invoice")
def step_no_invoice_yet(context):
    assert not invoice_of(context), "The booking already has an invoice"


@given("an invoice has been generated for that booking")
@given("an invoice has already been generated for that booking")
def step_invoice_generated(context):
    _run(context, "generate_invoice")
    invoices = invoice_of(context)
    assert invoices, f"generate_invoice produced no invoice: {context.operation_error}"
    context.current_invoice = invoices[0]


@when("I generate an invoice for that booking")
def step_generate_invoice(context):
    _run(context, "generate_invoice")


@when("I try to generate another invoice for that booking")
def step_generate_another_invoice(context):
    _run(context, "generate_invoice")


@then("that booking should now have an invoice")
def step_should_have_invoice(context):
    invoices = invoice_of(context)
    assert len(invoices) == 1, f"Expected exactly one invoice, found {len(invoices)}"
    context.current_invoice = invoices[0]


@then("the invoice amount should equal the booking's calculated price")
def step_invoice_amount(context):
    booking = refresh_current_booking(context)
    amount = float(context.current_invoice["amount"])
    assert amount == float(booking["price"]), (
        f"The invoice is for {amount} while the booking price is {booking['price']}"
    )


@then("the invoice should be marked as unpaid")
def step_invoice_unpaid(context):
    invoices = invoice_of(context)
    assert invoices and invoices[0]["paid"] is False, "The new invoice is not marked unpaid"


@then("the invoice should be marked as paid")
def step_invoice_paid(context):
    invoices = invoice_of(context)
    assert invoices and invoices[0]["paid"] is True, "The invoice is not marked paid"


@then("the invoice's issued date should be today")
def step_invoice_date(context):
    issued = str(context.current_invoice["issued_date"])
    today = datetime.date.today().isoformat()
    assert issued == today, f"Expected the invoice to be issued {today}, it says {issued}"


@when("the invoice is paid in full")
@when("I pay that invoice")
def step_pay_invoice(context):
    invoices = invoice_of(context)
    assert invoices, "There is no invoice to pay"
    context.current_invoice = invoices[0]
    run_method(context, "/invoice", INVOICE_TABLE, context.current_invoice["id"], "pay_invoice")


@given("that invoice has already been paid")
def step_already_paid(context):
    step_pay_invoice(context)


@when("I try to pay that invoice again")
def step_pay_again(context):
    run_method(context, "/invoice", INVOICE_TABLE, context.current_invoice["id"], "pay_invoice")


@then("I should see an error indicating the invoice is already paid")
def step_error_already_paid(context):
    invoices = [i for i in api_get(context, "/invoice/") if i["id"] == context.current_invoice["id"]]
    assert invoices, "The invoice disappeared"
    assert invoices[0]["paid"] is True, "The invoice is no longer marked paid"
    assert context.operation_error, (
        "The second payment was correctly refused, but " + GAP
    )
