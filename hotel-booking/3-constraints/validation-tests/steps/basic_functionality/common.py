"""Common background and hook steps."""
from behave import given, then
from steps.basic_functionality.helpers import navigate_to

@given("the hotel booking application is running and the database is empty")
def step_app_running_and_empty(context):
    navigate_to(context, "/guest")
    context.page.wait_for_load_state("networkidle")

@then("the operation should succeed")
def step_operation_succeeded(context):
    assert context.operation_succeeded, f"Expected operation to succeed but got error: {context.operation_error}"

@then("the operation should fail")
def step_operation_failed(context):
    assert not context.operation_succeeded, "Expected operation to fail but it succeeded"
