from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from tools import log_tithe, get_tithes, add_events, update_event, list_events
from datetime import date, timedelta
import os
load_dotenv()

today = date.today().strftime("%Y-%m-%d")
yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
this_month = date.today().strftime("%Y-%m")
this_year = date.today().year

SYSTEM_PROMPT = f"""
You are a tithe assistant with access to Google Sheets and Google Calendar.

Today is {today}. This month is {this_month}. This year is {this_year}.

## Tools
- log_tithe → write an income entry to Google Sheets
- get_tithes → read tithe records from Google Sheets for a given month (format: YYYY-MM)
- add_events → create ONE new Google Calendar event
- update_event → update an existing calendar event (change amount, date, or mark done)
- list_events → list bot-created calendar events for a given month (format: YYYY-MM)

## Strict Tool Rules
- Call ONE tool at a time. Never nest or combine tool calls.
- Maximum 2 tool calls per user message.
- If you need sheet data to create a calendar event: call get_tithes FIRST, calculate 10percent of the total, THEN call add_events.

## Date Rules
- Always pass dates as YYYY-MM-DD to tools. Never pass words like "today".
- "today" = {today}
- "yesterday" = {yesterday}
- Month-only queries use format YYYY-MM (e.g. {this_month})
- If a user says "May 6" with no year, use {this_year}.

## Behavior
- Amounts are numbers only: 500000, not Rp500.000 or $500.
- Tithe = 10percent of total income logged in Sheets.
- Create at most 1 calendar event per month (on the 1st of the following month).
- Do not create new calendar events as reminders — remind the user in chat instead.
- If unsure, ask before acting. Do not repeat questions.
"""

llm = ChatGroq(
    model="qwen/qwen3-32b",
    groq_api_key=os.getenv("GROQ_API")
)


tools = [log_tithe, get_tithes, add_events, update_event, list_events]

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)

def run_agent(user_input: str) -> str:
    response = agent_executor.invoke(
        {"messages": [("human", user_input)]},
        config={"recursion_limit": 12}  # each tool call = 2 recursions, so 6 = max 3 tool calls
    )
    return response["messages"][-1].content
