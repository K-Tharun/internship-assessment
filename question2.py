import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from question1 import get_all_sheet_names, SPREADSHEET_ID, SCOPES
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("sheets", "v4", credentials=creds)

def upload_to_postgres(sheet_name, data, fill_missing_with="None"):
    """
    Uploads a single sheet to PostgreSQL.
    - fill_missing_with='None' → missing values become NULL
    - fill_missing_with=''     → missing values become empty string
    """

    if not data:
        print(f"No data in sheet: {sheet_name}")
        return

    headers = data[0]
    rows = data[1:]

    # Decide what to fill missing values with
    filler = None if fill_missing_with == "None" else ""

    # Normalize rows to match header length
    normalized_rows = []
    for row in rows:
        if len(row) < len(headers):
            # Pad missing columns with filler (e.g., None or "")
            padded_row = row + [filler] * (len(headers) - len(row))
            normalized_rows.append(padded_row)
        elif len(row) > len(headers):
            # Truncate extra columns
            trimmed_row = row[:len(headers)]
            normalized_rows.append(trimmed_row)
        else:
            # Row has correct length
            normalized_rows.append(row)

    df = pd.DataFrame(normalized_rows, columns=headers)

    engine = create_engine("postgresql://postgres:pass123@localhost:5432/sheetsdb")
    table_name = sheet_name.strip().lower().replace(" ", "_").replace("-", "_")

    try:
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)
        print(f"Uploaded '{sheet_name}' to table: {table_name}")
    except SQLAlchemyError as e:
        print(f"Error uploading {sheet_name}:\n{e}")


def main():
    service = get_service()
    sheet_api = service.spreadsheets()
    sheet_names = get_all_sheet_names(service, SPREADSHEET_ID)

    for sheet_name in sheet_names:
        safe = f"'{sheet_name}'" if ' ' in sheet_name else sheet_name
        result = sheet_api.values().get(spreadsheetId=SPREADSHEET_ID, range=safe).execute()
        values = result.get("values", [])
        upload_to_postgres(sheet_name, values)

    print("All sheets uploaded to PostgreSQL.")

if __name__ == "__main__":
    main()
