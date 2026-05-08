from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from langchain_core.tools import tool
import pickle
import json
import os

EVENT_STORE = "event_store.json"

def load_events():
    if not os.path.exists(EVENT_STORE):
        return {}
    with open(EVENT_STORE, 'r') as f:
        return json.load(f)

def save_events(events):
    with open(EVENT_STORE, 'w') as f:
        json.dump(events, f, indent=2)

def get_service():
    with open('token.pickle', 'rb') as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("calendar", "v3", credentials=creds)

@tool
def add_events(amount: str, date: str) -> str: 
    """Add a Google Calendar reminder event for a tithe. amount is a number string like '500'. date is in YYYY-MM-DD format like '2026-05-07'"""
    import re
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        return f"Error: date must be in YYYY-MM-DD format, got: '{date}'"
    
    service = get_service()
    event = {
        'summary': f'Tithe reminder: {amount}',
        'start': {
            'dateTime': f'{date}T09:00:00', 
            'timeZone': 'Asia/Jakarta'
        }, 
        'end': {                                   
            'dateTime': f'{date}T09:30:00',
            'timeZone': 'Asia/Jakarta'
        }
    }
    result = service.events().insert(calendarId='primary', body=event).execute()

    events = load_events()
    events[date] = {
        'event_id': result['id'],
        'amount': amount,
        'summary': result['summary']
    }
    save_events(events)

    return f"Created tithe reminder event: {amount} on {date} — {result.get('htmlLink')}" 

@tool
def update_event(date: str, new_amount: str = None, new_date: str = None, mark_done: bool = False) -> str:
    """Update an existing tithe calendar event. Find event by its original date in YYYY-MM-DD format.
    Optionally update the amount, reschedule to a new_date, or mark it as done."""
    events = load_events()
    
    if date not in events:
        return f"No event found for {date}. Available dates: {list(events.keys())}"
    
    service = get_service()
    event_id = events[date]['event_id']
    
    # Fetch current event from Google
    current = service.events().get(calendarId='primary', eventId=event_id).execute()
    
    # Apply updates
    if mark_done:
        current['summary'] = current['summary'] + ' ✅'
        current['colorId'] = '2'  # green
    
    if new_amount:
        current['summary'] = f'Tithe reminder: {new_amount} ✅' if mark_done else f'Tithe reminder: {new_amount}'
        events[date]['amount'] = new_amount

    if new_date:
        current['start'] = {'dateTime': f'{new_date}T09:00:00', 'timeZone': 'Asia/Jakarta'}
        current['end'] = {'dateTime': f'{new_date}T09:30:00', 'timeZone': 'Asia/Jakarta'}
        # Re-key the store entry under new date
        events[new_date] = events.pop(date)

    result = service.events().update(
        calendarId='primary',
        eventId=event_id,
        body=current
    ).execute()
    
    save_events(events)
    return f"Updated event: {result['summary']} on {result['start'].get('dateTime', '')} — {result.get('htmlLink')}"

@tool
def list_events(month: str) -> str:
    """List all tithe calendar events the bot has created for a given month in YYYY-MM format."""
    events = load_events()
    filtered = {k: v for k, v in events.items() if k.startswith(month)}
    if not filtered:
        return f"No events found for {month}."
    result = []
    for date, info in filtered.items():
        result.append(f"- {date}: {info['summary']} (amount: {info['amount']}, id: {info['event_id']})")
    return "\n".join(result)