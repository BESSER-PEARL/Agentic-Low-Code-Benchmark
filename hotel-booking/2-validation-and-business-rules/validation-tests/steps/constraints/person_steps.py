"""Step definitions for constraints/person_contact_validation.feature."""
from behave import then, when

from steps.basic_functionality.helpers import (
    fill_text_input,
    navigate_to,
    next_id,
    open_add_modal,
    wait_for_table,
)
from steps.support.ui import record_outcome
from steps.basic_functionality.helpers import submit_form

GUEST_TABLE = "table-guest-0"
EMPLOYEE_TABLE = "table-employee-4"

_SCREEN = {
    "guest": ("/guest", GUEST_TABLE, "Guest"),
    "employee": ("/employee", EMPLOYEE_TABLE, "Employee"),
}

VALID_EMAIL = "valid.person@example.com"
VALID_PHONE = "+15551234567"


def _create_person(context, person_type, email, phone):
    route, table, label = _SCREEN[person_type]
    navigate_to(context, route)
    wait_for_table(context, table)
    open_add_modal(context, label)

    fill_text_input(context, "id", next_id(context))
    fill_text_input(context, "name", "Test")
    fill_text_input(context, "last_name", "Person")
    fill_text_input(context, "phone_number", phone)
    fill_text_input(context, "email", email)

    submit_form(context)
    record_outcome(context)


@when('I try to create a "{person_type}" with email "{email}"')
def step_create_person_with_email(context, person_type, email):
    # Everything but the email is valid, so a refusal can only be about the email.
    _create_person(context, person_type, email=email, phone=VALID_PHONE)


@when('I try to create a "{person_type}" with phone number "{phone_number}"')
def step_create_person_with_phone(context, person_type, phone_number):
    _create_person(
        context,
        person_type,
        email=f"person{context._id_counter}@example.com",
        phone=phone_number,
    )


@then("I should see an error indicating the email is invalid")
def step_email_error(context):
    assert context.operation_error, "Expected an error message but the dialog showed none"
    assert "email" in context.operation_error.lower(), (
        f"Expected the error to name the email, got {context.operation_error!r}"
    )


@then("I should see an error indicating the phone number is invalid")
def step_phone_error(context):
    assert context.operation_error, "Expected an error message but the dialog showed none"
    assert "phone" in context.operation_error.lower(), (
        f"Expected the error to name the phone number, got {context.operation_error!r}"
    )
