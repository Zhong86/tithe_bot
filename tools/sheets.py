from dotenv import load_dotenv
from langchain_core.tools import tool
import gspread
from google.oauth2.service_account import Credentials
import os

load_dotenv()

def get_sheet():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    gc = gspread.authorize(creds)
    return gc.open_by_key(os.getenv("SHEETS_ID"))

@tool
def log_tithe(amount: str, date: str) -> str:
    """Log a tithe/donation entry. Input: amount, and date."""
    sheet = get_sheet().worksheet("Tithes")
    sheet.append_row([date, amount])
    return f"Logged tithe: Received {amount} on {date}"

@tool
def get_tithes(month: str) -> str:
    """Get all tithe records for a given month e.g. '2026-05'"""
    sheet = get_sheet().worksheet("Tithes")
    records = sheet.get_all_records()
    filtered = [r for r in records if r["Date"].startswith(month)]
    return str(filtered)
