import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1_6MvPp3X2oI5DR4Isbk8qYPLDEy6dDVYffdLtDeZF4Q"

def get_all_sheet_names(service, spreadsheet_id):
    """Returns a list of all sheet names (tabs) in the Google Sheet."""
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get("sheets", [])
    return [sheet["properties"]["title"] for sheet in sheets]

def main():
    creds = None

    # Authentication
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

    try:
        # Connect to Google Sheets API
        service = build("sheets", "v4", credentials=creds)
        sheet_api = service.spreadsheets()

        # Get all sheet names
        sheet_names = get_all_sheet_names(service, SPREADSHEET_ID)

        # Loop through each sheet and read data from A1:
        for sheet_name in sheet_names:
            print(f"\n Sheet: {sheet_name}")

            # We wrap sheet name in single quotes if it contains spaces
            safe_sheet_name = f"'{sheet_name}'" if " " in sheet_name else sheet_name
            range_name = f"{safe_sheet_name}"

            result = sheet_api.values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
            values = result.get("values", [])

            if not values:
                print("  No data found.")
            else:
                for row in values:
                    print("  ", row)

    except HttpError as err:
        print(f"Google API Error:\n{err}")

if __name__ == "__main__":
    main()
