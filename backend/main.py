from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.api.v1 import chat
from app.api.v1 import debug
import os
from contextlib import asynccontextmanager
import firebase_admin
from firebase_admin import credentials
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.services.secrets_service import load_secrets_from_gcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    load_secrets_from_gcp()
    try:
        cred = credentials.Certificate("firebase-service-account.json")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully within lifespan event.")
    except Exception as e:
        print(f"CRITICAL ERROR during startup: Could not initialize Firebase Admin SDK: {e}")
    yield
    print("Application shutdown...")


app = FastAPI(
    title="OmniLeap API",
    description="The brain of the OmniLeap Unified Intelligence Agent.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter

# CORS-aware 429 handler — must add CORS headers manually because exception
# handler responses bypass the CORS middleware.
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    origin = request.headers.get("origin", "")
    headers = {"Retry-After": str(exc.retry_after)} if hasattr(exc, "retry_after") else {}
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
        headers=headers,
    )

static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Explicit origin list — wildcard + credentials is rejected by browsers.
# Add new frontend URLs here or set ALLOWED_ORIGINS env var (comma-separated).
_env_origins = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = (
    [o.strip() for o in _env_origins.split(",") if o.strip()]
    if _env_origins
    else [
        "https://omni-leap-ai-agent.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(debug.router, prefix="/debug", tags=["Debug"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the OmniLeap API."}
