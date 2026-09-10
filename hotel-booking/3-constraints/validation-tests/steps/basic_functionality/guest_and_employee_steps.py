"""Step definitions for guest_and_employee_management.feature."""
from behave import given, when, then
from steps.basic_functionality.helpers import (
    next_id, api_post, api_put, navigate_to, wait_for_table, open_add_modal,
    fill_text_input, submit_form, modal_is_visible, get_modal_error,
    find_row_by_text, get_cell_in_row, click_edit_in_row, click_remove_in_row,
    get_row_action_error, count_table_rows
)

GUEST_TABLE = "table-guest-0"
EMPLOYEE_TABLE = "table-employee-4"

G_COL_ID, G_COL_NAME, G_COL_LAST_NAME, G_COL_PHONE, G_COL_EMAIL = 0, 1, 2, 3, 4
E_COL_ID, E_COL_NAME, E_COL_LAST_NAME, E_COL_PHONE, E_COL_EMAIL = 0, 1, 2, 3, 4

def create_guest_via_api(context, name="Jane", last_name="Doe", phone="+15551234567", email="jane.doe@example.com"):
    data = {"id": next_id(context), "name": name, "last_name": last_name, "phone_number": phone, "email": email}
    guest = api_post(context, "/guest/", data)
    # Ensure response has id field for later use
    if "id" not in guest and "id" in data:
        guest["id"] = data["id"]
    context.guests[email] = guest
    return guest

def create_employee_via_api(context, name="Mario", last_name="Rossi", phone="+15552223333", email="mario.rossi@hotel.com"):
    data = {"id": next_id(context), "name": name, "last_name": last_name, "phone_number": phone, "email": email}
    emp = api_post(context, "/employee/", data)
    # Ensure response has id field for later use
    if "id" not in emp and "id" in data:
        emp["id"] = data["id"]
    context.employees[email] = emp
    return emp

# ---------------------------------------------------------------------------
# GUEST: Given steps
# ---------------------------------------------------------------------------

@given('a guest exists with email "{email}" and phone number "{phone}"')
def step_guest_exists_with_email_phone(context, email, phone):
    create_guest_via_api(context, email=email, phone=phone)

@given('a guest exists with email "{email}"')
def step_guest_exists_with_email(context, email):
    create_guest_via_api(context, email=email)

@given("a guest exists with the following details:")
def step_guest_exists_with_details(context):
    for row in context.table:
        create_guest_via_api(context, name=row["name"], last_name=row["last_name"],
                           phone=row.get("phone_number", "+15551234567"), email=row["email"])

@given("the following guests exist:")
def step_multiple_guests_exist(context):
    for row in context.table:
        create_guest_via_api(context, name=row["name"], last_name=row["last_name"], email=row["email"])

@given("that guest has no bookings")
def step_guest_has_no_bookings(context):
    pass

# ---------------------------------------------------------------------------
# GUEST: When steps
# ---------------------------------------------------------------------------

@when("I create a guest with the following details:")
def step_create_guest_via_ui(context):
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)
    open_add_modal(context, "Guest")

    row = context.table[0]
    guest_id = next_id(context)
    fill_text_input(context, "id", guest_id)
    fill_text_input(context, "name", row["name"])
    fill_text_input(context, "last_name", row["last_name"])
    fill_text_input(context, "phone_number", row["phone_number"])
    fill_text_input(context, "email", row["email"])

    submit_form(context)

    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
        # Store the created guest so assertions can find it
        guest_data = {
            "id": guest_id,
            "name": row["name"],
            "last_name": row["last_name"],
            "phone_number": row["phone_number"],
            "email": row["email"],
        }
        context.guests[row["email"]] = guest_data
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, GUEST_TABLE)

@when('I update that guest\'s phone number to "{new_phone}"')
def step_update_guest_phone(context, new_phone):
    guest_email = next(iter(context.guests))
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)

    click_edit_in_row(context, GUEST_TABLE, guest_email)
    fill_text_input(context, "phone_number", new_phone)
    submit_form(context)

    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, GUEST_TABLE)

@when('I request the guest with email "{email}"')
def step_request_guest_by_email(context, email):
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)
    context._viewing_guest_email = email

@when("I request the list of all guests")
def step_request_guest_list(context):
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)

@when('I delete the guest with email "{email}"')
def step_delete_guest(context, email):
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)
    click_remove_in_row(context, GUEST_TABLE, email)
    context.page.wait_for_timeout(800)
    wait_for_table(context, GUEST_TABLE)

    err = get_row_action_error(context, GUEST_TABLE)
    if err:
        context.operation_succeeded = False
        context.operation_error = err
    else:
        context.operation_succeeded = True
        context.operation_error = None

# ---------------------------------------------------------------------------
# GUEST: Then steps
# ---------------------------------------------------------------------------

@then('a guest with email "{email}" should exist')
def step_guest_should_exist(context, email):
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)
    row = find_row_by_text(context, GUEST_TABLE, email)
    assert row.is_visible(), f"Expected a guest row with email {email!r} to be visible"

@then('a guest with email "{email}" should no longer exist')
def step_guest_should_not_exist(context, email):
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)
    rows = context.page.locator(f"#{GUEST_TABLE} tbody tr").filter(has_text=email)
    assert rows.count() == 0, f"Expected no guest row with email {email!r} but found one"

@then('that guest\'s name should be "{name}"')
def step_guest_name_should_be(context, name):
    guest_email = getattr(context, "_viewing_guest_email", None) or next(iter(context.guests))
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)
    row = find_row_by_text(context, GUEST_TABLE, guest_email)
    cell_value = get_cell_in_row(row, G_COL_NAME)
    assert cell_value == name, f"Expected guest name {name!r}, got {cell_value!r}"

@then('that guest\'s last name should be "{last_name}"')
def step_guest_last_name_should_be(context, last_name):
    guest_email = getattr(context, "_viewing_guest_email", None) or next(iter(context.guests))
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)
    row = find_row_by_text(context, GUEST_TABLE, guest_email)
    cell_value = get_cell_in_row(row, G_COL_LAST_NAME)
    assert cell_value == last_name, f"Expected last name {last_name!r}, got {cell_value!r}"

@then('that guest\'s phone number should be "{phone}"')
def step_guest_phone_should_be(context, phone):
    guest_email = getattr(context, "_viewing_guest_email", None) or next(iter(context.guests))
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)
    row = find_row_by_text(context, GUEST_TABLE, guest_email)
    cell_value = get_cell_in_row(row, G_COL_PHONE)
    assert cell_value == phone, f"Expected phone {phone!r}, got {cell_value!r}"

@then('I should see a guest with name "{name}", last name "{last_name}", phone number "{phone}" and email "{email}"')
def step_see_guest_details(context, name, last_name, phone, email):
    navigate_to(context, "/guest")
    wait_for_table(context, GUEST_TABLE)
    row = find_row_by_text(context, GUEST_TABLE, email)
    assert row.is_visible(), f"No row found for guest with email {email!r}"
    assert get_cell_in_row(row, G_COL_NAME) == name
    assert get_cell_in_row(row, G_COL_LAST_NAME) == last_name
    assert get_cell_in_row(row, G_COL_PHONE) == phone
    assert get_cell_in_row(row, G_COL_EMAIL) == email

@then("the list should contain {count:d} guests")
def step_guest_list_count(context, count):
    wait_for_table(context, GUEST_TABLE)
    actual = count_table_rows(context, GUEST_TABLE)
    assert actual == count, f"Expected {count} guest rows, found {actual}"

@then('the list should include a guest with email "{email}"')
def step_guest_list_includes_email(context, email):
    wait_for_table(context, GUEST_TABLE)
    row = find_row_by_text(context, GUEST_TABLE, email)
    assert row.is_visible(), f"Expected guest with email {email!r} in list"

# ---------------------------------------------------------------------------
# EMPLOYEE: Given steps
# ---------------------------------------------------------------------------

@given("an employee exists with the following details:")
def step_employee_exists_with_details(context):
    for row in context.table:
        create_employee_via_api(context, name=row["name"], last_name=row["last_name"],
                              phone=row.get("phone_number", "+15552223333"), email=row["email"])

@given('an employee exists with email "{email}"')
def step_employee_exists_with_email(context, email):
    create_employee_via_api(context, email=email)

@given("that employee manages no bookings")
def step_employee_manages_no_bookings(context):
    pass

