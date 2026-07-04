# School Parent Dashboard Flask Application

A Flask web application that allows parents to access their child's academic and disciplinary records.

## Features

- **MDB File Access**: Connects to Microsoft Access database files (.mdb/.accdb) to retrieve student data
- **Parent Registration (OTP)**: Parents register with cellphone number → OTP via **WhatsApp** (primary) or **SMS** (fallback) → set password
- **Multi-Child Support**: Parents with multiple learners can switch learners from the dashboard
- **Password Protection**: Secure password-based authentication (hashed)
- **Academic Dashboard**: View academic performance with:
  - Interactive charts and graphs
  - Drilldown capabilities to view detailed subject information
  - Tabular data display
- **Disciplinary Dashboard**: View disciplinary records and incidents

## Prerequisites

- Python 3.7 or higher
- Microsoft Access Database Engine (for MDB file access)
  - Download from: https://www.microsoft.com/en-us/download/details.aspx?id=54920
- An MDB/ACCDB database file with the following tables (adjust table/column names in code as needed):
  - `Academics` - Academic records
  - `Disciplinary` - Disciplinary records
  - `SubjectDetails` - Detailed subject assessment data

## Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Microsoft Access Database Engine:
   - Download and install the Microsoft Access Database Engine 2016 Redistributable
   - This is required for pyodbc to connect to MDB files

4. Configure environment variables (Windows PowerShell):

```powershell
# Required for Access DB connection (example values)
$env:MDB_FILE_PATH = "C:\path\to\your\database.mdb"
$env:MDB_PASSWORD = "your_mdb_password"

# Admin login (recommended to set)
$env:ADMIN_USERNAME = "admin"
$env:ADMIN_PASSWORD = "set_a_strong_password"

# SMSPortal (REST API key) for OTP sending
$env:SMSPORTAL_CLIENT_ID = "your_client_id"
$env:SMSPORTAL_API_SECRET = "your_api_secret"

# Optional
$env:SMSPORTAL_SENDER_ID = "KISMET"   # max 11 chars (provider rules apply)
$env:SMSPORTAL_TEST_MODE = "false"    # set "true" to test without delivering SMS

# WhatsApp (primary OTP channel; falls back to SMS if unavailable or delivery fails)
$env:WHATSAPP_SERVICE_URL = "http://127.0.0.1:3001"   # default; set if service runs elsewhere
```

5. **(Optional) Start the WhatsApp service** (for OTP via WhatsApp with SMS fallback):
   - Install Node.js 18+, then in the project folder:
   ```bash
   cd whatsapp-service
   npm install
   npm start
   ```
   - Log in as admin → **Admin** → **WhatsApp**, and scan the QR code with WhatsApp on your phone.
   - OTPs will be sent via WhatsApp first; if the message is not delivered or the service is down, SMS (SMSPortal) is used automatically.

6. Configure the MDB file path (alternative options):
   - Set the `MDB_FILE_PATH` environment variable, or
   - Place your MDB file as `database.mdb` in the project root, or
   - Update the path in `app.py` line 15

## Database Schema Requirements

Your MDB database should have tables with the following structure (column names can be adjusted in the code):

### Academics Table
- `LearnerID` - Student identifier
- `Year` - Academic year
- `Term` - Term/Semester
- `Subject` - Subject name
- `Grade` - Grade/Letter grade
- `Percentage` - Percentage score

### Disciplinary Table
- `LearnerID` - Student identifier
- `Date` - Incident date
- `IncidentType` - Type of incident
- `Description` - Incident description
- `Severity` - Severity level (High/Medium/Low)
- `Status` - Current status

### SubjectDetails Table
- `LearnerID` - Student identifier
- `Subject` - Subject name
- `Year` - Academic year
- `Term` - Term/Semester
- `AssessmentDate` - Date of assessment
- `AssessmentType` - Type of assessment
- `Score` - Assessment score
- `Grade` - Grade received

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Parent registration (OTP):
   - Navigate to `http://localhost:5000/register`
   - Enter cellphone number
   - Enter OTP received via SMS
   - Create a password
   - Login at `http://localhost:5000/login`

## Customization

### Adjusting Table/Column Names

If your MDB database uses different table or column names, update the SQL queries in `app.py`:

- Line 185-188: Disciplinary query
- Line 203-206: Academics query
- Line 224-227: Subject details query

### Changing MDB File Path

Set the environment variable:
```bash
export MDB_FILE_PATH=/path/to/your/database.mdb
```

Or update line 15 in `app.py`:
```python
app.config['MDB_FILE_PATH'] = 'path/to/your/database.mdb'
```

## Security Notes

- Passwords are hashed using Werkzeug's secure password hashing
- OTPs expire after 10 minutes and have limited verification attempts
- Parents can only access learners linked to their account

## Troubleshooting

### MDB Connection Issues

If you get connection errors:
1. Ensure Microsoft Access Database Engine is installed
2. Verify the MDB file path is correct
3. Check that the MDB file is not password-protected (or update connection string)
4. Ensure the MDB file is not open in another application

### Table/Column Not Found

If queries return empty results:
1. Verify table names match your MDB database
2. Check column names match exactly (case-sensitive)
3. Verify LearnerID values match between User table and MDB tables

## License

This project is provided as-is for educational and school administration purposes.
