"""Main window: one tab per screen.

Merge note: if the scaffold's app.py already creates the service and has a
main() function, keep that part and only copy the tab-building code below.
"""
import tkinter as tk
from tkinter import ttk

from pharmacy.ui.register_medicine import RegisterMedicineFrame
from pharmacy.ui.receive_stock import ReceiveStockFrame
from pharmacy.ui.create_prescription import CreatePrescriptionFrame
from pharmacy.ui.dispense import DispenseFrame
from pharmacy.ui.low_stock import LowStockFrame


class PharmacyApp(tk.Tk):
    def __init__(self, service):
        super().__init__()
        self.title("Pharmacy Management System")
        self.geometry("720x500")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # each screen is a Frame that receives the service
        tabs = [
            ("Register Medicine", RegisterMedicineFrame),
            ("Receive Stock", ReceiveStockFrame),
            ("Create Prescription", CreatePrescriptionFrame),
            ("Dispense", DispenseFrame),
            ("Low Stock", LowStockFrame),
        ]
        self.frames = []
        for title, frame_class in tabs:
            frame = frame_class(self.notebook, service)
            self.notebook.add(frame, text=title)
            self.frames.append(frame)

        # reload the screen's data every time its tab is opened
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, _event):
        index = self.notebook.index(self.notebook.select())
        self.frames[index].refresh()


def run(service):
    """Start the application."""
    PharmacyApp(service).mainloop()

if __name__ == "__main__":
    from pharmacy.data.repository import Repository
    from pharmacy.services.dispensing_service import DispensingService

    repo = Repository("pharmacy.db")
    repo.load_seed()
    run(DispensingService(repo))