"""Screen 3: Create Prescription.

Rules shown in the interface:
  * a patient id, a branch and a prescriber code are entered
  * lines are added one by one (medicine + quantity)
  * the Save button stays disabled until at least ONE line exists
"""
import tkinter as tk
from tkinter import ttk, messagebox

from pharmacy.domain import Prescription, PrescriptionLine
from pharmacy.ui.ui_helpers import safe_call, read_number, make_choices


class CreatePrescriptionFrame(ttk.Frame):
    def __init__(self, parent, service):
        super().__init__(parent, padding=15)
        self.service = service
        self.medicine_lookup = {}  # "MED-001 - Paracetamol" -> "MED-001"
        self.branch_lookup = {}    # "1 - Main Campus" -> 1
        self.branches_by_id = {}   # 1 -> Branch object
        self.lines = []  # list of (medicine_code, medicine_label, quantity)

        ttk.Label(self, text="Patient ID").grid(row=0, column=0, sticky="w", pady=5)
        self.patient_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.patient_var, width=30).grid(row=0, column=1, columnspan=2, sticky="w")

        ttk.Label(self, text="Branch").grid(row=1, column=0, sticky="w", pady=5)
        self.branch_box = ttk.Combobox(self, state="readonly", width=28)
        self.branch_box.grid(row=1, column=1, columnspan=2, sticky="w")

        ttk.Label(self, text="Prescriber code").grid(row=2, column=0, sticky="w", pady=5)
        self.prescriber_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.prescriber_var, width=30).grid(row=2, column=1, columnspan=2, sticky="w")

        ttk.Label(self, text="Medicine").grid(row=3, column=0, sticky="w", pady=5)
        self.medicine_box = ttk.Combobox(self, state="readonly", width=28)
        self.medicine_box.grid(row=3, column=1, columnspan=2, sticky="w")

        ttk.Label(self, text="Quantity").grid(row=4, column=0, sticky="w", pady=5)
        self.qty_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.qty_var, width=10).grid(row=4, column=1, sticky="w")
        ttk.Button(self, text="Add line", command=self.on_add_line).grid(row=4, column=2, padx=5)

        # table showing the lines added so far
        self.table = ttk.Treeview(self, columns=("medicine", "qty"), show="headings", height=6)
        self.table.heading("medicine", text="Medicine")
        self.table.heading("qty", text="Quantity")
        self.table.grid(row=5, column=0, columnspan=3, pady=10, sticky="ew")

        ttk.Button(self, text="Clear lines", command=self.clear_lines).grid(row=6, column=0, sticky="w")
        # Save starts DISABLED (rule: at least one line)
        self.save_button = ttk.Button(self, text="Save prescription",
                                      command=self.on_save, state="disabled")
        self.save_button.grid(row=6, column=1, columnspan=2, sticky="e")

        self.refresh()

    def refresh(self):
        """Reload the branch and medicine dropdowns."""
        ok, branches = safe_call(self.service.list_branches)
        ok2, medicines = safe_call(self.service.list_medicines)
        if ok and ok2:
            labels, self.branch_lookup = make_choices(branches)
            self.branches_by_id = {b.id: b for b in branches}
            self.branch_box["values"] = labels
            labels, self.medicine_lookup = make_choices(medicines)
            self.medicine_box["values"] = labels

    def update_save_button(self):
        """Enable Save only when there is at least one line."""
        self.save_button.config(state="normal" if self.lines else "disabled")

    def on_add_line(self):
        label = self.medicine_box.get()
        medicine_code = self.medicine_lookup.get(label)
        if medicine_code is None:
            messagebox.showerror("Missing choice", "Please choose a medicine.")
            return
        qty = read_number(self.qty_var.get(), "Quantity")
        if qty is None:
            return
        # building the line checks the rules now (for example quantity above 0)
        ok, _ = safe_call(PrescriptionLine, medicine_code, qty)
        if not ok:
            return

        self.lines.append((medicine_code, label, qty))
        self.table.insert("", "end", values=(label, qty))
        self.qty_var.set("")
        self.update_save_button()

    def clear_lines(self):
        self.lines = []
        for row in self.table.get_children():
            self.table.delete(row)
        self.update_save_button()

    def save(self, patient_id, branch, prescriber_code):
        """Build the Prescription from the form, then save it through the service."""
        prescription = Prescription(patient_id, branch, prescriber_code)
        for medicine_code, _label, qty in self.lines:
            prescription.add_line(medicine_code, qty)
        return self.service.create_prescription(prescription)

    def on_save(self):
        branch = self.branches_by_id.get(self.branch_lookup.get(self.branch_box.get()))
        if branch is None:
            messagebox.showerror("Missing choice", "Please choose a branch.")
            return
        ok, _ = safe_call(self.save, self.patient_var.get().strip(),
                          branch, self.prescriber_var.get().strip())
        if ok:
            messagebox.showinfo("Done", "Prescription saved as pending.")
            self.patient_var.set("")
            self.prescriber_var.set("")
            self.clear_lines()
