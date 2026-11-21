"""Screen 4: Dispense (list of pending prescriptions with Dispense / Cancel)."""
from tkinter import ttk, messagebox

from pharmacy.ui.ui_helpers import safe_call, get


class DispenseFrame(ttk.Frame):
    def __init__(self, parent, service):
        super().__init__(parent, padding=15)
        self.service = service

        self.table = ttk.Treeview(self, columns=("id", "patient", "prescriber", "status"),
                                  show="headings", height=10, selectmode="browse")
        self.table.heading("id", text="Prescription ID")
        self.table.heading("patient", text="Patient")
        self.table.heading("prescriber", text="Prescriber")
        self.table.heading("status", text="Status")
        self.table.pack(fill="both", expand=True)

        buttons = ttk.Frame(self)
        buttons.pack(pady=10)
        ttk.Button(buttons, text="Dispense", command=self.on_dispense).pack(side="left", padx=5)
        ttk.Button(buttons, text="Cancel prescription", command=self.on_cancel).pack(side="left", padx=5)
        ttk.Button(buttons, text="Refresh", command=self.refresh).pack(side="left", padx=5)

        self.refresh()

    def refresh(self):
        """Reload the list of pending prescriptions."""
        for row in self.table.get_children():
            self.table.delete(row)
        ok, prescriptions = safe_call(self.service.list_pending)
        if ok:
            for p in prescriptions:
                self.table.insert("", "end", values=(
                    get(p, "id"), get(p, "patient_id"),
                    get(p, "prescriber_code") or "(none)", get(p, "status", "pending")))

    def selected_id(self):
        """Return the id of the selected row, or None (and warn the user)."""
        chosen = self.table.selection()
        if not chosen:
            messagebox.showwarning("Nothing selected", "Please select a prescription first.")
            return None
        return self.table.item(chosen[0])["values"][0]

    def on_dispense(self):
        prescription_id = self.selected_id()
        if prescription_id is None:
            return
        ok, _ = safe_call(self.service.dispense, prescription_id)
        if ok:
            messagebox.showinfo("Done", "Prescription dispensed.")
        self.refresh()  # refresh either way so the list is up to date

    def on_cancel(self):
        prescription_id = self.selected_id()
        if prescription_id is None:
            return
        ok, _ = safe_call(self.service.cancel, prescription_id)
        if ok:
            messagebox.showinfo("Done", "Prescription cancelled.")
        self.refresh()
