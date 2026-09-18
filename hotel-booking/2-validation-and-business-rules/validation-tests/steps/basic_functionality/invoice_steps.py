"""Step definitions for invoice_viewing.feature."""
from behave import given, when, then
from steps.basic_functionality.helpers import api_post, next_id, navigate_to, wait_for_table, find_row_by_text, count_table_rows, get_cell_in_row, get_cell
from steps.basic_functionality.booking_steps import create_booking_via_api
from steps.basic_functionality.guest_and_employee_steps import create_guest_via_api, create_employee_via_api
from steps.basic_functionality.room_steps import create_room_via_api
from datetime import date

INVOICE_TABLE = "table-invoice-5"
I_COL_ID, I_COL_AMOUNT, I_COL_PAID, I_COL_ISSUED_DATE = 0, 1, 2, 3

def create_invoice_via_api(context, booking_id, amount=100.0, paid=False):
    issued_date = date.today().isoformat()
    data = {"id": next_id(context), "issued_date": issued_date, "amount": amount, "paid": paid, "booking": booking_id}
    invoice = api_post(context, "/invoice/", data)
    # Ensure response has id field for later use
    if "id" not in invoice and "id" in data:
        invoice["id"] = data["id"]
    context.current_invoice = invoice
    return invoice

@given("a booking exists with an invoice for amount {amount:f} that is not paid")
def step_booking_with_unpaid_invoice(context, amount):
    guest = create_guest_via_api(context, email="jane.doe@example.com")
    employee = create_employee_via_api(context, email="mario.rossi@hotel.com")
    create_room_via_api(context, number=101)

    booking = create_booking_via_api(context, guest_id=guest["id"], employee_id=employee["id"],
                                    room_number=101, check_in="2026-10-01", check_out="2026-10-05", price=amount)
    create_invoice_via_api(context, booking_id=booking["id"], amount=amount, paid=False)

@given("a booking exists with no invoice")
def step_booking_without_invoice(context):
    guest = create_guest_via_api(context, email="jane.doe@example.com")
    employee = create_employee_via_api(context, email="mario.rossi@hotel.com")
    create_room_via_api(context, number=101)

    booking = create_booking_via_api(context, guest_id=guest["id"], employee_id=employee["id"],
                                    room_number=101, check_in="2026-10-01", check_out="2026-10-05")
    context.no_invoice_booking = booking

@when("I request the invoice for that booking")
def step_request_booking_invoice(context):
    navigate_to(context, "/invoice")
    wait_for_table(context, INVOICE_TABLE)

@when("I request the list of unpaid invoices")
def step_request_unpaid_invoices(context):
    navigate_to(context, "/invoice")
    wait_for_table(context, INVOICE_TABLE)

@then('I should see an invoice with amount {amount:f}')
def step_see_invoice_amount(context, amount):
    navigate_to(context, "/invoice")
    wait_for_table(context, INVOICE_TABLE)
    invoice = context.current_invoice
    row = find_row_by_text(context, INVOICE_TABLE, str(invoice["id"]))
    assert row.is_visible(), f"Expected invoice {invoice['id']} to be visible"
    cell_amount = float(get_cell(context, INVOICE_TABLE, row, "amount"))
    assert cell_amount == amount, f"Expected amount {amount}, got {cell_amount}"

@then("I should see that the invoice is not paid")
def step_invoice_not_paid(context):
    invoice = context.current_invoice
    navigate_to(context, "/invoice")
    wait_for_table(context, INVOICE_TABLE)
    row = find_row_by_text(context, INVOICE_TABLE, str(invoice["id"]))
    cell_paid = get_cell(context, INVOICE_TABLE, row, "paid")
    assert cell_paid.lower() in ["no", "false", "not paid"], f"Expected unpaid invoice, got {cell_paid}"

@then("I should see the invoice's issued date")
def step_see_invoice_date(context):
    invoice = context.current_invoice
    navigate_to(context, "/invoice")
    wait_for_table(context, INVOICE_TABLE)
    row = find_row_by_text(context, INVOICE_TABLE, str(invoice["id"]))
    cell_date = get_cell(context, INVOICE_TABLE, row, "issued_date")
    assert cell_date, f"Expected issued date to be visible"

@then("the list should include the invoice for that booking")
def step_list_includes_invoice(context):
    invoice = context.current_invoice
    navigate_to(context, "/invoice")
    wait_for_table(context, INVOICE_TABLE)
    row = find_row_by_text(context, INVOICE_TABLE, str(invoice["id"]))
    assert row.is_visible(), f"Expected invoice {invoice['id']} in list"

@then("I should be informed that the booking has no invoice")
def step_informed_no_invoice(context):
    navigate_to(context, "/invoice")
    wait_for_table(context, INVOICE_TABLE)
    booking = context.no_invoice_booking
    rows = context.page.locator(f"#{INVOICE_TABLE} tbody tr").filter(has_text=str(booking["id"]))
    assert rows.count() == 0, f"Expected no invoice for booking {booking['id']}"
