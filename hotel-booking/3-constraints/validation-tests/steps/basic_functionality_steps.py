"""Load the basic_functionality step definitions.

behave imports the modules directly under ``steps/`` and does not descend into
subdirectories, so the definitions grouped in ``steps/basic_functionality/``
would never register. Importing them here is what makes behave see them; the
grouping on disk is kept.
"""

from steps.basic_functionality import (  # noqa: F401
    booking_steps,
    common,
    guest_and_employee_steps,
    invoice_steps,
    room_steps,
)
