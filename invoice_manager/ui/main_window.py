"""
Main Window for Invoice Management System
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import List, Dict, Any, Optional

from .data_table import DataTable, FilterBar
from .dialogs import (
    InvoiceDateDialog,
    AddInvoiceDialog,
    EditInvoiceDialog,
    SettingsDialog,
    ConfirmDialog,
    LabSelectionDialog
)

# Import from parent package
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Database
from excel_parser import ExcelParser
from validators import InvoiceValidator


class InvoiceManagerApp(ctk.CTk):
    """Main application window for Invoice Management System."""

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Invoice Management System")
        self.geometry("1400x800")
        self.minsize(1200, 600)

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize database
        self.db = Database()

        # Initialize parser and validator
        self.parser = ExcelParser(self.db.get_all_lab_names())
        self.validator = InvoiceValidator(self.db.get_all_test_types())

        # Selected rows tracking
        self.selected_invoice_ids = []
        self.selected_abnormal_ids = []

        # Build UI
        self._create_toolbar()
        self._create_tabs()
        self._create_status_bar()

        # Load initial data
        self._refresh_data()

        # Bind window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_toolbar(self):
        """Create the top toolbar."""
        toolbar = ctk.CTkFrame(self, height=50)
        toolbar.pack(fill="x", padx=10, pady=5)
        toolbar.pack_propagate(False)

        # Upload button
        ctk.CTkButton(
            toolbar,
            text="Upload Invoice",
            command=self._upload_invoice,
            width=140
        ).pack(side="left", padx=5, pady=5)

        # Add Row button
        ctk.CTkButton(
            toolbar,
            text="Add Row",
            command=self._add_invoice,
            width=100
        ).pack(side="left", padx=5, pady=5)

        # Delete Row button
        ctk.CTkButton(
            toolbar,
            text="Delete Row",
            command=self._delete_selected,
            width=110,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left", padx=5, pady=5)

        # Edit button
        ctk.CTkButton(
            toolbar,
            text="Edit",
            command=self._edit_selected,
            width=80
        ).pack(side="left", padx=5, pady=5)

        # Refresh button
        ctk.CTkButton(
            toolbar,
            text="Refresh",
            command=self._refresh_data,
            width=100
        ).pack(side="left", padx=5, pady=5)

        # Settings button (right side)
        ctk.CTkButton(
            toolbar,
            text="Settings",
            command=self._open_settings,
            width=100
        ).pack(side="right", padx=5, pady=5)

        # Export button
        ctk.CTkButton(
            toolbar,
            text="Export",
            command=self._export_data,
            width=100
        ).pack(side="right", padx=5, pady=5)

    def _create_tabs(self):
        """Create the tabbed interface."""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)

        # Valid Invoices Tab
        self.tabview.add("Valid Invoices")
        self._create_valid_invoices_tab()

        # Abnormal Items Tab
        self.tabview.add("Abnormal Items")
        self._create_abnormal_items_tab()

        # Statistics Tab
        self.tabview.add("Statistics")
        self._create_statistics_tab()

    def _create_valid_invoices_tab(self):
        """Create the valid invoices tab."""
        tab = self.tabview.tab("Valid Invoices")

        # Filter bar
        self.valid_filter = FilterBar(
            tab,
            self.db.get_all_lab_names(),
            self._apply_valid_filter
        )
        self.valid_filter.pack(fill="x", padx=5, pady=5)

        # Data table
        self.valid_table = DataTable(
            tab,
            is_abnormal=False,
            on_select=self._on_valid_select,
            on_double_click=self._on_valid_double_click
        )
        self.valid_table.pack(fill="both", expand=True, padx=5, pady=5)

    def _create_abnormal_items_tab(self):
        """Create the abnormal items tab."""
        tab = self.tabview.tab("Abnormal Items")

        # Info label
        info_frame = ctk.CTkFrame(tab, fg_color="orange", corner_radius=5)
        info_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(
            info_frame,
            text="These items failed validation. Double-click to edit and fix, then move to valid invoices.",
            text_color="black"
        ).pack(pady=5)

        # Action buttons for abnormal items
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="Fix & Move to Valid",
            command=self._fix_and_move,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Delete Selected",
            command=self._delete_abnormal_selected,
            width=130,
            fg_color="red"
        ).pack(side="left", padx=5)

        # Data table
        self.abnormal_table = DataTable(
            tab,
            is_abnormal=True,
            on_select=self._on_abnormal_select,
            on_double_click=self._on_abnormal_double_click
        )
        self.abnormal_table.pack(fill="both", expand=True, padx=5, pady=5)

    def _create_statistics_tab(self):
        """Create the statistics tab."""
        tab = self.tabview.tab("Statistics")

        self.stats_frame = ctk.CTkScrollableFrame(tab)
        self.stats_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.pack(fill="x", padx=10, pady=5)
        self.status_bar.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10)

        self.count_label = ctk.CTkLabel(
            self.status_bar,
            text="",
            anchor="e"
        )
        self.count_label.pack(side="right", padx=10)

    def _set_status(self, message: str):
        """Update the status bar message."""
        self.status_label.configure(text=message)
        self.update_idletasks()

    def _update_counts(self):
        """Update the record counts in status bar."""
        valid_count = self.valid_table.get_record_count()
        abnormal_count = self.abnormal_table.get_record_count()
        self.count_label.configure(
            text=f"Valid: {valid_count} | Abnormal: {abnormal_count}"
        )

    # ==================== Data Operations ====================

    def _refresh_data(self):
        """Refresh all data from database."""
        self._set_status("Refreshing data...")

        # Load valid invoices
        valid_data = self.db.get_all_invoices()
        self.valid_table.load_data(valid_data)

        # Load abnormal invoices
        abnormal_data = self.db.get_all_abnormal_invoices()
        self.abnormal_table.load_data(abnormal_data)

        # Update statistics
        self._update_statistics()

        # Update counts
        self._update_counts()

        # Update filter dropdowns with current lab names
        lab_names = self.db.get_all_lab_names()
        self.valid_filter.update_lab_names(lab_names)
        self.parser.lab_names = lab_names

        # Update validator with current test types
        self.validator.update_test_types(self.db.get_all_test_types())

        self._set_status("Ready")

    def _apply_valid_filter(self, filters: Dict[str, Any]):
        """Apply filters to valid invoices."""
        if filters:
            data = self.db.search_invoices(filters)
        else:
            data = self.db.get_all_invoices()
        self.valid_table.load_data(data)
        self._update_counts()

    def _update_statistics(self):
        """Update the statistics display."""
        # Clear existing
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = self.db.get_statistics()

        # Title
        ctk.CTkLabel(
            self.stats_frame,
            text="Invoice Statistics",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=10)

        # Summary cards
        cards_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)

        # Total invoices card
        self._create_stat_card(
            cards_frame,
            "Total Valid Invoices",
            str(stats['total_invoices']),
            "blue"
        )

        # Abnormal count card
        self._create_stat_card(
            cards_frame,
            "Abnormal Items",
            str(stats['abnormal_invoices']),
            "orange"
        )

        # Total amount card
        self._create_stat_card(
            cards_frame,
            "Total Amount (USD)",
            f"${stats['total_amount']:,.2f}",
            "green"
        )

        # By lab breakdown
        ctk.CTkLabel(
            self.stats_frame,
            text="Invoices by Lab",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(20, 10))

        for lab, count in stats.get('by_lab', {}).items():
            lab_frame = ctk.CTkFrame(self.stats_frame)
            lab_frame.pack(fill="x", pady=2)
            ctk.CTkLabel(lab_frame, text=f"{lab or 'Unknown'}:", width=100).pack(side="left", padx=10)
            ctk.CTkLabel(lab_frame, text=str(count)).pack(side="left")

    def _create_stat_card(self, parent, title: str, value: str, color: str):
        """Create a statistics card."""
        colors = {
            "blue": "#1f538d",
            "green": "#2d8659",
            "orange": "#cc7a00"
        }
        card = ctk.CTkFrame(parent, fg_color=colors.get(color, "gray"))
        card.pack(side="left", padx=10, pady=5, ipadx=20, ipady=10)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12)
        ).pack()

        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack()

    # ==================== Upload Operations ====================

    def _upload_invoice(self):
        """Handle invoice file upload."""
        file_path = filedialog.askopenfilename(
            title="Select Invoice Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )

        if not file_path:
            return

        filename = os.path.basename(file_path)
        detected_lab = self.parser.detect_lab_name(filename)

        # Show date input dialog
        dialog = InvoiceDateDialog(self, filename, detected_lab)
        self.wait_window(dialog)

        if dialog.result is None:
            return

        invoice_date = dialog.result

        # If lab not detected, ask user to select
        if not detected_lab:
            lab_dialog = LabSelectionDialog(
                self,
                self.db.get_all_lab_names(),
                filename
            )
            self.wait_window(lab_dialog)
            if lab_dialog.result:
                detected_lab = lab_dialog.result
            else:
                messagebox.showwarning("Warning", "Upload cancelled - no lab selected")
                return

        self._set_status(f"Parsing {filename}...")

        try:
            records, lab_name, warnings = self.parser.parse_file(file_path, invoice_date)

            # Override lab name if user selected one
            if detected_lab:
                for record in records:
                    record['lab_name'] = detected_lab

            if warnings:
                messagebox.showwarning("Parse Warnings", "\n".join(warnings))

            if not records:
                messagebox.showinfo("Info", "No data rows found in the file")
                return

            # Validate records
            self._set_status("Validating records...")
            valid_records, abnormal_records = self.validator.validate_records(records)

            # Save to database
            self._set_status("Saving to database...")

            valid_count = 0
            if valid_records:
                valid_count = self.db.add_invoices_batch(valid_records)

            abnormal_count = 0
            if abnormal_records:
                abnormal_count = self.db.add_abnormal_invoices_batch(abnormal_records)

            # Refresh display
            self._refresh_data()

            # Show summary
            messagebox.showinfo(
                "Upload Complete",
                f"Successfully processed {filename}\n\n"
                f"Valid records: {valid_count}\n"
                f"Abnormal records: {abnormal_count}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse file:\n{str(e)}")
            self._set_status("Ready")

    # ==================== CRUD Operations ====================

    def _add_invoice(self):
        """Add a new invoice manually."""
        dialog = AddInvoiceDialog(
            self,
            self.db.get_all_lab_names(),
            self.db.get_all_test_types()
        )
        self.wait_window(dialog)

        if dialog.result:
            # Validate the new invoice
            result = self.validator.validate_record(dialog.result)

            if result.is_valid:
                self.db.add_invoice(dialog.result)
                self._refresh_data()
                messagebox.showinfo("Success", "Invoice added successfully")
            else:
                # Ask if user wants to add to abnormal
                errors = "\n".join(result.errors)
                if messagebox.askyesno(
                        "Validation Failed",
                        f"Invoice has validation errors:\n{errors}\n\n"
                        "Add to Abnormal Items instead?"
                ):
                    self.db.add_abnormal_invoice(dialog.result, "; ".join(result.errors))
                    self._refresh_data()

    def _edit_selected(self):
        """Edit the selected invoice."""
        # Check which tab is active
        current_tab = self.tabview.get()

        if current_tab == "Valid Invoices":
            if self.selected_invoice_ids:
                self._on_valid_double_click(self.selected_invoice_ids[0])
            else:
                messagebox.showwarning("Warning", "Please select an invoice to edit")
        elif current_tab == "Abnormal Items":
            if self.selected_abnormal_ids:
                self._on_abnormal_double_click(self.selected_abnormal_ids[0])
            else:
                messagebox.showwarning("Warning", "Please select an item to edit")

    def _delete_selected(self):
        """Delete selected invoices."""
        if not self.selected_invoice_ids:
            messagebox.showwarning("Warning", "Please select invoices to delete")
            return

        count = len(self.selected_invoice_ids)
        if messagebox.askyesno("Confirm Delete", f"Delete {count} selected invoice(s)?"):
            self.db.delete_invoices_batch(self.selected_invoice_ids)
            self.selected_invoice_ids = []
            self._refresh_data()

    def _delete_abnormal_selected(self):
        """Delete selected abnormal items."""
        if not self.selected_abnormal_ids:
            messagebox.showwarning("Warning", "Please select items to delete")
            return

        count = len(self.selected_abnormal_ids)
        if messagebox.askyesno("Confirm Delete", f"Delete {count} selected item(s)?"):
            for item_id in self.selected_abnormal_ids:
                self.db.delete_abnormal_invoice(item_id)
            self.selected_abnormal_ids = []
            self._refresh_data()

    def _fix_and_move(self):
        """Fix selected abnormal item and move to valid."""
        if not self.selected_abnormal_ids:
            messagebox.showwarning("Warning", "Please select an item to fix")
            return

        if len(self.selected_abnormal_ids) > 1:
            messagebox.showwarning("Warning", "Please select only one item at a time")
            return

        self._on_abnormal_double_click(self.selected_abnormal_ids[0])

    # ==================== Selection Handlers ====================

    def _on_valid_select(self, ids: List[int]):
        """Handle selection in valid invoices table."""
        self.selected_invoice_ids = ids

    def _on_valid_double_click(self, invoice_id: int):
        """Handle double-click on valid invoice."""
        invoice = self.db.get_invoice_by_id(invoice_id)
        if invoice:
            dialog = EditInvoiceDialog(
                self,
                self.db.get_all_lab_names(),
                self.db.get_all_test_types(),
                invoice
            )
            self.wait_window(dialog)

            if dialog.result:
                self.db.update_invoice(invoice_id, dialog.result)
                self._refresh_data()

    def _on_abnormal_select(self, ids: List[int]):
        """Handle selection in abnormal items table."""
        self.selected_abnormal_ids = ids

    def _on_abnormal_double_click(self, item_id: int):
        """Handle double-click on abnormal item."""
        # Get the abnormal invoice data
        abnormal_invoices = self.db.get_all_abnormal_invoices()
        item = next((i for i in abnormal_invoices if i['id'] == item_id), None)

        if item:
            dialog = EditInvoiceDialog(
                self,
                self.db.get_all_lab_names(),
                self.db.get_all_test_types(),
                item
            )
            self.wait_window(dialog)

            if dialog.result:
                # Re-validate the corrected data
                result = self.validator.validate_record(dialog.result)

                if result.is_valid:
                    # Move to valid invoices
                    self.db.move_to_valid(item_id, dialog.result)
                    self._refresh_data()
                    messagebox.showinfo("Success", "Item corrected and moved to valid invoices")
                else:
                    # Still has errors, ask what to do
                    errors = "\n".join(result.errors)
                    messagebox.showwarning(
                        "Still Invalid",
                        f"Item still has validation errors:\n{errors}\n\n"
                        "Please correct these issues."
                    )

    # ==================== Settings ====================

    def _open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self, self.db)
        self.wait_window(dialog)

        # Refresh data to pick up any changes
        self._refresh_data()

    # ==================== Export ====================

    def _export_data(self):
        """Export data to Excel file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Invoices",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            import pandas as pd

            # Get all valid invoices
            invoices = self.db.get_all_invoices()

            if not invoices:
                messagebox.showwarning("Warning", "No data to export")
                return

            # Convert to DataFrame
            df = pd.DataFrame(invoices)

            # Remove internal columns
            columns_to_remove = ['created_at', 'updated_at']
            for col in columns_to_remove:
                if col in df.columns:
                    df = df.drop(columns=[col])

            # Export to Excel
            df.to_excel(file_path, index=False, sheet_name='Invoices')

            messagebox.showinfo("Success", f"Exported {len(invoices)} invoices to:\n{file_path}")

        except ImportError:
            messagebox.showerror("Error", "pandas is required for export. Please install it.")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")

    # ==================== Cleanup ====================

    def _on_closing(self):
        """Handle window close."""
        self.db.close()
        self.destroy()


def main():
    """Main entry point."""
    app = InvoiceManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
