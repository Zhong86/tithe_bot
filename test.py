from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
import gspread
import os
load_dotenv()

def test_sheets():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"  # ← add this
        ]
    )
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(os.getenv("SHEETS_ID"))
    
    # Try reading
    worksheet = sheet.sheet1
    print("✅ Connected to sheet:", sheet.title)
    print("📄 First row:", worksheet.row_values(1))
    
    # Try writing
    worksheet.append_row(["TEST", "100", "2026-05-06"])
    print("✅ Write successful — check your sheet!")

test_sheets()


from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def test_calendar():
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )
    service = build("calendar", "v3", credentials=creds)
    
    # List calendars accessible to the service account
    calendars = service.calendarList().list().execute()
    print("✅ Connected to Calendar!")
    for cal in calendars.get("items", []):
        print("📅 Calendar found:", cal["summary"])
test_calendar()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

def test_groq():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API")
    )
    response = llm.invoke([HumanMessage(content="Say hello!")])
    print("✅ Groq working:", response.content)

test_groq()