"""
Excel Parser Module for Invoice Management System
Handles parsing of Excel files from testing labs (BV, ITS, TUV, SGS).
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet


class ExcelParser:
    """Parser for Excel invoice files."""

    # Expected column headers mapping to database fields
    HEADER_MAPPING = {
        "Tajan Bidding Tracking Number": "tajan_tracking_number",
        "Amazon Test Request #": "amazon_test_request",
        "Amazon Tracker Number": "amazon_tracker_number",
        "ASIN#": "asin",
        "Development Center (SEA, LUX/EU, JP)": "development_center",
        "Category (New HCC)": "category",
        "Product Brand": "product_brand",
        "Product Description": "product_description",
        "Testing SLA (Working days)": "testing_sla",
        "Test / Service Type": "test_service_type",
        "Quotation/Order Number": "quotation_order_number",
        "Request Date": "request_date",
        "Test Start Date": "test_start_date",
        "Report Delivered Date": "report_delivered_date",
        "Report number": "report_number",
        "Test / inspection Location": "test_location",
        "Product line": "product_line",
        "AMAZON QUALITY MANAGER": "amazon_quality_manager",
        "AMAZON SOURCING MANAGER": "amazon_sourcing_manager",
        "Invoice #": "invoice_number",
        "Lab contact": "lab_contact",
        "COMMENT (IF ANY)": "comment",
        "AMOUNT (Currency=USD)": "amount_usd",
    }

    # Rows to skip (subtotals, etc.)
    SKIP_KEYWORDS = [
        "subtotal", "sub total", "sub-total",
        "tax rate", "sales tax",
        "freight",
        "total", "grand total"
    ]

    # Target sheet name
    TARGET_SHEET = "TESTING+SERVICES"

    def __init__(self, lab_names: List[str] = None):
        """
        Initialize the parser.

        Args:
            lab_names: List of valid lab names for detection
        """
        self.lab_names = lab_names or ["BV", "ITS", "TUV", "SGS"]

    def detect_lab_name(self, filename: str) -> Optional[str]:
        """
        Detect lab name from filename.

        Args:
            filename: Name of the Excel file

        Returns:
            Detected lab name or None
        """
        filename_upper = filename.upper()
        for lab in self.lab_names:
            if lab.upper() in filename_upper:
                return lab.upper()
        return None

    def parse_file(self, file_path: str, invoice_date: str = None) -> Tuple[List[Dict[str, Any]], Optional[str], List[str]]:
        """
        Parse an Excel file and extract invoice data.

        Args:
            file_path: Path to the Excel file
            invoice_date: Optional invoice date to assign to all rows

        Returns:
            Tuple of (list of invoice records, detected lab name, list of warnings)
        """
        warnings = []
        records = []

        # Get filename for lab detection
        filename = os.path.basename(file_path)
        lab_name = self.detect_lab_name(filename)

        if not lab_name:
            warnings.append(f"Could not detect lab name from filename: {filename}")

        try:
            workbook = load_workbook(file_path, data_only=True)
        except Exception as e:
            raise ValueError(f"Failed to open Excel file: {str(e)}")

        # Find the TESTING+SERVICES sheet
        sheet = None
        for sheet_name in workbook.sheetnames:
            if self.TARGET_SHEET.lower() in sheet_name.lower():
                sheet = workbook[sheet_name]
                break

        if sheet is None:
            # Try to find a similar sheet
            available_sheets = ", ".join(workbook.sheetnames)
            raise ValueError(
                f"Sheet '{self.TARGET_SHEET}' not found. "
                f"Available sheets: {available_sheets}"
            )

        # Parse the sheet
        records, parse_warnings = self._parse_sheet(sheet, lab_name, invoice_date)
        warnings.extend(parse_warnings)

        workbook.close()
        return records, lab_name, warnings

    def _parse_sheet(self, sheet: Worksheet, lab_name: str, invoice_date: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parse a worksheet and extract records.

        Args:
            sheet: The worksheet to parse
            lab_name: Detected lab name
            invoice_date: Invoice date to assign

        Returns:
            Tuple of (list of records, list of warnings)
        """
        warnings = []
        records = []

        # Find header row
        header_row_idx = None
        header_mapping = {}

        for row_idx, row in enumerate(sheet.iter_rows(min_row=1, max_row=50), start=1):
            row_values = [cell.value for cell in row]
            # Check if this row contains expected headers
            matches = 0
            for cell_idx, value in enumerate(row_values):
                if value and str(value).strip() in self.HEADER_MAPPING:
                    matches += 1
                    header_mapping[cell_idx] = self.HEADER_MAPPING[str(value).strip()]

            if matches >= 5:  # Found at least 5 matching headers
                header_row_idx = row_idx
                break

        if header_row_idx is None:
            warnings.append("Could not find header row with expected columns")
            return records, warnings

        # Parse data rows
        for row_idx, row in enumerate(sheet.iter_rows(min_row=header_row_idx + 1), start=header_row_idx + 1):
            row_values = [cell.value for cell in row]

            # Skip empty rows
            if self._is_empty_row(row_values):
                continue

            # Skip subtotal/total rows
            if self._is_skip_row(row_values):
                continue

            # Build record
            record = self._build_record(row_values, header_mapping, lab_name, invoice_date)
            if record:
                records.append(record)

        return records, warnings

    def _is_empty_row(self, row_values: List[Any]) -> bool:
        """Check if a row is completely empty."""
        return all(v is None or str(v).strip() == "" for v in row_values)

    def _is_skip_row(self, row_values: List[Any]) -> bool:
        """Check if a row should be skipped (subtotal, total, etc.)."""
        for value in row_values:
            if value:
                value_str = str(value).lower().strip()
                for keyword in self.SKIP_KEYWORDS:
                    if keyword in value_str:
                        return True
        return False

    def _build_record(self, row_values: List[Any], header_mapping: Dict[int, str],
                      lab_name: str, invoice_date: str) -> Optional[Dict[str, Any]]:
        """
        Build a record dictionary from row values.

        Args:
            row_values: List of cell values
            header_mapping: Mapping of column index to field name
            lab_name: Detected lab name
            invoice_date: Invoice date

        Returns:
            Record dictionary or None
        """
        record = {}

        for col_idx, field_name in header_mapping.items():
            if col_idx < len(row_values):
                value = row_values[col_idx]
                # Convert to string for non-numeric fields, handle None
                if field_name == "amount_usd":
                    record[field_name] = self._parse_amount(value)
                elif field_name in ["request_date", "test_start_date", "report_delivered_date"]:
                    record[field_name] = self._parse_date(value)
                else:
                    record[field_name] = str(value).strip() if value is not None else ""

        # Add lab name and invoice date
        record["lab_name"] = lab_name or ""
        record["invoice_date"] = invoice_date or ""

        return record

    def _parse_amount(self, value: Any) -> Optional[float]:
        """Parse amount value to float."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[,$\s]', '', str(value))
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    def _parse_date(self, value: Any) -> str:
        """Parse date value to string."""
        if value is None:
            return ""
        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')
        return str(value).strip()

    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        Get all sheet names from an Excel file.

        Args:
            file_path: Path to the Excel file

        Returns:
            List of sheet names
        """
        try:
            workbook = load_workbook(file_path, read_only=True)
            names = workbook.sheetnames
            workbook.close()
            return names
        except Exception as e:
            raise ValueError(f"Failed to read Excel file: {str(e)}")
