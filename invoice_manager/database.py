"""
SQLite Database Module for Invoice Management System
Handles all database operations including CRUD for invoices, lab names, and test types.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple


class Database:
    """Database handler for the Invoice Management System."""

    # Default allowed test/service types
    DEFAULT_TEST_TYPES = [
        "Benchmark Test", "Benchmark Sample Purchase", "Usability Test",
        "Usability Protocol", "Comparison", "DDC Design Document Collection",
        "Delorean DDC", "DP Review", "PRD & Protocol Upgrade",
        "Performance Protocol", "PVT", "PT", "PPT", "PT-Initial",
        "PT-Final", "ET", "VT", "Delorean PT", "Packaging",
        "Failure & Defect Analysis", "Declaration of Conformity", "ECR"
    ]

    # Default lab names
    DEFAULT_LAB_NAMES = ["BV", "ITS", "TUV", "SGS"]

    def __init__(self, db_path: str = "invoice_manager.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
        self._initialize_defaults()

    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def _create_tables(self):
        """Create all required database tables."""
        # Main invoices table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tajan_tracking_number TEXT,
                amazon_test_request TEXT,
                amazon_tracker_number TEXT,
                asin TEXT,
                development_center TEXT,
                category TEXT,
                product_brand TEXT,
                product_description TEXT,
                testing_sla TEXT,
                test_service_type TEXT,
                quotation_order_number TEXT,
                request_date TEXT,
                test_start_date TEXT,
                report_delivered_date TEXT,
                report_number TEXT,
                test_location TEXT,
                product_line TEXT,
                amazon_quality_manager TEXT,
                amazon_sourcing_manager TEXT,
                invoice_number TEXT,
                lab_contact TEXT,
                comment TEXT,
                amount_usd REAL,
                lab_name TEXT,
                invoice_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Abnormal invoice items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS abnormal_invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tajan_tracking_number TEXT,
                amazon_test_request TEXT,
                amazon_tracker_number TEXT,
                asin TEXT,
                development_center TEXT,
                category TEXT,
                product_brand TEXT,
                product_description TEXT,
                testing_sla TEXT,
                test_service_type TEXT,
                quotation_order_number TEXT,
                request_date TEXT,
                test_start_date TEXT,
                report_delivered_date TEXT,
                report_number TEXT,
                test_location TEXT,
                product_line TEXT,
                amazon_quality_manager TEXT,
                amazon_sourcing_manager TEXT,
                invoice_number TEXT,
                lab_contact TEXT,
                comment TEXT,
                amount_usd REAL,
                lab_name TEXT,
                invoice_date TEXT,
                validation_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Lab names configuration table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lab_names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Test/Service types configuration table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def _initialize_defaults(self):
        """Initialize default lab names and test types if not exist."""
        # Check if lab names exist
        self.cursor.execute("SELECT COUNT(*) FROM lab_names")
        if self.cursor.fetchone()[0] == 0:
            for lab in self.DEFAULT_LAB_NAMES:
                self.add_lab_name(lab)

        # Check if test types exist
        self.cursor.execute("SELECT COUNT(*) FROM test_types")
        if self.cursor.fetchone()[0] == 0:
            for test_type in self.DEFAULT_TEST_TYPES:
                self.add_test_type(test_type)

    # ==================== Invoice Operations ====================

    def add_invoice(self, invoice_data: Dict[str, Any]) -> int:
        """Add a new invoice to the database."""
        columns = ', '.join(invoice_data.keys())
        placeholders = ', '.join(['?' for _ in invoice_data])
        query = f"INSERT INTO invoices ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, list(invoice_data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_invoices_batch(self, invoices: List[Dict[str, Any]]) -> int:
        """Add multiple invoices in a batch."""
        if not invoices:
            return 0

        columns = list(invoices[0].keys())
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO invoices ({columns_str}) VALUES ({placeholders})"

        values = [tuple(inv.get(col) for col in columns) for inv in invoices]
        self.cursor.executemany(query, values)
        self.conn.commit()
        return len(invoices)

    def get_all_invoices(self) -> List[Dict[str, Any]]:
        """Retrieve all invoices."""
        self.cursor.execute("SELECT * FROM invoices ORDER BY id DESC")
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def get_invoice_by_id(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific invoice by ID."""
        self.cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def update_invoice(self, invoice_id: int, updates: Dict[str, Any]) -> bool:
        """Update an existing invoice."""
        if not updates:
            return False

        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE invoices SET {set_clause} WHERE id = ?"

        self.cursor.execute(query, list(updates.values()) + [invoice_id])
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_invoice(self, invoice_id: int) -> bool:
        """Delete an invoice by ID."""
        self.cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_invoices_batch(self, invoice_ids: List[int]) -> int:
        """Delete multiple invoices."""
        if not invoice_ids:
            return 0

        placeholders = ', '.join(['?' for _ in invoice_ids])
        self.cursor.execute(f"DELETE FROM invoices WHERE id IN ({placeholders})", invoice_ids)
        self.conn.commit()
        return self.cursor.rowcount

    def search_invoices(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search invoices with various filters."""
        query = "SELECT * FROM invoices WHERE 1=1"
        params = []

        if filters.get('lab_name'):
            query += " AND lab_name = ?"
            params.append(filters['lab_name'])

        if filters.get('date_from'):
            query += " AND invoice_date >= ?"
            params.append(filters['date_from'])

        if filters.get('date_to'):
            query += " AND invoice_date <= ?"
            params.append(filters['date_to'])

        if filters.get('search_text'):
            search = f"%{filters['search_text']}%"
            query += """ AND (
                tajan_tracking_number LIKE ? OR
                amazon_test_request LIKE ? OR
                asin LIKE ? OR
                product_brand LIKE ? OR
                product_description LIKE ? OR
                invoice_number LIKE ?
            )"""
            params.extend([search] * 6)

        query += " ORDER BY id DESC"
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    # ==================== Abnormal Invoice Operations ====================

    def add_abnormal_invoice(self, invoice_data: Dict[str, Any], validation_error: str) -> int:
        """Add an invoice to the abnormal items table."""
        invoice_data['validation_error'] = validation_error
        columns = ', '.join(invoice_data.keys())
        placeholders = ', '.join(['?' for _ in invoice_data])
        query = f"INSERT INTO abnormal_invoices ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, list(invoice_data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_abnormal_invoices_batch(self, invoices: List[Tuple[Dict[str, Any], str]]) -> int:
        """Add multiple abnormal invoices in a batch."""
        if not invoices:
            return 0

        count = 0
        for invoice_data, error in invoices:
            self.add_abnormal_invoice(invoice_data, error)
            count += 1
        return count

    def get_all_abnormal_invoices(self) -> List[Dict[str, Any]]:
        """Retrieve all abnormal invoices."""
        self.cursor.execute("SELECT * FROM abnormal_invoices ORDER BY id DESC")
        return [dict(row) for row in self.cursor.fetchall()]

    def delete_abnormal_invoice(self, invoice_id: int) -> bool:
        """Delete an abnormal invoice by ID."""
        self.cursor.execute("DELETE FROM abnormal_invoices WHERE id = ?", (invoice_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def move_to_valid(self, abnormal_id: int, updates: Dict[str, Any] = None) -> bool:
        """Move an abnormal invoice to the valid invoices table after correction."""
        self.cursor.execute("SELECT * FROM abnormal_invoices WHERE id = ?", (abnormal_id,))
        row = self.cursor.fetchone()
        if not row:
            return False

        invoice_data = dict(row)
        # Remove abnormal-specific fields
        del invoice_data['id']
        del invoice_data['validation_error']
        del invoice_data['created_at']

        # Apply any updates
        if updates:
            invoice_data.update(updates)

        # Add to valid invoices
        self.add_invoice(invoice_data)
        # Remove from abnormal
        self.delete_abnormal_invoice(abnormal_id)
        return True

    # ==================== Lab Name Operations ====================

    def add_lab_name(self, name: str) -> bool:
        """Add a new lab name."""
        try:
            self.cursor.execute("INSERT INTO lab_names (name) VALUES (?)", (name.upper(),))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_lab_names(self) -> List[str]:
        """Get all configured lab names."""
        self.cursor.execute("SELECT name FROM lab_names ORDER BY name")
        return [row[0] for row in self.cursor.fetchall()]

    def delete_lab_name(self, name: str) -> bool:
        """Delete a lab name."""
        self.cursor.execute("DELETE FROM lab_names WHERE name = ?", (name.upper(),))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_lab_name(self, old_name: str, new_name: str) -> bool:
        """Update a lab name."""
        try:
            self.cursor.execute(
                "UPDATE lab_names SET name = ? WHERE name = ?",
                (new_name.upper(), old_name.upper())
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False

    # ==================== Test Type Operations ====================

    def add_test_type(self, name: str) -> bool:
        """Add a new test/service type."""
        try:
            self.cursor.execute("INSERT INTO test_types (name) VALUES (?)", (name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_test_types(self) -> List[str]:
        """Get all configured test/service types."""
        self.cursor.execute("SELECT name FROM test_types ORDER BY name")
        return [row[0] for row in self.cursor.fetchall()]

    def delete_test_type(self, name: str) -> bool:
        """Delete a test/service type."""
        self.cursor.execute("DELETE FROM test_types WHERE name = ?", (name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_test_type(self, old_name: str, new_name: str) -> bool:
        """Update a test/service type."""
        try:
            self.cursor.execute(
                "UPDATE test_types SET name = ? WHERE name = ?",
                (new_name, old_name)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False

    # ==================== Utility Operations ====================

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}

        self.cursor.execute("SELECT COUNT(*) FROM invoices")
        stats['total_invoices'] = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM abnormal_invoices")
        stats['abnormal_invoices'] = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT lab_name, COUNT(*) FROM invoices GROUP BY lab_name")
        stats['by_lab'] = {row[0]: row[1] for row in self.cursor.fetchall()}

        self.cursor.execute("SELECT SUM(amount_usd) FROM invoices")
        result = self.cursor.fetchone()[0]
        stats['total_amount'] = result if result else 0.0

        return stats

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
