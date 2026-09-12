from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title="NGX Multi-Factor Research API", version="0.1.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_url], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root() -> dict[str, str]:
    return {"service": "ngx-research-api", "docs": "/docs"}