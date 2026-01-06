# Invoice Management System

A local Windows desktop application for managing Excel-based invoice data from multiple testing labs (BV, ITS, TUV, SGS).

## Features

### Core Functionality
- **Excel Invoice Upload**: Parse invoice data from Excel files with TESTING+SERVICES tab
- **Lab Name Detection**: Auto-detect lab name (BV, ITS, TUV, SGS) from filename
- **Data Validation**: Automatic validation with abnormal items tracking
- **CRUD Operations**: View, add, edit, and delete invoice records
- **Filter & Search**: Filter by lab name, date range, or search text
- **Export**: Export data to Excel format

### Data Validation Rules
The system validates uploaded invoices against these rules:
1. **Missing Tracking Number**: Tajan Bidding Tracking Number must not be empty
2. **Invalid Test Type**: Test/Service Type must be in the allowed list

### Supported Test/Service Types (22 types)
- Benchmark Test
- Benchmark Sample Purchase
- Usability Test
- Usability Protocol
- Comparison
- DDC Design Document Collection
- Delorean DDC
- DP Review
- PRD & Protocol Upgrade
- Performance Protocol
- PVT, PT, PPT, PT-Initial, PT-Final, ET, VT
- Delorean PT
- Packaging
- Failure & Defect Analysis
- Declaration of Conformity
- ECR

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project**
   ```bash
   cd invoice_manager
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### Uploading Invoices

1. Click **"Upload Invoice"** button
2. Select an Excel file (.xlsx) containing invoice data
3. Enter the invoice date in YYYY-MM-DD format
4. If the lab name cannot be detected from the filename, you'll be prompted to select one
5. The system will:
   - Parse the TESTING+SERVICES tab
   - Validate each record
   - Add valid records to the main table
   - Add invalid records to the "Abnormal Items" tab

### Excel File Requirements

Your Excel file should have a sheet named **"TESTING+SERVICES"** with these columns:
- Tajan Bidding Tracking Number
- Amazon Test Request #
- Amazon Tracker Number
- ASIN#
- Development Center (SEA, LUX/EU, JP)
- Category (New HCC)
- Product Brand
- Product Description
- Testing SLA (Working days)
- Test / Service Type
- Quotation/Order Number
- Request Date
- Test Start Date
- Report Delivered Date
- Report number
- Test / inspection Location
- Product line
- AMAZON QUALITY MANAGER
- AMAZON SOURCING MANAGER
- Invoice #
- Lab contact
- COMMENT (IF ANY)
- AMOUNT (Currency=USD)

### Managing Data

#### View Data
- Use the **"Valid Invoices"** tab to view all valid invoice records
- Use the **"Abnormal Items"** tab to view records that failed validation
- Use the **"Statistics"** tab to see summary information

#### Filter Data
- Use the filter bar to search by text, lab name, or date range
- Click **"Filter"** to apply filters
- Click **"Clear"** to reset filters

#### Add Records
1. Click **"Add Row"** button
2. Fill in the required fields (marked with *)
3. Click **"Save"**

#### Edit Records
1. Double-click on a row, or select a row and click **"Edit"**
2. Modify the fields as needed
3. Click **"Save"**

#### Delete Records
1. Select one or more rows
2. Click **"Delete Row"** button
3. Confirm the deletion

### Fixing Abnormal Items

1. Go to the **"Abnormal Items"** tab
2. Double-click on an item to edit it
3. Fix the validation errors (e.g., add tracking number, correct test type)
4. Click **"Save"**
5. If valid, the item will be moved to the Valid Invoices table

### Settings

Click **"Settings"** to manage:
- **Lab Names**: Add, edit, or delete lab names for detection
- **Test Types**: Add, edit, or delete allowed test/service types

### Exporting Data

1. Click **"Export"** button
2. Choose a location and filename
3. The data will be exported to an Excel file

## Project Structure

```
invoice_manager/
├── main.py              # Application entry point
├── database.py          # SQLite database operations
├── excel_parser.py      # Excel file parsing
├── validators.py        # Data validation logic
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── ui/
    ├── __init__.py
    ├── main_window.py   # Main application window
    ├── data_table.py    # Table view component
    └── dialogs.py       # Dialog windows
```

## Database

The application uses SQLite for data persistence. The database file (`invoice_manager.db`) is created automatically in the application directory.

### Tables
- **invoices**: Valid invoice records
- **abnormal_invoices**: Records that failed validation
- **lab_names**: Configured lab names
- **test_types**: Allowed test/service types

## Building Executable (Optional)

To create a standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "InvoiceManager" main.py
```

The executable will be in the `dist` folder.

## Troubleshooting

### "Could not find TESTING+SERVICES sheet"
- Ensure your Excel file has a sheet with "TESTING+SERVICES" in its name

### "Could not detect lab name"
- Include the lab name (BV, ITS, TUV, or SGS) in the filename
- Or select the lab manually when prompted

### Records going to Abnormal Items
- Check that Tajan Bidding Tracking Number is filled
- Check that Test/Service Type matches one of the allowed types (case-sensitive)

## License

This project is for internal use only.

## Support

For issues or feature requests, please contact the development team.
