"""Shared UI and API helpers for Behave step definitions."""
import re

import requests

def next_id(context):
    context._id_counter += 1
    return context._id_counter

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def api_post(context, endpoint, data):
    resp = requests.post(f"{context.api_base}{endpoint}", json=data, timeout=10)
    resp.raise_for_status()
    return resp.json()

def api_put(context, endpoint, data):
    resp = requests.put(f"{context.api_base}{endpoint}", json=data, timeout=10)
    resp.raise_for_status()
    return resp.json()

def api_get(context, endpoint):
    resp = requests.get(f"{context.api_base}{endpoint}", timeout=10)
    resp.raise_for_status()
    return resp.json()

def api_delete(context, endpoint):
    requests.delete(f"{context.api_base}{endpoint}", timeout=5)

# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def navigate_to(context, path):
    context.page.goto(f"{context.ui_base}{path}")
    context.page.wait_for_load_state("networkidle")

# ---------------------------------------------------------------------------
# Modal helpers
# ---------------------------------------------------------------------------

def open_add_modal(context, entity_label):
    context.page.click(f'button[title="Add {entity_label}"]')
    context.page.wait_for_selector(".bsr-modal", state="visible")

def fill_text_input(context, field, value):
    input_selector = f"#modal-input-{field}"
    context.page.fill(input_selector, str(value))
    context.page.wait_for_timeout(100)
    context.page.evaluate(f"""
        const el = document.querySelector('{input_selector}');
        if (el) {{
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
        }}
    """)

def fill_select(context, field, value):
    context.page.select_option(f"#modal-input-{field}", value=str(value))

def fill_select_by_label(context, field, label):
    context.page.select_option(f"#modal-input-{field}", label=label)

def check_list_item(context, label_text):
    modal = context.page.locator(".bsr-modal")
    modal.get_by_text(label_text, exact=True).click()

def select_lookup_by_label(context, field, label):
    """Select from a dropdown lookup field by visible label or substring match."""
    select_elem = context.page.locator(f"#modal-input-{field}").first
    if not select_elem.is_visible():
        return

    # Get all options and find one that matches the label
    options = select_elem.locator("option")
    option_count = options.count()

    for i in range(option_count):
        option_text = options.nth(i).inner_text()
        option_value = options.nth(i).get_attribute("value")
        # Match by exact label or partial match (for email addresses, room numbers, etc)
        if label in option_text or option_text in label:
            select_elem.select_option(value=option_value)
            return

    # If no match found, try direct select_option
    try:
        select_elem.select_option(label=label)
    except:
        try:
            select_elem.select_option(value=label)
        except:
            pass

def check_list_items(context, items):
    """Check multiple items in a checkbox list (multi-select) by their labels."""
    modal = context.page.locator(".bsr-modal")
    for item_label in items:
        # Find checkbox for this item and click it
        item_row = modal.locator("div").filter(has_text=item_label).first
        checkbox = item_row.locator("input[type='checkbox']").first
        if checkbox.is_visible():
            if not checkbox.is_checked():
                checkbox.click()
            else:
                checkbox.check()

def submit_form(context):
    context.page.locator(".bsr-modal button[type='submit']").click()
    context.page.wait_for_timeout(500)

def modal_is_visible(context):
    return context.page.locator(".bsr-modal").is_visible()

def get_modal_error(context):
    """The reason the dialog is refusing to close.

    React writes the inline colour as rgb(), so selecting on the generator's
    #fee2e2 matched nothing and every refused operation read back as having no
    message at all.
    """
    err = context.page.locator(".bsr-modal [style*='rgb(254, 226, 226)']").first
    try:
        err.wait_for(state="visible", timeout=5000)
    except Exception:
        return ""
    return err.inner_text().strip()

def close_modal_if_open(context):
    if modal_is_visible(context):
        context.page.keyboard.press("Escape")
        context.page.wait_for_selector(".bsr-modal", state="hidden")

# ---------------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------------

def wait_for_table(context, table_id):
    context.page.wait_for_function(
        f"""() => {{
            const el = document.getElementById('{table_id}');
            return el && !el.textContent.includes('Loading data');
        }}"""
    )

def count_table_rows(context, table_id):
    rows = context.page.locator(f"#{table_id} tbody tr")
    return rows.count()

def find_row_by_text(context, table_id, text):
    return context.page.locator(f"#{table_id} tbody tr").filter(has_text=text).first

def get_cell_in_row(row_locator, col_index):
    return row_locator.locator("td").nth(col_index).inner_text().strip()

def get_cell(context, table_id, row_locator, field):
    """A row's cell for a field, located by the column header.

    The generator emits the columns in the order the model yields them, not the
    order the attributes were declared, so a fixed index reads a neighbouring
    column: the invoice amount was being read out of the issued-date column.
    """
    headers = context.page.locator(f"#{table_id} thead th").all_inner_texts()
    wanted = field.replace("_", " ").strip().lower()
    for index, header in enumerate(headers):
        label = re.sub(r"[^a-z ]", "", header.strip().lower()).strip()
        if label == wanted:
            return row_locator.locator("td").nth(index).inner_text().strip()
    raise AssertionError(f"No column for {field!r}; headers were {headers}")

def click_edit_in_row(context, table_id, row_text):
    row = find_row_by_text(context, table_id, row_text)
    row.locator('button[title="Edit"]').click()
    context.page.wait_for_selector(".bsr-modal", state="visible")

def click_remove_in_row(context, table_id, row_text):
    row = find_row_by_text(context, table_id, row_text)
    row.locator('button[title="Remove"]').click()

def get_row_action_error(context, table_id):
    alert = context.page.locator(f"#{table_id} [role='alert']")
    if alert.is_visible():
        return alert.inner_text().strip()
    return ""
