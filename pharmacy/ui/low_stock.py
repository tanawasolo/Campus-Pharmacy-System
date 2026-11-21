"""Screen 5: Low Stock (table + branch filter + Refresh)."""
from tkinter import ttk

from pharmacy.ui.ui_helpers import safe_call, get, make_choices


class LowStockFrame(ttk.Frame):
    ALL = "All branches"

    def __init__(self, parent, service):
        super().__init__(parent, padding=15)
        self.service = service
        self.branch_lookup = {}

        # --- top bar: branch filter and refresh button ---
        top = ttk.Frame(self)
        top.pack(fill="x", pady=5)
        ttk.Label(top, text="Branch").pack(side="left")
        self.branch_box = ttk.Combobox(top, state="readonly", width=25)
        self.branch_box.pack(side="left", padx=5)
        ttk.Button(top, text="Refresh", command=self.refresh).pack(side="left")

        # --- table of low stock items ---
        columns = ("branch", "medicine", "quantity", "reorder")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col, title in zip(columns, ("Branch", "Medicine", "Quantity", "Reorder level")):
            self.table.heading(col, text=title)
        self.table.pack(fill="both", expand=True)

        self.load_branches()
        self.refresh()

    def load_branches(self):
        ok, branches = safe_call(self.service.list_branches)
        if ok:
            labels, self.branch_lookup = make_choices(branches)
            self.branch_box["values"] = [self.ALL] + labels
        self.branch_box.set(self.ALL)

    def refresh(self):
        """Reload the table using the chosen branch filter."""
        for row in self.table.get_children():
            self.table.delete(row)

        # None means "no filter" = every branch
        branch_id = self.branch_lookup.get(self.branch_box.get())
        ok, items = safe_call(self.service.low_stock, branch_id)
        if ok:
            for item in items:
                medicine = f"{get(item, 'medicine_code')} - {get(item, 'medicine_name')}"
                self.table.insert("", "end", values=(
                    get(item, "branch_name"), medicine,
                    get(item, "quantity"), get(item, "reorder_level")))
