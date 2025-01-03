from fastapi import APIRouter
from src.config import AppConfigs
from fastapi.responses import RedirectResponse

router = APIRouter()

# Root endpoint for redirecting to Swagger documentation
@router.get("/", tags=["Root"], include_in_schema=False)
async def redirect_to_swagger():
    """
    Redirects the root URL to the Swagger documentation.
    """
    return RedirectResponse(url=AppConfigs.API_DOC_URL)