from langchain_core.tools import tool
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def get_service():
    """Get calendar events for a given date e.g. '2026-05-06'"""
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    service = build("calendar", "v3", credentials=creds)
    return service

@tool
def add_events(amount: str, date: str) -> str: 
    """Add a calendar event for tithe reminder. Input: amount on a date."""
    service = get_service()
    event = {
        'summary': f'Tithe reminder: {amount}',
        'start': {
            'dateTime': f'{date}T09:00:00', 
            'timeZone': 'Asia/Jakarta'
        }
    }
    service.events().insert(calendarId='primary', body=event).execute()
    return "Created tithe reminder event: {amount} on {date}"