import firebase_admin
from firebase_admin import firestore, auth
import datetime

# --- THIS IS THE FIX ---
# We no longer call firestore.client() at the top level.
# Instead, we will get the client instance inside each function when it's needed.

def get_db_client():
    """Helper function to get the Firestore client, ensuring the app is initialized."""
    if not firebase_admin._apps:
        # This is a fallback for safety, but the lifespan event in main.py should handle initialization.
        from firebase_admin import credentials
        print("Firebase app not initialized. Attempting fallback initialization...")
        try:
            cred = credentials.Certificate("firebase-service-account.json")
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"CRITICAL: Fallback Firebase initialization failed: {e}")
            raise e
    return firestore.client()

def save_message_to_firestore(user_id: str, session_id: str, sender: str, text: str):
    """Saves a single message to a user's conversation history in Firestore."""
    try:
        db = get_db_client()
        messages_ref = db.collection('conversations').document(user_id).collection('messages')
        messages_ref.add({
            'session_id': session_id,
            'sender': sender,
            'text': text,
            'timestamp': datetime.datetime.utcnow()
        })
    except Exception as e:
        print(f"Error saving message to Firestore for user {user_id}: {e}")

def get_conversations_from_firestore(user_id: str):
    """Retrieves all messages for a specific user, ordered by timestamp."""
    try:
        db = get_db_client()
        messages_ref = db.collection('conversations').document(user_id).collection('messages')
        query = messages_ref.order_by('timestamp', direction=firestore.Query.ASCENDING)
        docs = query.stream()
        messages = []
        for doc in docs:
            message_data = doc.to_dict()
            message_data['timestamp'] = message_data['timestamp'].isoformat()
            messages.append(message_data)
        return messages
    except Exception as e:
        print(f"Error fetching conversations for user {user_id}: {e}")
        return None

def delete_conversation_from_firestore(user_id: str):
    """Deletes all messages in the 'messages' subcollection for a given user."""
    try:
        db = get_db_client()
        messages_ref = db.collection('conversations').document(user_id).collection('messages')
        docs = messages_ref.stream()
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
        batch.commit()
        return True
    except Exception as e:
        print(f"Error deleting conversation for user {user_id}: {e}")
        return False

def delete_single_session_from_firestore(user_id: str, session_id: str):
    """Deletes all messages for a specific session_id for a given user."""
    try:
        db = get_db_client()
        messages_ref = db.collection('conversations').document(user_id).collection('messages')
        docs = messages_ref.where('session_id', '==', session_id).stream()
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
        batch.commit()
        return True
    except Exception as e:
        print(f"Error deleting session {session_id} for user {user_id}: {e}")
        return False

def verify_firebase_token(id_token: str) -> dict:
    """Verifies the Firebase ID token from the frontend and returns the user's data."""
    try:
        # The auth module doesn't need the client, it uses the default initialized app
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return None
