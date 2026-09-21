from fastapi import APIRouter

from app.api import companies, datasets, experiments, factors, health, portfolios, regimes

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(factors.router, prefix="/factors", tags=["factors"])
api_router.include_router(regimes.router, prefix="/regimes", tags=["regimes"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
