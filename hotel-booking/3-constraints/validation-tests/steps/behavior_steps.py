"""Load the behavior step definitions.

behave imports the modules directly under ``steps/`` and does not descend into
subdirectories, so the definitions grouped in ``steps/behavior/`` would never
register. Importing them here is what makes behave see them.
"""

from steps.behavior import booking_steps  # noqa: F401
