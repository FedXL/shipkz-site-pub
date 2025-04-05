import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)


async def add_last_string(values: [()], sheet: str):
    """Function to add last string to the google sheet"""
    SAMPLE_SPREADSHEET_ID = '1K5klORD16jCxbR75fg4JfMWGN9YWbqcDCRf_LC8O62o'
    SAMPLE_RANGE_NAME = sheet
    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
    body = {
        "values": values
    }

    result = service.append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(result)


def add_last_strings_to_basket(values: [()], sheet: str):
    SAMPLE_SPREADSHEET_ID = '1K5klORD16jCxbR75fg4JfMWGN9YWbqcDCRf_LC8O62o'
    SAMPLE_RANGE_NAME = sheet
    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
    body = {
        "values": values
    }
    service.append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()


def add_last_string33(values: [()], sheet: str):
    """Function to add last string to the google sheet"""
    SAMPLE_SPREADSHEET_ID = '1K5klORD16jCxbR75fg4JfMWGN9YWbqcDCRf_LC8O62o'
    SAMPLE_RANGE_NAME = sheet
    service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
    body = {
        "values": values
    }

    result = service.append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(result)

if __name__ == '__main__':
    add_last_string33([('1', '2', '3','5')], 'Dashboard')