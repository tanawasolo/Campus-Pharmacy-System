"""Screen 3: Create Prescription.

Rules shown in the interface:
  * a prescriber code is typed in
  * lines are added one by one (medicine + quantity)
  * the Save button stays disabled until at least ONE line exists
"""
import tkinter as tk
from tkinter import ttk, messagebox

from pharmacy.ui.ui_helpers import safe_call, read_number, make_choices


class CreatePrescriptionFrame(ttk.Frame):
    def __init__(self, parent, service):
        super().__init__(parent, padding=15)
        self.service = service
        self.medicine_lookup = {}
        self.lines = []  # list of (medicine_id, medicine_label, quantity)

        ttk.Label(self, text="Prescriber code").grid(row=0, column=0, sticky="w", pady=5)
        self.prescriber_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.prescriber_var, width=30).grid(row=0, column=1, columnspan=2, sticky="w")

        ttk.Label(self, text="Medicine").grid(row=1, column=0, sticky="w", pady=5)
        self.medicine_box = ttk.Combobox(self, state="readonly", width=28)
        self.medicine_box.grid(row=1, column=1, columnspan=2, sticky="w")

        ttk.Label(self, text="Quantity").grid(row=2, column=0, sticky="w", pady=5)
        self.qty_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.qty_var, width=10).grid(row=2, column=1, sticky="w")
        ttk.Button(self, text="Add line", command=self.on_add_line).grid(row=2, column=2, padx=5)

        # table showing the lines added so far
        self.table = ttk.Treeview(self, columns=("medicine", "qty"), show="headings", height=6)
        self.table.heading("medicine", text="Medicine")
        self.table.heading("qty", text="Quantity")
        self.table.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

        ttk.Button(self, text="Clear lines", command=self.clear_lines).grid(row=4, column=0, sticky="w")
        # Save starts DISABLED (rule: at least one line)
        self.save_button = ttk.Button(self, text="Save prescription",
                                      command=self.on_save, state="disabled")
        self.save_button.grid(row=4, column=1, columnspan=2, sticky="e")

        self.refresh()

    def refresh(self):
        """Reload the medicine dropdown."""
        ok, medicines = safe_call(self.service.repo.list_medicines)
        if ok:
            labels, self.medicine_lookup = make_choices(medicines)
            self.medicine_box["values"] = labels

    def update_save_button(self):
        """Enable Save only when there is at least one line."""
        self.save_button.config(state="normal" if self.lines else "disabled")

    def on_add_line(self):
        label = self.medicine_box.get()
        medicine_id = self.medicine_lookup.get(label)
        if medicine_id is None:
            messagebox.showerror("Missing choice", "Please choose a medicine.")
            return
        qty = read_number(self.qty_var.get(), "Quantity")
        if qty is None:
            return

        self.lines.append((medicine_id, label, qty))
        self.table.insert("", "end", values=(label, qty))
        self.qty_var.set("")
        self.update_save_button()

    def clear_lines(self):
        self.lines = []
        for row in self.table.get_children():
            self.table.delete(row)
        self.update_save_button()

    def on_save(self):
        # the service expects (medicine_id, quantity) pairs
        service_lines = [(med_id, qty) for med_id, _label, qty in self.lines]
        ok, _ = safe_call(self.service.create_prescription,
                          self.prescriber_var.get().strip(), service_lines)
        if ok:
            messagebox.showinfo("Done", "Prescription saved as pending.")
            self.prescriber_var.set("")
            self.clear_lines()
