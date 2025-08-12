"""
Quick authentication script to generate token.json
Run this once: python authenticate_calendar.py
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def authenticate():
    """Generate token.json from your existing credentials.json"""
    
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found in current directory")
        return False
        
    if os.path.exists("token.json"):
        print("✅ token.json already exists!")
        return True
    
    try:
        print("🔧 Starting authentication process...")
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        
        print("✅ Successfully created token.json!")
        print("🎉 Your calendar tool is now ready to use!")
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    authenticate()