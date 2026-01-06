"""
Validation Module for Invoice Management System
Handles validation of invoice data before storage.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of invoice validation."""
    is_valid: bool
    errors: List[str]
    record: Dict[str, Any]


class InvoiceValidator:
    """Validator for invoice records."""

    def __init__(self, allowed_test_types: List[str] = None):
        """
        Initialize validator.

        Args:
            allowed_test_types: List of valid test/service types
        """
        self.allowed_test_types = allowed_test_types or []
        # Create a set for faster lookup (case-insensitive)
        self._test_types_lower = {t.lower().strip() for t in self.allowed_test_types}

    def update_test_types(self, test_types: List[str]):
        """Update the list of allowed test types."""
        self.allowed_test_types = test_types
        self._test_types_lower = {t.lower().strip() for t in test_types}

    def validate_record(self, record: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single invoice record.

        Args:
            record: Invoice record dictionary

        Returns:
            ValidationResult with validation status and any errors
        """
        errors = []

        # Rule 1: Missing Tracking Number
        tracking_number = record.get('tajan_tracking_number', '').strip()
        if not tracking_number:
            errors.append("Missing Tajan Bidding Tracking Number")

        # Rule 2: Invalid Test Type
        test_type = record.get('test_service_type', '').strip()
        if test_type:
            if test_type.lower() not in self._test_types_lower:
                errors.append(f"Invalid Test/Service Type: '{test_type}'")
        else:
            # Empty test type is also considered invalid
            errors.append("Missing Test/Service Type")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            record=record
        )

    def validate_records(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Tuple[Dict[str, Any], str]]]:
        """
        Validate multiple invoice records.

        Args:
            records: List of invoice records

        Returns:
            Tuple of (valid_records, abnormal_records_with_errors)
        """
        valid_records = []
        abnormal_records = []

        for record in records:
            result = self.validate_record(record)
            if result.is_valid:
                valid_records.append(result.record)
            else:
                # Combine all errors into a single string
                error_message = "; ".join(result.errors)
                abnormal_records.append((result.record, error_message))

        return valid_records, abnormal_records

    def validate_for_correction(self, record: Dict[str, Any]) -> List[str]:
        """
        Validate a record that's being corrected.
        Returns list of remaining issues.

        Args:
            record: The corrected record

        Returns:
            List of validation error messages
        """
        result = self.validate_record(record)
        return result.errors


class DataIntegrityChecker:
    """Check data integrity and consistency."""

    @staticmethod
    def check_duplicates(records: List[Dict[str, Any]], key_field: str = 'tajan_tracking_number') -> List[Dict[str, Any]]:
        """
        Find duplicate records based on a key field.

        Args:
            records: List of records to check
            key_field: Field to check for duplicates

        Returns:
            List of records that have duplicates
        """
        seen = {}
        duplicates = []

        for record in records:
            key = record.get(key_field, '').strip()
            if key:
                if key in seen:
                    if seen[key] not in duplicates:
                        duplicates.append(seen[key])
                    duplicates.append(record)
                else:
                    seen[key] = record

        return duplicates

    @staticmethod
    def check_amount_validity(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find records with invalid or suspicious amounts.

        Args:
            records: List of records to check

        Returns:
            List of records with amount issues
        """
        suspicious = []

        for record in records:
            amount = record.get('amount_usd')
            if amount is not None:
                try:
                    amt = float(amount)
                    if amt < 0:
                        suspicious.append(record)
                    elif amt > 1000000:  # Suspiciously large
                        suspicious.append(record)
                except (ValueError, TypeError):
                    suspicious.append(record)

        return suspicious

    @staticmethod
    def check_date_consistency(record: Dict[str, Any]) -> List[str]:
        """
        Check date field consistency.

        Args:
            record: Record to check

        Returns:
            List of warnings about date inconsistencies
        """
        warnings = []

        request_date = record.get('request_date', '')
        test_start_date = record.get('test_start_date', '')
        report_date = record.get('report_delivered_date', '')

        # Basic checks - dates should be in logical order
        if request_date and test_start_date:
            if request_date > test_start_date:
                warnings.append("Test start date is before request date")

        if test_start_date and report_date:
            if test_start_date > report_date:
                warnings.append("Report delivered date is before test start date")

        return warnings
