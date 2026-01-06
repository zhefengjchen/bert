"""
Dialog Windows for Invoice Management System
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime


class BaseDialog(ctk.CTkToplevel):
    """Base class for dialogs."""

    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center the dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")

        self.result = None


class InvoiceDateDialog(BaseDialog):
    """Dialog for entering invoice date when uploading."""

    def __init__(self, parent, filename: str, detected_lab: Optional[str]):
        super().__init__(parent, "Invoice Upload", 450, 200)

        # Info label
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            info_frame,
            text=f"File: {filename}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=2)

        lab_text = detected_lab if detected_lab else "Not detected (will prompt for selection)"
        lab_color = "green" if detected_lab else "orange"
        ctk.CTkLabel(
            info_frame,
            text=f"Lab: {lab_text}",
            font=ctk.CTkFont(size=12),
            text_color=lab_color
        ).pack(anchor="w", pady=2)

        # Date entry
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            date_frame,
            text="Invoice Date (YYYY-MM-DD):",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=2)

        self.date_entry = ctk.CTkEntry(date_frame, width=200)
        self.date_entry.pack(anchor="w", pady=5)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            fg_color="gray"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Upload",
            command=self.confirm,
            width=100
        ).pack(side="right", padx=5)

    def confirm(self):
        date_str = self.date_entry.get().strip()
        # Validate date format
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            self.result = date_str
            self.destroy()
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")

    def cancel(self):
        self.result = None
        self.destroy()


class AddInvoiceDialog(BaseDialog):
    """Dialog for manually adding a new invoice."""

    FIELDS = [
        ("tajan_tracking_number", "Tajan Tracking Number*"),
        ("amazon_test_request", "Amazon Test Request #"),
        ("amazon_tracker_number", "Amazon Tracker Number"),
        ("asin", "ASIN#"),
        ("development_center", "Development Center"),
        ("category", "Category"),
        ("product_brand", "Product Brand"),
        ("product_description", "Product Description"),
        ("testing_sla", "Testing SLA"),
        ("test_service_type", "Test/Service Type*"),
        ("quotation_order_number", "Quotation/Order Number"),
        ("request_date", "Request Date"),
        ("test_start_date", "Test Start Date"),
        ("report_delivered_date", "Report Delivered Date"),
        ("report_number", "Report Number"),
        ("test_location", "Test Location"),
        ("product_line", "Product Line"),
        ("amazon_quality_manager", "Amazon Quality Manager"),
        ("amazon_sourcing_manager", "Amazon Sourcing Manager"),
        ("invoice_number", "Invoice #"),
        ("lab_contact", "Lab Contact"),
        ("comment", "Comment"),
        ("amount_usd", "Amount (USD)"),
        ("lab_name", "Lab Name*"),
        ("invoice_date", "Invoice Date*"),
    ]

    def __init__(self, parent, lab_names: List[str], test_types: List[str],
                 existing_data: Dict[str, Any] = None):
        super().__init__(parent, "Add Invoice" if not existing_data else "Edit Invoice", 600, 700)

        self.lab_names = lab_names
        self.test_types = test_types
        self.entries = {}

        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self, width=560, height=580)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create entry fields
        for field_name, label in self.FIELDS:
            frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            frame.pack(fill="x", pady=3)

            ctk.CTkLabel(
                frame,
                text=label,
                width=180,
                anchor="w"
            ).pack(side="left", padx=5)

            # Special handling for dropdowns
            if field_name == "lab_name":
                entry = ctk.CTkComboBox(frame, values=lab_names, width=300)
            elif field_name == "test_service_type":
                entry = ctk.CTkComboBox(frame, values=test_types, width=300)
            elif field_name == "development_center":
                entry = ctk.CTkComboBox(
                    frame,
                    values=["SEA", "LUX/EU", "JP", ""],
                    width=300
                )
            else:
                entry = ctk.CTkEntry(frame, width=300)

            entry.pack(side="left", padx=5)
            self.entries[field_name] = entry

            # Pre-fill if editing
            if existing_data and field_name in existing_data:
                value = existing_data.get(field_name, "")
                if isinstance(entry, ctk.CTkComboBox):
                    entry.set(str(value) if value else "")
                else:
                    entry.insert(0, str(value) if value else "")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            width=100,
            fg_color="gray"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self.confirm,
            width=100
        ).pack(side="right", padx=5)

    def confirm(self):
        """Validate and save the invoice data."""
        data = {}
        for field_name, entry in self.entries.items():
            if isinstance(entry, ctk.CTkComboBox):
                data[field_name] = entry.get()
            else:
                data[field_name] = entry.get()

        # Basic validation for required fields
        if not data.get('tajan_tracking_number'):
            messagebox.showerror("Validation Error", "Tajan Tracking Number is required")
            return

        if not data.get('test_service_type'):
            messagebox.showerror("Validation Error", "Test/Service Type is required")
            return

        if not data.get('lab_name'):
            messagebox.showerror("Validation Error", "Lab Name is required")
            return

        if not data.get('invoice_date'):
            messagebox.showerror("Validation Error", "Invoice Date is required")
            return

        # Convert amount to float
        if data.get('amount_usd'):
            try:
                data['amount_usd'] = float(data['amount_usd'])
            except ValueError:
                messagebox.showerror("Validation Error", "Invalid amount format")
                return

        self.result = data
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class EditInvoiceDialog(AddInvoiceDialog):
    """Dialog for editing an existing invoice."""

    def __init__(self, parent, lab_names: List[str], test_types: List[str],
                 invoice_data: Dict[str, Any]):
        super().__init__(parent, lab_names, test_types, invoice_data)
        self.title("Edit Invoice")


class SettingsDialog(BaseDialog):
    """Dialog for managing settings (lab names and test types)."""

    def __init__(self, parent, db):
        super().__init__(parent, "Settings", 700, 500)
        self.db = db

        # Create tab view
        self.tabview = ctk.CTkTabview(self, width=660, height=420)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Lab Names Tab
        self.tabview.add("Lab Names")
        self._create_lab_names_tab()

        # Test Types Tab
        self.tabview.add("Test Types")
        self._create_test_types_tab()

        # Close button
        ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            width=100
        ).pack(pady=10)

    def _create_lab_names_tab(self):
        """Create the lab names management tab."""
        tab = self.tabview.tab("Lab Names")

        # List frame
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollable list
        self.lab_listbox = ctk.CTkScrollableFrame(list_frame, width=400, height=280)
        self.lab_listbox.pack(side="left", fill="both", expand=True)

        # Control buttons
        btn_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        btn_frame.pack(side="right", fill="y", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Add",
            command=self._add_lab_name,
            width=80
        ).pack(pady=5)

        ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=self._delete_lab_name,
            width=80,
            fg_color="red"
        ).pack(pady=5)

        # Entry for new lab name
        self.lab_entry = ctk.CTkEntry(tab, placeholder_text="Enter lab name")
        self.lab_entry.pack(fill="x", padx=10, pady=5)

        self._refresh_lab_names()

    def _create_test_types_tab(self):
        """Create the test types management tab."""
        tab = self.tabview.tab("Test Types")

        # List frame
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollable list
        self.type_listbox = ctk.CTkScrollableFrame(list_frame, width=400, height=280)
        self.type_listbox.pack(side="left", fill="both", expand=True)

        # Control buttons
        btn_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        btn_frame.pack(side="right", fill="y", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Add",
            command=self._add_test_type,
            width=80
        ).pack(pady=5)

        ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=self._delete_test_type,
            width=80,
            fg_color="red"
        ).pack(pady=5)

        # Entry for new test type
        self.type_entry = ctk.CTkEntry(tab, placeholder_text="Enter test type")
        self.type_entry.pack(fill="x", padx=10, pady=5)

        self._refresh_test_types()

    def _refresh_lab_names(self):
        """Refresh the lab names list."""
        # Clear existing
        for widget in self.lab_listbox.winfo_children():
            widget.destroy()

        self.lab_checkboxes = {}
        for lab in self.db.get_all_lab_names():
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(self.lab_listbox, text=lab, variable=var)
            cb.pack(anchor="w", pady=2)
            self.lab_checkboxes[lab] = var

    def _refresh_test_types(self):
        """Refresh the test types list."""
        # Clear existing
        for widget in self.type_listbox.winfo_children():
            widget.destroy()

        self.type_checkboxes = {}
        for test_type in self.db.get_all_test_types():
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(self.type_listbox, text=test_type, variable=var)
            cb.pack(anchor="w", pady=2)
            self.type_checkboxes[test_type] = var

    def _add_lab_name(self):
        """Add a new lab name."""
        name = self.lab_entry.get().strip()
        if name:
            if self.db.add_lab_name(name):
                self.lab_entry.delete(0, 'end')
                self._refresh_lab_names()
            else:
                messagebox.showerror("Error", "Lab name already exists")
        else:
            messagebox.showwarning("Warning", "Please enter a lab name")

    def _delete_lab_name(self):
        """Delete selected lab names."""
        to_delete = [name for name, var in self.lab_checkboxes.items() if var.get()]
        if to_delete:
            if messagebox.askyesno("Confirm", f"Delete {len(to_delete)} lab name(s)?"):
                for name in to_delete:
                    self.db.delete_lab_name(name)
                self._refresh_lab_names()

    def _add_test_type(self):
        """Add a new test type."""
        name = self.type_entry.get().strip()
        if name:
            if self.db.add_test_type(name):
                self.type_entry.delete(0, 'end')
                self._refresh_test_types()
            else:
                messagebox.showerror("Error", "Test type already exists")
        else:
            messagebox.showwarning("Warning", "Please enter a test type")

    def _delete_test_type(self):
        """Delete selected test types."""
        to_delete = [name for name, var in self.type_checkboxes.items() if var.get()]
        if to_delete:
            if messagebox.askyesno("Confirm", f"Delete {len(to_delete)} test type(s)?"):
                for name in to_delete:
                    self.db.delete_test_type(name)
                self._refresh_test_types()


class ConfirmDialog(BaseDialog):
    """Simple confirmation dialog."""

    def __init__(self, parent, title: str, message: str):
        super().__init__(parent, title, 350, 150)

        ctk.CTkLabel(
            self,
            text=message,
            wraplength=300
        ).pack(pady=30)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="No",
            command=self._no,
            width=80,
            fg_color="gray"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Yes",
            command=self._yes,
            width=80
        ).pack(side="right", padx=5)

    def _yes(self):
        self.result = True
        self.destroy()

    def _no(self):
        self.result = False
        self.destroy()


class LabSelectionDialog(BaseDialog):
    """Dialog for selecting lab name when auto-detection fails."""

    def __init__(self, parent, lab_names: List[str], filename: str):
        super().__init__(parent, "Select Lab Name", 400, 200)

        ctk.CTkLabel(
            self,
            text=f"Could not detect lab name from:\n{filename}",
            wraplength=350
        ).pack(pady=15)

        ctk.CTkLabel(
            self,
            text="Please select the lab:"
        ).pack(pady=5)

        self.lab_combo = ctk.CTkComboBox(self, values=lab_names, width=200)
        self.lab_combo.pack(pady=10)
        if lab_names:
            self.lab_combo.set(lab_names[0])

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.cancel,
            width=80,
            fg_color="gray"
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="OK",
            command=self.confirm,
            width=80
        ).pack(side="right", padx=5)

    def confirm(self):
        self.result = self.lab_combo.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()
