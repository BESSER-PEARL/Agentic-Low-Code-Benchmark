import os
import sys
import requests
from playwright.sync_api import sync_playwright

# This directory holds the steps package, so it is what has to be importable
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

BASE_API = "http://localhost:8000"
BASE_UI = "http://localhost:3000"

_RESET_ORDER = ["/invoice/", "/booking/", "/guest/", "/employee/", "/room/", "/person/"]


def _delete_all(api_base, endpoint):
    try:
        resp = requests.get(f"{api_base}{endpoint}", timeout=10)
        if resp.status_code != 200:
            return
        data = resp.json()
        if not isinstance(data, list):
            return
        for item in data:
            pk = item.get("id") if "id" in item else item.get("number")
            if pk is not None:
                requests.delete(f"{api_base}{endpoint}{pk}/", timeout=5)
    except Exception:
        pass


def reset_database(context):
    for endpoint in _RESET_ORDER:
        _delete_all(context.api_base, endpoint)


def before_all(context):
    context.api_base = BASE_API
    context.ui_base = BASE_UI
    context._playwright = sync_playwright().start()
    context.browser = context._playwright.chromium.launch(headless=False)


def after_all(context):
    context.browser.close()
    context._playwright.stop()


def before_scenario(context, scenario):
    reset_database(context)
    context.page = context.browser.new_page()
    context.page.set_default_timeout(15000)
    context._id_counter = 0
    # Entity caches keyed by identifier
    context.guests = {}        # email -> response dict
    context.employees = {}     # email -> response dict
    context.rooms = {}         # number -> response dict
    context.bookings = []      # list of booking dicts
    context.current_booking = None
    context.no_invoice_booking = None
    context.current_invoice = None
    context.operation_succeeded = None
    context.operation_error = None


def after_scenario(context, scenario):
    reset_database(context)
    context.page.close()
