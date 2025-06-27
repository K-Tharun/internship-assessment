# Google Sheets data to PostgreSQL

## Overview

This project connects to a Google Spreadsheet using the **Google Sheets API**, reads data from **all sheets/tabs**, and stores each sheet as a separate table in a **PostgreSQL database** using **SQLAlchemy** and **pandas**.

The project is split into two Python scripts:

- `question1.py` → Authenticates and reads all Google Sheets data
- `question2.py` → Normalizes and inserts each sheet into PostgreSQL

---

## Technologies Used

- Python 3.10+
- Google Sheets API
- pandas
- SQLAlchemy
- PostgreSQL (via Docker)
- Docker CLI

---

##  Setup Instructions

### 1.Clone the Repository

```bash
git clone https://github.com/K-Tharun/internship-assessment.git
cd internship-assessment
```

### 2.Set Up Virtual Environment and Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate           # On Windows
# or
source venv/bin/activate        # On macOS/Linux

pip install -r requirements.txt
```

### 3.Start PostgreSQL via Docker

```bash
docker run --name mypg \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=pass123 \
  -e POSTGRES_DB=sheetsdb \
  -p 5432:5432 \
  -d postgres
```

### 4.Add Google Sheets API Credentials

Place your downloaded credentials.json (from Google Cloud Console) into the root folder of this project.

### 5.Run the Scripts

Fetch and print Google Sheets data (Question 1):
```bash
python question1.py
```

Upload sheet data to PostgreSQL (Question 2):
```bash
python question2.py
```

## Outcomes

1. Authenticated with Google Sheets API

    Set up OAuth 2.0 flow using credentials.json

    Generated token.json for reuse

    Enabled spreadsheets.readonly scope

2. Fetched Data from All Google Sheets Tabs

    Automatically detected all sheet/tab names using the Sheets API

    Used dynamic range (like 'Sheet Name') to extract full sheet contents

    Handled tab names with spaces and special characters

3. Normalized Data for Processing

    Ensured every row matched the number of columns from the header

    Handled incomplete or extra-wide rows by:

    Padding with None (to insert as SQL NULL)

    Trimming extra columns

4. Deployed PostgreSQL with Docker

Used Docker CLI to run PostgreSQL container (mypg)

Set up default credentials and database:
user=postgres, password=pass123, db=sheetsdb

5. Stored Each Sheet as a Table in PostgreSQL

Used pandas.DataFrame and SQLAlchemy to:

    Auto-create tables based on headers

    Insert normalized rows

    Convert sheet names to safe table names (e.g., Fairness Tools → fairness_tools)