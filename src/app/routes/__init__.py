from fastapi import APIRouter
from src.app.routes import tenants

api_routes = APIRouter()

api_routes.include_router(tenants.router, prefix='/v1')

__all__ = ["api_routes"]