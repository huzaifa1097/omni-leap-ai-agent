import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_calendar_events() -> str:
    """
    Get upcoming events from the user's primary Google Calendar.
    Returns a formatted string with upcoming events.
    """
    creds = None
    
    # Check if token.json exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # Handle authentication
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open("token.json", "w") as token:
                    token.write(creds.to_json())
            except Exception as e:
                return "❌ Calendar access token expired. Please re-authenticate with Google Calendar."
        else:
            return "❌ Google Calendar not authenticated. Please run the authentication script first."
    
    try:
        # Build the Calendar API service
        service = build("calendar", "v3", credentials=creds)
        
        # Get current time in RFC3339 format
        now = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Fetch upcoming events from the next 30 days
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        
        if not events:
            return "📅 No upcoming events found on your calendar."
        
        # Format the events for display
        event_list = "📅 Here are your upcoming events:\n\n"
        for i, event in enumerate(events, 1):
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No title")
            
            # Format date/time for better readability
            try:
                if "T" in start:  # DateTime format
                    dt = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
                    formatted_time = dt.strftime("%Y-%m-%d at %I:%M %p")
                else:  # Date only format
                    dt = datetime.datetime.fromisoformat(start)
                    formatted_time = dt.strftime("%Y-%m-%d (All day)")
            except:
                formatted_time = start
            
            event_list += f"{i}. **{summary}**\n   📅 {formatted_time}\n\n"
        
        return event_list
        
    except HttpError as error:
        return f"❌ An error occurred with the Google Calendar API: {error}"
    except Exception as e:
        return f"❌ Unexpected error accessing calendar: {str(e)}"