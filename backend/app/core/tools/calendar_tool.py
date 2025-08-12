from langchain.tools import tool
from app.services.calendar_service import get_calendar_events

@tool
def calendar_tool(query: str) -> str:
    """
    Use this tool to check for upcoming events on the user's Google Calendar.
    This tool takes a dummy query as input, which is not used.
    For example: 'what is on my calendar?'
    """
    # The 'query' argument is ignored, but it is required to prevent a bug.
    return get_calendar_events()