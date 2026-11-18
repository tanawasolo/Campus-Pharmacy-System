"""Role D: main window. Run with: python -m pharmacy.ui.app

Shell only. Each tab is a placeholder; replace it with a ttk.Frame subclass
that takes the service in its constructor.
"""
import tkinter as tk
from tkinter import ttk

from pharmacy.data.repository import Repository
from pharmacy.domain.prescriber_registry import PrescriberRegistry
from pharmacy.services.dispensing_service import DispensingService

TABS = ["Register Medicine", "Receive Stock", "Create Prescription", "Dispense", "Low Stock"]


def build_service():
    repo = Repository()
    # TODO: load allowed codes through the repository (list_prescriber_codes)
    registry = PrescriberRegistry(repo.list_prescriber_codes())
    return DispensingService(repo, registry)


def main():
    root = tk.Tk()
    root.title("Campus Pharmacy System")
    root.geometry("900x600")

    try:
        service = build_service()
    except NotImplementedError:
        service = None

    if service is None:
        ttk.Label(root, text="Backend not implemented yet (Roles A-C).").pack(pady=20)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    for name in TABS:
        # TODO: replace placeholder with the real screen, passing `service`
        frame = ttk.Frame(notebook)
        ttk.Label(frame, text=f"{name}: TODO").pack(pady=20)
        notebook.add(frame, text=name)

    root.mainloop()


if __name__ == "__main__":
    main()
