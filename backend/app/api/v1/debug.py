from fastapi import APIRouter, Request, HTTPException
import firebase_admin
from firebase_admin import auth
import traceback
import json

router = APIRouter()

@router.post("/debug-token")
async def debug_token(request: Request):
    """Debug endpoint to test Firebase token verification"""
    try:
        # Get the raw request data
        auth_header = request.headers.get("Authorization")
        print(f"[DEBUG] Auth header received: {auth_header[:50] if auth_header else 'None'}...")
        
        if not auth_header:
            return {"error": "No Authorization header", "headers": dict(request.headers)}
        
        if not auth_header.startswith("Bearer "):
            return {"error": "Invalid Authorization header format", "header": auth_header[:50]}
        
        token = auth_header.split("Bearer ")[1]
        print(f"[DEBUG] Extracted token length: {len(token)}")
        print(f"[DEBUG] Token first 50 chars: {token[:50]}...")
        
        # Check if Firebase is initialized
        if not firebase_admin._apps:
            return {"error": "Firebase Admin SDK not initialized"}
        
        print(f"[DEBUG] Firebase apps: {list(firebase_admin._apps.keys())}")
        
        # Try to verify the token
        print("[DEBUG] Attempting to verify token...")
        decoded_token = auth.verify_id_token(token)
        print(f"[DEBUG] Token verified successfully!")
        
        return {
            "success": True,
            "uid": decoded_token.get('uid'),
            "email": decoded_token.get('email'),
            "exp": decoded_token.get('exp'),
            "iat": decoded_token.get('iat'),
            "aud": decoded_token.get('aud'),  # Should be omni-client-21d02
            "iss": decoded_token.get('iss'),  # Should be https://securetoken.google.com/omni-client-21d02
            "token_length": len(token)
        }
        
    except firebase_admin.auth.ExpiredIdTokenError as e:
        error_msg = f"Token expired: {str(e)}"
        print(f"[DEBUG] {error_msg}")
        return {"success": False, "error": error_msg, "error_type": "ExpiredIdTokenError"}
        
    except firebase_admin.auth.InvalidIdTokenError as e:
        error_msg = f"Invalid token: {str(e)}"
        print(f"[DEBUG] {error_msg}")
        return {"success": False, "error": error_msg, "error_type": "InvalidIdTokenError"}
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        traceback_str = traceback.format_exc()
        print(f"[DEBUG] {error_msg}")
        print(f"[DEBUG] Traceback: {traceback_str}")
        return {
            "success": False, 
            "error": error_msg, 
            "error_type": str(type(e)),
            "traceback": traceback_str
        }

@router.get("/debug-firebase")
async def debug_firebase():
    """Debug endpoint to check Firebase initialization"""
    try:
        # Check Firebase initialization
        apps = list(firebase_admin._apps.keys())
        
        if not apps:
            return {"error": "No Firebase apps initialized"}
        
        # Get the default app
        app = firebase_admin.get_app()
        
        return {
            "success": True,
            "firebase_apps": apps,
            "project_id": app.project_id if hasattr(app, 'project_id') else "Unknown",
            "credentials_type": str(type(app.credential))
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }