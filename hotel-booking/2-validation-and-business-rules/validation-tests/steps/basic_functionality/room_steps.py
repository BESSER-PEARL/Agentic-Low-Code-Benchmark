"""Step definitions for room_management.feature."""
from behave import given, when, then
from steps.basic_functionality.helpers import (
    api_post, navigate_to, wait_for_table, open_add_modal,
    fill_text_input, submit_form, modal_is_visible, get_modal_error,
    find_row_by_text, get_cell_in_row, click_edit_in_row, click_remove_in_row,
    count_table_rows, get_row_action_error
)

ROOM_TABLE = "table-room-2"
R_COL_NUMBER, R_COL_MAX_PEOPLE, R_COL_DESCRIPTION, R_COL_PRICE = 0, 1, 2, 3

def create_room_via_api(context, number, max_people=2, description="Standard room", price=90.0):
    """Create the room, or hand back the one already there.

    A scenario reaches this through several Given steps (its own and the ones it
    reuses), and the second call would otherwise fail on the unique room number.
    """
    if number in context.rooms:
        return context.rooms[number]
    data = {"number": number, "max_people": max_people, "description": description, "price": price}
    room = api_post(context, "/room/", data)
    # Ensure response has number field for later use
    if "number" not in room and "number" in data:
        room["number"] = data["number"]
    context.rooms[number] = room
    return room

@given("a room numbered {number:d} exists with max_people {max_people:d} and price {price:f}")
def step_room_exists(context, number, max_people, price):
    create_room_via_api(context, number=number, max_people=max_people, price=price)

@given("a room numbered {number:d} already exists")
def step_room_already_exists(context, number):
    create_room_via_api(context, number=number)

@given("a room numbered {number:d} exists with price {price:f}")
def step_room_exists_with_price(context, number, price):
    create_room_via_api(context, number=number, price=price)

@given("a room numbered {number:d} exists")
def step_room_exists_basic(context, number):
    create_room_via_api(context, number=number)

@given("the following rooms exist:")
def step_multiple_rooms_exist(context):
    for row in context.table:
        create_room_via_api(context, number=int(row["number"]), max_people=int(row.get("max_people", 2)),
                           price=float(row["price"]))

@given("that room is not part of any booking")
def step_room_not_in_booking(context):
    pass

@when("I create a room with the following details:")
def step_create_room_via_ui(context):
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    open_add_modal(context, "Room")

    row = context.table[0]
    fill_text_input(context, "number", row["number"])
    fill_text_input(context, "max_people", row["max_people"])
    fill_text_input(context, "description", row.get("description", ""))
    fill_text_input(context, "price", row["price"])

    submit_form(context)

    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, ROOM_TABLE)

@when("I try to create another room numbered {number:d}")
def step_try_create_duplicate_room(context, number):
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    open_add_modal(context, "Room")

    fill_text_input(context, "number", str(number))
    fill_text_input(context, "max_people", "2")
    fill_text_input(context, "description", "")
    fill_text_input(context, "price", "90.0")

    submit_form(context)

    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, ROOM_TABLE)

@when("I request the list of all rooms")
def step_request_room_list(context):
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)

@when("I update that room's price to {price:f}")
def step_update_room_price(context, price):
    room_number = context._current_room_number
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    click_edit_in_row(context, ROOM_TABLE, str(room_number))
    fill_text_input(context, "price", str(price))
    submit_form(context)

    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, ROOM_TABLE)

@when('I update that room\'s description to "{description}"')
def step_update_room_description(context, description):
    room_number = context._current_room_number
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    click_edit_in_row(context, ROOM_TABLE, str(room_number))
    fill_text_input(context, "description", description)
    submit_form(context)

    if not modal_is_visible(context):
        context.operation_succeeded = True
        context.operation_error = None
    else:
        context.operation_succeeded = False
        context.operation_error = get_modal_error(context)
        context.page.keyboard.press("Escape")

    wait_for_table(context, ROOM_TABLE)

@when("I delete the room numbered {number:d}")
def step_delete_room(context, number):
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    click_remove_in_row(context, ROOM_TABLE, str(number))
    context.page.wait_for_timeout(800)
    wait_for_table(context, ROOM_TABLE)

    err = get_row_action_error(context, ROOM_TABLE)
    if err:
        context.operation_succeeded = False
        context.operation_error = err
    else:
        context.operation_succeeded = True
        context.operation_error = None

@then("the list should contain {count:d} rooms")
def step_room_list_count(context, count):
    wait_for_table(context, ROOM_TABLE)
    actual = count_table_rows(context, ROOM_TABLE)
    assert actual == count, f"Expected {count} room rows, found {actual}"

@then('the list should include a room numbered {number:d}')
def step_room_list_includes(context, number):
    wait_for_table(context, ROOM_TABLE)
    row = find_row_by_text(context, ROOM_TABLE, str(number))
    assert row.is_visible(), f"Expected room {number} in list"

@then('a room numbered {number:d} should exist')
def step_room_should_exist(context, number):
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    context._current_room_number = number
    row = find_row_by_text(context, ROOM_TABLE, str(number))
    assert row.is_visible(), f"Expected room {number} to exist"

@then('a room numbered {number:d} should no longer exist')
def step_room_should_not_exist(context, number):
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    rows = context.page.locator(f"#{ROOM_TABLE} tbody tr").filter(has_text=str(number))
    assert rows.count() == 0, f"Expected no room {number} but found one"

@then("that room's maximum occupancy should be {max_people:d}")
def step_room_max_occupancy(context, max_people):
    room_number = context._current_room_number
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    row = find_row_by_text(context, ROOM_TABLE, str(room_number))
    cell_value = int(get_cell_in_row(row, R_COL_MAX_PEOPLE))
    assert cell_value == max_people, f"Expected max_people {max_people}, got {cell_value}"

@then("that room's price should be {price:f}")
def step_room_price(context, price):
    room_number = context._current_room_number
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    row = find_row_by_text(context, ROOM_TABLE, str(room_number))
    cell_value = float(get_cell_in_row(row, R_COL_PRICE))
    assert cell_value == price, f"Expected price {price}, got {cell_value}"

@then('that room\'s description should be "{description}"')
def step_room_description(context, description):
    room_number = context._current_room_number
    navigate_to(context, "/room")
    wait_for_table(context, ROOM_TABLE)
    row = find_row_by_text(context, ROOM_TABLE, str(room_number))
    cell_value = get_cell_in_row(row, R_COL_DESCRIPTION)
    assert cell_value == description, f"Expected description {description}, got {cell_value}"

