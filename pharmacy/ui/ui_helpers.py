"""Small helpers shared by every screen (keeps the screens simple)."""
import traceback
from tkinter import messagebox

from pharmacy.domain import PharmacyError


def safe_call(func, *args, **kwargs):
    """Run a service call and catch any PharmacyError.

    Returns (True, result) when it worked.
    Returns (False, None) after showing a readable error box when it failed.
    This is the ONLY place that turns exceptions into messages, so every
    screen behaves the same way.
    """
    try:
        return True, func(*args, **kwargs)
    except PharmacyError as err:
        messagebox.showerror("Not allowed", str(err))
        return False, None
    except Exception as err:
        traceback.print_exc()
        messagebox.showerror("Unexpected error", f"Something went wrong: {err}")
        return False, None


def read_number(text, label, whole=True):
    """Convert text typed by the user into a number.

    Shows an error box and returns None if the text is not a valid number.
    """
    try:
        return int(text) if whole else float(text)
    except ValueError:
        kind = "whole number" if whole else "number"
        messagebox.showerror("Invalid input", f"{label} must be a {kind}.")
        return None


def get(obj, name, default=""):
    """Read a field from an object OR a dictionary (works with both)."""
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def make_choices(items):
    """Turn a list of medicines/branches into dropdown text.

    Returns (labels, lookup) where lookup maps "1 - Main Campus" -> 1
    or "MED-001 - Paracetamol 500mg" -> "MED-001".
    """
    lookup = {}
    for item in items:
        key = get(item, "id", None)
        if key is None:
            key = get(item, "code")
        lookup[f"{key} - {get(item, 'name')}"] = key
    return list(lookup.keys()), lookup