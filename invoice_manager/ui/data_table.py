"""
Data Table Component for Invoice Management System
Provides a scrollable, sortable table view for invoice data.
"""

import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from typing import List, Dict, Any, Callable, Optional


class DataTable(ctk.CTkFrame):
    """
    A scrollable table component for displaying invoice data.
    Uses tkinter Treeview for efficient rendering of large datasets.
    """

    # Column definitions with display names and widths
    COLUMNS = [
        ("id", "ID", 50),
        ("tajan_tracking_number", "Tajan Tracking #", 150),
        ("amazon_test_request", "Amazon Test Req", 120),
        ("amazon_tracker_number", "Amazon Tracker", 120),
        ("asin", "ASIN", 100),
        ("development_center", "Dev Center", 80),
        ("category", "Category", 100),
        ("product_brand", "Brand", 100),
        ("product_description", "Description", 150),
        ("testing_sla", "SLA", 60),
        ("test_service_type", "Test Type", 120),
        ("quotation_order_number", "Quotation #", 100),
        ("request_date", "Request Date", 100),
        ("test_start_date", "Test Start", 100),
        ("report_delivered_date", "Report Date", 100),
        ("report_number", "Report #", 100),
        ("test_location", "Location", 100),
        ("product_line", "Product Line", 100),
        ("amazon_quality_manager", "Quality Mgr", 100),
        ("amazon_sourcing_manager", "Sourcing Mgr", 100),
        ("invoice_number", "Invoice #", 100),
        ("lab_contact", "Lab Contact", 100),
        ("comment", "Comment", 150),
        ("amount_usd", "Amount (USD)", 100),
        ("lab_name", "Lab", 60),
        ("invoice_date", "Invoice Date", 100),
    ]

    # Columns for abnormal items view (includes validation error)
    ABNORMAL_COLUMNS = COLUMNS + [("validation_error", "Validation Error", 200)]

    def __init__(self, parent, is_abnormal: bool = False,
                 on_select: Callable = None,
                 on_double_click: Callable = None):
        """
        Initialize the data table.

        Args:
            parent: Parent widget
            is_abnormal: If True, show validation error column
            on_select: Callback when row is selected
            on_double_click: Callback when row is double-clicked
        """
        super().__init__(parent)
        self.is_abnormal = is_abnormal
        self.on_select = on_select
        self.on_double_click = on_double_click
        self.data = []

        self._setup_table()

    def _setup_table(self):
        """Set up the treeview table."""
        # Configure style for better visibility
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=25)
        style.configure("Treeview.Heading",
                        background="#1f538d",
                        foreground="white",
                        font=('Helvetica', 10, 'bold'))
        style.map("Treeview",
                  background=[('selected', '#1f538d')],
                  foreground=[('selected', 'white')])

        # Create treeview with scrollbars
        columns = self.ABNORMAL_COLUMNS if self.is_abnormal else self.COLUMNS
        column_ids = [col[0] for col in columns]

        # Frame for treeview and scrollbars
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True)

        # Horizontal scrollbar
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        h_scroll.pack(side="bottom", fill="x")

        # Vertical scrollbar
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        v_scroll.pack(side="right", fill="y")

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=column_ids,
            show="headings",
            selectmode="extended",
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set
        )
        self.tree.pack(fill="both", expand=True)

        # Configure scrollbars
        h_scroll.config(command=self.tree.xview)
        v_scroll.config(command=self.tree.yview)

        # Configure columns
        for col_id, col_name, col_width in columns:
            self.tree.heading(col_id, text=col_name,
                              command=lambda c=col_id: self._sort_column(c))
            self.tree.column(col_id, width=col_width, minwidth=50)

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Sort state
        self._sort_column_id = None
        self._sort_reverse = False

    def load_data(self, data: List[Dict[str, Any]]):
        """
        Load data into the table.

        Args:
            data: List of invoice dictionaries
        """
        self.data = data
        self._refresh_display()

    def _refresh_display(self):
        """Refresh the table display with current data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add data rows
        columns = self.ABNORMAL_COLUMNS if self.is_abnormal else self.COLUMNS
        column_ids = [col[0] for col in columns]

        for record in self.data:
            values = [record.get(col_id, "") for col_id in column_ids]
            # Format amount for display
            amount_idx = column_ids.index("amount_usd")
            if values[amount_idx]:
                try:
                    values[amount_idx] = f"${float(values[amount_idx]):,.2f}"
                except (ValueError, TypeError):
                    pass
            self.tree.insert("", "end", values=values, iid=str(record.get('id', '')))

    def _sort_column(self, column_id: str):
        """Sort the table by a column."""
        if self._sort_column_id == column_id:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column_id = column_id
            self._sort_reverse = False

        # Sort the data
        def sort_key(record):
            value = record.get(column_id, "")
            if column_id == "amount_usd":
                try:
                    return float(value) if value else 0
                except (ValueError, TypeError):
                    return 0
            elif column_id == "id":
                try:
                    return int(value) if value else 0
                except (ValueError, TypeError):
                    return 0
            return str(value).lower()

        self.data.sort(key=sort_key, reverse=self._sort_reverse)
        self._refresh_display()

    def _on_select(self, event):
        """Handle row selection."""
        if self.on_select:
            selected_ids = self.get_selected_ids()
            self.on_select(selected_ids)

    def _on_double_click(self, event):
        """Handle double-click on row."""
        if self.on_double_click:
            selected_ids = self.get_selected_ids()
            if selected_ids:
                self.on_double_click(selected_ids[0])

    def get_selected_ids(self) -> List[int]:
        """Get the IDs of selected rows."""
        selected = self.tree.selection()
        ids = []
        for item in selected:
            try:
                ids.append(int(item))
            except ValueError:
                pass
        return ids

    def get_selected_records(self) -> List[Dict[str, Any]]:
        """Get the full records of selected rows."""
        selected_ids = self.get_selected_ids()
        return [r for r in self.data if r.get('id') in selected_ids]

    def clear_selection(self):
        """Clear all selections."""
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def select_all(self):
        """Select all rows."""
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def get_record_count(self) -> int:
        """Get the total number of records."""
        return len(self.data)


class FilterBar(ctk.CTkFrame):
    """Filter bar for the data table."""

    def __init__(self, parent, lab_names: List[str], on_filter: Callable):
        """
        Initialize filter bar.

        Args:
            parent: Parent widget
            lab_names: List of lab names for dropdown
            on_filter: Callback when filter is applied
        """
        super().__init__(parent)
        self.on_filter = on_filter

        # Search entry
        ctk.CTkLabel(self, text="Search:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(self, width=200, placeholder_text="Search...")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self._apply_filter())

        # Lab filter
        ctk.CTkLabel(self, text="Lab:").pack(side="left", padx=(20, 5))
        self.lab_combo = ctk.CTkComboBox(
            self,
            values=["All"] + lab_names,
            width=100,
            command=lambda v: self._apply_filter()
        )
        self.lab_combo.set("All")
        self.lab_combo.pack(side="left", padx=5)

        # Date range
        ctk.CTkLabel(self, text="From:").pack(side="left", padx=(20, 5))
        self.date_from = ctk.CTkEntry(self, width=100, placeholder_text="YYYY-MM-DD")
        self.date_from.pack(side="left", padx=5)

        ctk.CTkLabel(self, text="To:").pack(side="left", padx=5)
        self.date_to = ctk.CTkEntry(self, width=100, placeholder_text="YYYY-MM-DD")
        self.date_to.pack(side="left", padx=5)

        # Filter button
        ctk.CTkButton(
            self,
            text="Filter",
            command=self._apply_filter,
            width=80
        ).pack(side="left", padx=10)

        # Clear button
        ctk.CTkButton(
            self,
            text="Clear",
            command=self._clear_filter,
            width=80,
            fg_color="gray"
        ).pack(side="left", padx=5)

    def _apply_filter(self):
        """Apply the current filter settings."""
        filters = {}

        search_text = self.search_entry.get().strip()
        if search_text:
            filters['search_text'] = search_text

        lab = self.lab_combo.get()
        if lab and lab != "All":
            filters['lab_name'] = lab

        date_from = self.date_from.get().strip()
        if date_from:
            filters['date_from'] = date_from

        date_to = self.date_to.get().strip()
        if date_to:
            filters['date_to'] = date_to

        self.on_filter(filters)

    def _clear_filter(self):
        """Clear all filters."""
        self.search_entry.delete(0, 'end')
        self.lab_combo.set("All")
        self.date_from.delete(0, 'end')
        self.date_to.delete(0, 'end')
        self.on_filter({})

    def update_lab_names(self, lab_names: List[str]):
        """Update the lab names in the dropdown."""
        self.lab_combo.configure(values=["All"] + lab_names)
