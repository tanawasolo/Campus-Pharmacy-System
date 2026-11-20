"""Screen 2: Receive Stock (add stock of a medicine to a branch)."""
import tkinter as tk
from tkinter import ttk, messagebox

from pharmacy.ui.ui_helpers import safe_call, read_number, make_choices


class ReceiveStockFrame(ttk.Frame):
    def __init__(self, parent, service):
        super().__init__(parent, padding=15)
        self.service = service
        self.branch_lookup = {}    # "1 - Main" -> 1
        self.medicine_lookup = {}  # "3 - Panadol" -> 3

        ttk.Label(self, text="Branch").grid(row=0, column=0, sticky="w", pady=5)
        self.branch_box = ttk.Combobox(self, state="readonly", width=28)
        self.branch_box.grid(row=0, column=1)

        ttk.Label(self, text="Medicine").grid(row=1, column=0, sticky="w", pady=5)
        self.medicine_box = ttk.Combobox(self, state="readonly", width=28)
        self.medicine_box.grid(row=1, column=1)

        ttk.Label(self, text="Quantity received").grid(row=2, column=0, sticky="w", pady=5)
        self.qty_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.qty_var, width=30).grid(row=2, column=1)

        ttk.Button(self, text="Receive stock", command=self.on_receive).grid(row=3, column=1, sticky="w", pady=10)

        self.refresh()

    def refresh(self):
        """Reload the dropdown lists (new medicines may have been added)."""
        ok, branches = safe_call(self.service.repo.list_branches)
        ok2, medicines = safe_call(self.service.repo.list_medicines)
        if ok and ok2:
            labels, self.branch_lookup = make_choices(branches)
            self.branch_box["values"] = labels
            labels, self.medicine_lookup = make_choices(medicines)
            self.medicine_box["values"] = labels

    def on_receive(self):
        branch_id = self.branch_lookup.get(self.branch_box.get())
        medicine_id = self.medicine_lookup.get(self.medicine_box.get())
        if branch_id is None or medicine_id is None:
            messagebox.showerror("Missing choice", "Please choose a branch and a medicine.")
            return
        qty = read_number(self.qty_var.get(), "Quantity")
        if qty is None:
            return

        ok, _ = safe_call(self.service.receive_stock, branch_id, medicine_id, qty)
        if ok:
            messagebox.showinfo("Done", "Stock received.")
            self.qty_var.set("")