# ---------------------------------------------------------------------------
# EMPLOYEE: When steps
# ---------------------------------------------------------------------------

@when("I create an employee with the following details:")
def step_create_employee_via_ui(context):
    navigate_to(context, "/employee")
    wait_for_table(context, EMPLOYEE_TABLE)
    open_add_modal(context, "Employee")

    row = context.table[0]
    emp_id = next_id(context)
    phone = row.get("phone_number", "+15552223333")
    fill_text_input(context, "id", emp_id)
    fill_text_input(context, "name", row["name"])
    fill_text_input(context, "last_name", row["last_name"])
    fill_text_input(context, "phone_number", phone)
    fill_text_input(context, "email", row["email"])

    submit_form(context)

    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
        # Store the created employee so assertions can find it
        emp_data = {
            "id": emp_id,
            "name": row["name"],
            "last_name": row["last_name"],
            "phone_number": phone,
            "email": row["email"],
        }
        context.employees[row["email"]] = emp_data
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, EMPLOYEE_TABLE)

@when('I request the employee with email "{email}"')
def step_request_employee_by_email(context, email):
    navigate_to(context, "/employee")
    wait_for_table(context, EMPLOYEE_TABLE)
    context._viewing_employee_email = email

@when('I update that employee\'s last name to "{last_name}"')
def step_update_employee_last_name(context, last_name):
    emp_email = next(iter(context.employees))
    navigate_to(context, "/employee")
    wait_for_table(context, EMPLOYEE_TABLE)
    click_edit_in_row(context, EMPLOYEE_TABLE, emp_email)
    fill_text_input(context, "last_name", last_name)
    submit_form(context)

    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, EMPLOYEE_TABLE)

@when('I delete the employee with email "{email}"')
def step_delete_employee(context, email):
    navigate_to(context, "/employee")
    wait_for_table(context, EMPLOYEE_TABLE)
    click_remove_in_row(context, EMPLOYEE_TABLE, email)
    context.page.wait_for_timeout(800)
    wait_for_table(context, EMPLOYEE_TABLE)

    err = get_row_action_error(context, EMPLOYEE_TABLE)
    if err:
        context.operation_succeeded = False
        context.operation_error = err
    else:
        context.operation_succeeded = True
        context.operation_error = None

# ---------------------------------------------------------------------------
# EMPLOYEE: Then steps
# ---------------------------------------------------------------------------

@then('an employee with email "{email}" should exist')
def step_employee_should_exist(context, email):
    navigate_to(context, "/employee")
    wait_for_table(context, EMPLOYEE_TABLE)
    row = find_row_by_text(context, EMPLOYEE_TABLE, email)
    assert row.is_visible(), f"Expected employee row with email {email!r}"

@then('an employee with email "{email}" should no longer exist')
def step_employee_should_not_exist(context, email):
    navigate_to(context, "/employee")
    wait_for_table(context, EMPLOYEE_TABLE)
    rows = context.page.locator(f"#{EMPLOYEE_TABLE} tbody tr").filter(has_text=email)
    assert rows.count() == 0, f"Expected no employee with email {email!r} but found one"

@then('I should see an employee with name "{name}", last name "{last_name}" and email "{email}"')
def step_see_employee_details(context, name, last_name, email):
    navigate_to(context, "/employee")
    wait_for_table(context, EMPLOYEE_TABLE)
    row = find_row_by_text(context, EMPLOYEE_TABLE, email)
    assert row.is_visible(), f"No row found for employee with email {email!r}"
    assert get_cell_in_row(row, E_COL_NAME) == name
    assert get_cell_in_row(row, E_COL_LAST_NAME) == last_name
    assert get_cell_in_row(row, E_COL_EMAIL) == email

@then('that employee\'s last name should be "{last_name}"')
def step_employee_last_name_should_be(context, last_name):
    emp_email = getattr(context, "_viewing_employee_email", None) or next(iter(context.employees))
    navigate_to(context, "/employee")
    wait_for_table(context, EMPLOYEE_TABLE)
    row = find_row_by_text(context, EMPLOYEE_TABLE, emp_email)
    cell_value = get_cell_in_row(row, E_COL_LAST_NAME)
    assert cell_value == last_name, f"Expected last name {last_name!r}, got {cell_value!r}"
