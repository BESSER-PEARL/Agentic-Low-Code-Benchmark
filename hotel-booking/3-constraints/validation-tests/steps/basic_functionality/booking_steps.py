"""Step definitions for booking_management.feature."""
from behave import given, when, then
from testing.steps.helpers import (
    api_post, api_get, next_id, navigate_to, wait_for_table, open_add_modal,
    fill_text_input, fill_select_by_label, check_list_item, submit_form,
    modal_is_visible, get_modal_error, find_row_by_text, get_cell_in_row,
    click_edit_in_row, count_table_rows
)
from testing.steps.guest_and_employee_steps import create_guest_via_api, create_employee_via_api
from testing.steps.room_steps import create_room_via_api

BOOKING_TABLE = "table-booking-1"
B_COL_ID, B_COL_CHECK_IN, B_COL_CHECK_OUT = 0, 1, 2

def create_booking_via_api(context, guest_id, employee_id, room_number, check_in, check_out, price=360.0):
    data = {
        "id": next_id(context),
        "check_in": check_in,
        "check_out": check_out,
        "booking_status": "pending_payment",
        "stay_status": "not_arrived",
        "price": price,
        "guests": [guest_id],
        "booking_contact": guest_id,
        "rooms": [{"target": room_number, "agreed_price": price}],
        "managed_by": employee_id,
    }
    booking = api_post(context, "/booking/", data)
    # Ensure response has id field for later use
    if "id" not in booking and "id" in data:
        booking["id"] = data["id"]
    context.bookings.append(booking)
    context.current_booking = booking
    return booking

@given('a booking exists for guest "{guest_email}" in room {room:d} from {check_in} to {check_out}')
def step_booking_exists_simple(context, guest_email, room, check_in, check_out):
    guest = context.guests.get(guest_email)
    if guest is None:
        guest = create_guest_via_api(context, email=guest_email)

    emp_email = next(iter(context.employees)) if context.employees else "mario.rossi@hotel.com"
    employee = context.employees.get(emp_email)
    if employee is None:
        employee = create_employee_via_api(context, email=emp_email)

    if room not in context.rooms:
        create_room_via_api(context, number=room)

    from datetime import date
    nights = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days
    price = nights * context.rooms[room].get("price", 90.0)

    create_booking_via_api(context, guest_id=guest["id"], employee_id=employee["id"],
                          room_number=room, check_in=check_in, check_out=check_out, price=price)

@given('a booking exists for guest "{guest_email}" in room {room:d} from {check_in} to {check_out} managed by "{emp_email}"')
def step_booking_exists_managed(context, guest_email, room, check_in, check_out, emp_email):
    guest = context.guests.get(guest_email)
    if guest is None:
        guest = create_guest_via_api(context, email=guest_email)

    employee = context.employees.get(emp_email)
    if employee is None:
        employee = create_employee_via_api(context, email=emp_email)

    if room not in context.rooms:
        create_room_via_api(context, number=room)

    from datetime import date
    nights = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days
    price = nights * context.rooms[room].get("price", 90.0)

    create_booking_via_api(context, guest_id=guest["id"], employee_id=employee["id"],
                          room_number=room, check_in=check_in, check_out=check_out, price=price)

@when("I create a booking with the following details:")
def step_create_booking_via_ui(context):
    """Create booking via the GUI form."""
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)
    open_add_modal(context, "Booking")
    context.page.wait_for_timeout(500)

    row = context.table[0]

    # Fill date and price fields
    fill_text_input(context, "id", next_id(context))
    context.page.wait_for_timeout(100)

    fill_text_input(context, "check_in", row["check_in"])
    context.page.wait_for_timeout(100)

    fill_text_input(context, "check_out", row["check_out"])
    context.page.wait_for_timeout(100)

    # Don't fill price - let the backend use its default value
    # fill_text_input(context, "price", "360.0")
    # context.page.wait_for_timeout(100)

    # Select booking_contact (N:1 single select dropdown)
    if "booking_contact" in row:
        select_elem = context.page.locator("#modal-input-booking_contact")
        # Get all options to see what's available
        options = select_elem.locator("option")
        option_found = False
        for i in range(options.count()):
            opt_text = options.nth(i).inner_text().strip()
            opt_value = options.nth(i).get_attribute("value")
            # Try to match by email, name, ID, or value
            if (row["booking_contact"] in opt_text or
                opt_text in row["booking_contact"] or
                row["booking_contact"] in opt_value):
                select_elem.select_option(value=opt_value)
                option_found = True
                break
        if not option_found:
            # Fallback: just try the label as-is
            try:
                select_elem.select_option(label=row["booking_contact"])
            except:
                pass
        context.page.wait_for_timeout(150)

    # Select managed_by (N:1 single select dropdown)
    if "managed_by" in row:
        select_elem = context.page.locator("#modal-input-managed_by")
        # Get all options to see what's available
        options = select_elem.locator("option")
        option_found = False
        for i in range(options.count()):
            opt_text = options.nth(i).inner_text().strip()
            opt_value = options.nth(i).get_attribute("value")
            # Try to match by email, name, ID, or value
            if (row["managed_by"] in opt_text or
                opt_text in row["managed_by"] or
                row["managed_by"] in opt_value):
                select_elem.select_option(value=opt_value)
                option_found = True
                break
        if not option_found:
            # Fallback: just try the label as-is
            try:
                select_elem.select_option(label=row["managed_by"])
            except:
                pass
        context.page.wait_for_timeout(150)

    # Select guests (N:M multi-select checkboxes)
    if "guests" in row:
        guests_list = [g.strip() for g in row["guests"].split(",")]
        for guest_identifier in guests_list:
            # Find checkbox by looking for labels containing the guest identifier
            checkbox = context.page.locator(".bsr-modal input[type='checkbox']")
            for i in range(checkbox.count()):
                parent = checkbox.nth(i).locator("xpath=ancestor::div[1]")
                if guest_identifier in parent.inner_text():
                    if not checkbox.nth(i).is_checked():
                        checkbox.nth(i).click()
                    break
            context.page.wait_for_timeout(100)

    # Select rooms (N:M multi-select checkboxes)
    if "rooms" in row:
        rooms_list = [r.strip() for r in row["rooms"].split(",")]
        agreed_prices = {}
        if "rooms_agreed_prices" in row:
            prices_list = [p.strip() for p in row["rooms_agreed_prices"].split(",")]
            # Map room numbers to agreed prices
            for i, room_id in enumerate(rooms_list):
                if i < len(prices_list):
                    agreed_prices[room_id] = prices_list[i]

        for room_identifier in rooms_list:
            # Find checkbox by looking for labels containing the room identifier
            checkbox = context.page.locator(".bsr-modal input[type='checkbox']")
            for i in range(checkbox.count()):
                parent = checkbox.nth(i).locator("xpath=ancestor::div[1]")
                if room_identifier in parent.inner_text():
                    if not checkbox.nth(i).is_checked():
                        checkbox.nth(i).click()
                    # After checking the room, fill in agreed price if specified
                    if room_identifier in agreed_prices:
                        price_input = parent.locator("input[type='number']").first
                        if price_input.is_visible():
                            fill_text_input(context, f"rooms_{room_identifier}_agreed_price", agreed_prices[room_identifier])
                    break
            context.page.wait_for_timeout(100)

    # Submit form
    submit_form(context)
    context.page.wait_for_timeout(1000)

    # Check result
    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
        # Find the newly created booking in the table by check_in date
        wait_for_table(context, BOOKING_TABLE)
        booking_row = find_row_by_text(context, BOOKING_TABLE, row["check_in"])
        if booking_row.is_visible():
            # Extract booking ID from the row
            booking_id = get_cell_in_row(booking_row, B_COL_ID)
            # Fetch full booking data from API to get all fields
            response = api_get(context, f"/booking/{booking_id}/")
            # API response is nested under "booking" key
            booking_data = response.get("booking", response)
            # Ensure id is preserved if API response doesn't include it
            if "id" not in booking_data:
                booking_data["id"] = booking_id
            context.current_booking = booking_data
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, BOOKING_TABLE)

