"""
KisanDirect - FastAPI Application Entry Point
================================================
Wires together auth, farmer/buyer/marketplace, AI matching, price
intelligence, demand forecasting, logistics, and admin analytics routers.

Run (after installing requirements.txt and setting up PostgreSQL):
    uvicorn app.main:app --reload --port 8000

Swagger UI: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.db import Base, engine
from app.api import auth, farmers, crop_listings, offers, orders, prices, demand, ai_match, logistics, admin

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered digital agricultural marketplace connecting farmers directly "
        "with buyers, reducing unnecessary intermediary layers while keeping "
        "essential supply-chain services (transport, storage, aggregation) "
        "transparent and efficient. Built for SIH 2026 — PS 33 (SIH26033)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-create tables on startup for local/dev convenience.
# In production, use Alembic migrations instead of create_all().
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(farmers.router)
app.include_router(crop_listings.router)
app.include_router(offers.router)
app.include_router(orders.router)
app.include_router(prices.router)
app.include_router(demand.router)
app.include_router(ai_match.router)
app.include_router(logistics.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "KisanDirect API",
        "status": "running",
        "docs": "/docs",
        "modules": ["marketplace", "price-intelligence", "demand-forecasting", "logistics"],
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
