"""UI operations shared by the behavior and constraints step definitions.

These sit on top of steps.basic_functionality.helpers and add the two things the
scenarios in those folders need and plain CRUD does not: driving the booking
dialog with its relationship fields, and running an entity method from the
buttons the generated page puts next to the table.
"""
from steps.basic_functionality.helpers import (
    api_get,
    fill_text_input,
    get_modal_error,
    modal_is_visible,
    navigate_to,
    open_add_modal,
    submit_form,
    wait_for_table,
)

BOOKING_TABLE = "table-booking-1"
INVOICE_TABLE = "table-invoice-5"


# ---------------------------------------------------------------------------
# Multi-selects and lookups
# ---------------------------------------------------------------------------

def select_lookup(context, field, label):
    """Pick an option of a single-select lookup by what it displays."""
    select_elem = context.page.locator(f"#modal-input-{field}").first
    options = select_elem.locator("option")
    seen = []
    for i in range(options.count()):
        text = (options.nth(i).inner_text() or "").strip()
        value = options.nth(i).get_attribute("value") or ""
        seen.append(text)
        if value and (text == label or label in text or text in label):
            select_elem.select_option(value=value)
            return
    raise AssertionError(f"No option for {label!r} in #modal-input-{field}; options were {seen}")


_TOGGLE_OPTION = """({ label, wanted }) => {
    const boxes = Array.from(document.querySelectorAll('.bsr-modal input[type="checkbox"]'));
    for (const box of boxes) {
        const id = box.getAttribute('data-option-id') || '';
        const text = (box.parentElement?.textContent || '').trim();
        if (id === label || text === label || text.includes(label)) {
            if (box.checked !== wanted) box.parentElement.click();
            return true;
        }
    }
    return false;
}"""


def _toggle_option(context, label, wanted):
    """Set one option of a relationship multi-select.

    Options are matched on the record they stand for (data-option-id) as well as
    on their text: a guest is named in the features by email, which is what the
    option shows, while a room is named by its number, which is its key rather
    than its label.

    The dialog opens before it has fetched the records to offer, so this waits
    for the option to appear rather than reading an empty list and concluding it
    does not exist.
    """
    for _ in range(20):
        if context.page.evaluate(_TOGGLE_OPTION, {"label": str(label), "wanted": wanted}):
            context.page.wait_for_timeout(120)
            return
        context.page.wait_for_timeout(250)
    raise AssertionError(f"No multi-select option matching {label!r} in this dialog")


def tick_option(context, label):
    _toggle_option(context, label, True)


def untick_option(context, label):
    _toggle_option(context, label, False)


def fill_link_attribute(context, end, target, attribute, value):
    """Fill an association-class attribute that unfolded under a ticked option."""
    fill_text_input(context, f"{end}-{target}-{attribute}", value)


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------

def open_booking_dialog(context):
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)
    open_add_modal(context, "Booking")


def create_booking_via_ui(
    context,
    guests,
    rooms,
    contact=None,
    manager=None,
    check_in="2026-10-01",
    check_out="2026-10-05",
    agreed_prices=None,
    price="0",
    booking_id=None,
):
    """Fill and submit the booking dialog, recording how it went.

    Everything a scenario can leave out is left out on purpose: passing no rooms
    or no contact is how the association-constraint scenarios ask the application
    to refuse the booking.
    """
    from steps.basic_functionality.helpers import next_id

    open_booking_dialog(context)
    booking_id = booking_id or next_id(context)

    fill_text_input(context, "id", booking_id)
    fill_text_input(context, "check_in", check_in)
    fill_text_input(context, "check_out", check_out)
    fill_text_input(context, "price", price)

    if contact:
        select_lookup(context, "booking_contact", contact)
    if manager:
        select_lookup(context, "managed_by", manager)
    for guest in guests or []:
        tick_option(context, guest)
    for room in rooms or []:
        tick_option(context, room)
        agreed = (agreed_prices or {}).get(str(room))
        if agreed is not None:
            fill_link_attribute(context, "rooms", room, "agreed_price", agreed)

    submit_form(context)
    record_outcome(context)

    if context.operation_succeeded:
        context.current_booking = api_get(context, f"/booking/{booking_id}/")["booking"]
        context.bookings.append(context.current_booking)
    return context.current_booking


def edit_booking(context, booking_id=None):
    """Open the edit dialog of the booking the scenario is working on."""
    from steps.basic_functionality.helpers import click_edit_in_row

    booking_id = booking_id or context.current_booking["id"]
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)
    click_edit_in_row(context, BOOKING_TABLE, str(booking_id))


def save_dialog(context):
    submit_form(context)
    record_outcome(context)


def record_outcome(context):
    """A closed dialog means the application accepted the operation."""
    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")


def refresh_current_booking(context):
    context.current_booking = api_get(context, f"/booking/{context.current_booking['id']}/")["booking"]
    return context.current_booking


# ---------------------------------------------------------------------------
# Entity methods, run from the buttons beside the table
# ---------------------------------------------------------------------------

def run_method(context, route, table_id, row_text, method):
    """Select a row and run one of the method buttons on the page.

    The button reads the row selected in its source table, so the row has to be
    clicked first; the outcome then arrives either as a result popup or as an
    error toast, and both are recorded the way a dialog submit would be.
    """
    navigate_to(context, route)
    wait_for_table(context, table_id)

    row = context.page.locator(f"#{table_id} tbody tr").filter(has_text=str(row_text)).first
    assert row.count(), f"No row containing {row_text!r} in #{table_id}"
    row.click()
    context.page.wait_for_timeout(200)

    button = context.page.locator("button").filter(has_text=method).first
    assert button.count(), f"No method button for {method!r} on {route}"
    button.click()
    context.page.wait_for_timeout(1200)

    error = context.page.locator("div:has-text('Error:')").last
    has_error = error.count() > 0 and error.is_visible()
    if has_error:
        context.operation_succeeded = False
        context.operation_error = (error.inner_text() or "").strip()
    else:
        context.operation_succeeded = True
        context.operation_error = None
        context.method_result = read_result_popup(context)
    dismiss_popups(context)
    return context.operation_succeeded


def read_result_popup(context):
    popup = context.page.locator("div").filter(has_text="Result").last
    if popup.count() and popup.is_visible():
        return (popup.inner_text() or "").strip()
    return ""


def dismiss_popups(context):
    for label in ("Close", "OK", "Dismiss"):
        button = context.page.locator("button").filter(has_text=label).last
        if button.count() and button.is_visible():
            button.click()
            context.page.wait_for_timeout(150)
            return


# ---------------------------------------------------------------------------
# Reading state back out of the tables
# ---------------------------------------------------------------------------

def booking_cell(context, field, booking_id=None):
    from steps.basic_functionality.helpers import find_row_by_text, get_cell

    booking_id = booking_id or context.current_booking["id"]
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)
    row = find_row_by_text(context, BOOKING_TABLE, str(booking_id))
    return get_cell(context, BOOKING_TABLE, row, field)


def invoice_of(context, booking_id=None):
    booking_id = booking_id or context.current_booking["id"]
    invoices = api_get(context, "/invoice/")
    return [inv for inv in invoices if inv.get("booking_id") == booking_id]