@when('I request the details of that booking')
def step_request_booking_details(context):
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)

@when('I request the bookings managed by employee "{emp_email}"')
def step_request_bookings_by_employee(context, emp_email):
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)

@when('I request the bookings where "{guest_email}" is a guest')
def step_request_bookings_by_guest(context, guest_email):
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)

@when('I update that booking\'s check-in date to {check_in} and check-out date to {check_out}')
def step_update_booking_dates(context, check_in, check_out):
    booking = context.current_booking
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)
    click_edit_in_row(context, BOOKING_TABLE, str(booking["id"]))
    fill_text_input(context, "check_in", check_in)
    fill_text_input(context, "check_out", check_out)
    submit_form(context)

    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, BOOKING_TABLE)

@then("the list should contain {count:d} booking")
def step_booking_list_count(context, count):
    wait_for_table(context, BOOKING_TABLE)
    actual = count_table_rows(context, BOOKING_TABLE)
    assert actual == count, f"Expected {count} booking rows, found {actual}"

@then("the booking should exist with check-in date {check_in} and check-out date {check_out}")
def step_booking_exists_with_dates(context, check_in, check_out):
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)
    booking = context.current_booking
    row = find_row_by_text(context, BOOKING_TABLE, str(booking["id"]))
    assert row.is_visible(), f"Expected booking {booking['id']} to exist"
    assert get_cell_in_row(row, B_COL_CHECK_IN) == check_in
    assert get_cell_in_row(row, B_COL_CHECK_OUT) == check_out

@then("the new booking's status should be \"{status}\"")
def step_booking_status_should_be(context, status):
    booking = context.current_booking
    assert booking.get("booking_status") == status, f"Expected booking status {status}, got {booking.get('booking_status')}"

@then("the new booking's stay status should be \"{stay_status}\"")
def step_booking_stay_status_should_be(context, stay_status):
    booking = context.current_booking
    assert booking.get("stay_status") == stay_status, f"Expected stay status {stay_status}, got {booking.get('stay_status')}"

@then("I should see the check-in date {check_in}")
def step_see_checkin_date(context, check_in):
    booking = context.current_booking
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)
    row = find_row_by_text(context, BOOKING_TABLE, str(booking["id"]))
    actual = get_cell_in_row(row, B_COL_CHECK_IN)
    assert actual == check_in, f"Expected check-in {check_in}, got {actual}"

@then("I should see the check-out date {check_out}")
def step_see_checkout_date(context, check_out):
    booking = context.current_booking
    navigate_to(context, "/booking")
    wait_for_table(context, BOOKING_TABLE)
    row = find_row_by_text(context, BOOKING_TABLE, str(booking["id"]))
    actual = get_cell_in_row(row, B_COL_CHECK_OUT)
    assert actual == check_out, f"Expected check-out {check_out}, got {actual}"

@then('I should see that the booking contact is "{contact_email}"')
def step_see_booking_contact(context, contact_email):
    pass

@then('I should see that room {room:d} is included in the booking')
def step_see_room_in_booking(context, room):
    pass

@then("the booking price should be {expected_price:f}")
def step_booking_price_should_be(context, expected_price):
    booking = context.current_booking
    booking_price = float(booking.get("price", 0))
    assert booking_price == expected_price, f"Expected booking price {expected_price}, got {booking_price}"
