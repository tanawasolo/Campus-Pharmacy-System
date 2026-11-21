"""Screen 1: Register Medicine."""
import tkinter as tk
from tkinter import ttk, messagebox

from pharmacy.domain import make_medicine
from pharmacy.ui.ui_helpers import safe_call, read_number


class RegisterMedicineFrame(ttk.Frame):
    def __init__(self, parent, service):
        super().__init__(parent, padding=15)
        self.service = service  # all logic goes through the service

        # --- input fields ---
        ttk.Label(self, text="Medicine code").grid(row=0, column=0, sticky="w", pady=5)
        self.code_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.code_var, width=30).grid(row=0, column=1)

        ttk.Label(self, text="Medicine name").grid(row=1, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var, width=30).grid(row=1, column=1)

        ttk.Label(self, text="Unit price").grid(row=2, column=0, sticky="w", pady=5)
        self.price_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.price_var, width=30).grid(row=2, column=1)

        ttk.Label(self, text="Reorder level").grid(row=3, column=0, sticky="w", pady=5)
        self.reorder_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.reorder_var, width=30).grid(row=3, column=1)

        # tick box: controlled medicine or ordinary medicine
        self.controlled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Controlled medicine",
                        variable=self.controlled_var).grid(row=4, column=1, sticky="w", pady=5)

        ttk.Button(self, text="Register", command=self.on_register).grid(row=5, column=1, sticky="w", pady=10)

    def register(self, code, name, price, reorder, controlled):
        """Build the Medicine (the domain class checks every rule), then save it."""
        medicine = make_medicine(code, name, price, reorder, controlled)
        return self.service.register_medicine(medicine)

    def on_register(self):
        """Called when the Register button is clicked."""
        price = read_number(self.price_var.get(), "Unit price", whole=False)
        reorder = read_number(self.reorder_var.get(), "Reorder level")
        if price is None or reorder is None:
            return  # an error box was already shown

        ok, _ = safe_call(self.register,
                          self.code_var.get().strip(), self.name_var.get().strip(),
                          price, reorder, self.controlled_var.get())
        if ok:
            messagebox.showinfo("Done", "Medicine registered.")
            # clear the form for the next medicine
            self.code_var.set("")
            self.name_var.set("")
            self.price_var.set("")
            self.reorder_var.set("")
            self.controlled_var.set(False)

    def refresh(self):
        """Nothing to reload on this screen."""
        pass
