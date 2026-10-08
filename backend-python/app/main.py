"""
FastAPI URL Shortener Microservice
Provides REST APIs for:
  - Short URL Generation with Custom Slug support
  - 302 Temporary Redirection with asynchronous analytics tracking
  - Click metrics & analytics reporting
  - Health checks & system info
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from contextlib import asynccontextmanager

from app.encoder import generate_random_slug
from app.storage import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await store.init()
    yield
    # Shutdown


app = FastAPI(
    title="TinyURL Core Microservice",
    description="High-performance URL Shortener service with Base62 encoding and Redis caching",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request & Response Models ---
class ShortenRequest(BaseModel):
    url: HttpUrl = Field(..., description="The original long destination URL")
    custom_alias: Optional[str] = Field(None, min_length=3, max_length=30, description="Optional custom slug")
    ttl_days: Optional[int] = Field(730, description="TTL in days (default: 2 years)")


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: str
    custom_alias: bool


# --- API Routes ---

@app.get("/api/v1/health")
async def health_check():
    """Liveness and readiness probe for Kubernetes / Docker."""
    return {
        "status": "healthy",
        "service": "url-shortener-python",
        "redis_connected": store.redis_client is not None,
    }


@app.post("/api/v1/shorten", response_model=ShortenResponse, status_code=201)
async def shorten_url(payload: ShortenRequest, request: Request):
    """
    Creates a new short URL.
    - If custom_alias is provided, verifies uniqueness.
    - Otherwise generates a random Base62 7-character slug.
    """
    original_url_str = str(payload.url)

    if payload.custom_alias:
        slug = payload.custom_alias.strip()
        # Check collision
        existing = await store.get(slug)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Custom slug '{slug}' is already taken. Please choose another."
            )
        is_custom = True
    else:
        # Generate unique 7-char Base62 slug with collision retry loop
        is_custom = False
        for _ in range(5):
            slug = generate_random_slug(7)
            if not await store.get(slug):
                break
        else:
            raise HTTPException(status_code=500, detail="Failed to generate unique slug. Try again.")

    record = await store.save(
        short_code=slug,
        original_url=original_url_str,
        custom_alias=is_custom,
    )

    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{slug}"

    return ShortenResponse(
        short_code=slug,
        short_url=short_url,
        original_url=original_url_str,
        created_at=record["created_at"],
        custom_alias=is_custom,
    )


@app.get("/api/v1/analytics/{short_code}")
async def get_analytics(short_code: str):
    """Retrieves access statistics and click history for a short code."""
    data = await store.get_analytics(short_code)
    if not data:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return data


@app.get("/api/v1/recent")
async def get_recent_links():
    """Lists the most recently shortened links for the dashboard."""
    return await store.list_recent(limit=20)


@app.get("/{short_code}", response_class=RedirectResponse)
async def redirect_to_original(short_code: str, request: Request, background_tasks: BackgroundTasks):
    """
    Resolves short code and returns HTTP 302 Found redirect.
    Executes click metric collection in the background to ensure sub-10ms response times.
    """
    # Exclude internal paths or favicon
    if short_code in ("favicon.ico", "docs", "openapi.json", "api"):
        raise HTTPException(status_code=404, detail="Not found")

    record = await store.get(short_code)
    if not record:
        raise HTTPException(status_code=404, detail="Short link has expired or does not exist")

    # Fire-and-forget background analytics task
    referrer = request.headers.get("referer")
    user_agent = request.headers.get("user-agent")
    client_ip = request.client.host if request.client else "127.0.0.1"

    background_tasks.add_task(
        store.record_click,
        short_code=short_code,
        referrer=referrer,
        user_agent=user_agent,
        ip=client_ip,
    )

    # Return 302 Found so browser doesn't permanently cache, enabling accurate click analytics
    return RedirectResponse(url=record["original_url"], status_code=302)
