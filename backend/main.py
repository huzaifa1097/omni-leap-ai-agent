from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1 import chat
from app.api.v1 import debug
import os
from contextlib import asynccontextmanager
import firebase_admin
from firebase_admin import credentials

# --- THIS IS THE FIX ---
# Import our new secrets service
from app.services.secrets_service import load_secrets_from_gcp

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs ONCE when the server starts up.
    print("Application startup...")
    
    # --- THIS IS THE FIX ---
    # Load secrets from Google Secret Manager if running in the cloud.
    # This will populate the environment variables and create the service account file.
    load_secrets_from_gcp()
    
    try:
        # The Firebase SDK will now find the file created by the secrets service
        # or the local file if running locally.
        cred = credentials.Certificate("firebase-service-account.json")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully within lifespan event.")
    except Exception as e:
        print(f"CRITICAL ERROR during startup: Could not initialize Firebase Admin SDK: {e}")
    
    yield
    # Code here would run on shutdown.
    print("Application shutdown...")

app = FastAPI(
    title="OmniLeap API",
    description="The brain of the OmniLeap Unified Intelligence Agent.",
    version="1.0.0",
    lifespan=lifespan
)

# Create a directory for static files if it doesn't exist
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Mount the static directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(debug.router, prefix="/debug", tags=["Debug"]) 
@app.get("/")
def read_root():
    return {"message": "Welcome to the OmniLeap API."}
