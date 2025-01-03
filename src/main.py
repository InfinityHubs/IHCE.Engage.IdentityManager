import logging
from fastapi import FastAPI
from src.config import AppConfigs
from contextlib import asynccontextmanager
from src.app.routes import startup, health_check, api_routes
from src.app.utils import Redis
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to initialize the FastAPI application with configuration
def application() -> FastAPI:
    """
    Initializes the FastAPI application with the configuration from AppConfigs.

    Returns:
        FastAPI: An instance of the FastAPI application.
    """
    return FastAPI(
        title=AppConfigs.PIPELINE,
        docs_url=AppConfigs.API_DOC_URL,
        version=AppConfigs.PROJECT_VERSION,
        description=AppConfigs.PROJECT_DESCRIPTION,
    )


# Function to include all routers into the FastAPI app
def include_application_routers(_app: FastAPI):
    """
    Includes all application routers into the FastAPI app.

    Args:
        _app (FastAPI): The FastAPI application instance.
    """
    # Include routers with their respective prefixes
    _app.include_router(startup.router, include_in_schema=False)
    _app.include_router(health_check.router, include_in_schema=False)
    _app.include_router(api_routes, include_in_schema=True, prefix=AppConfigs.API_PREFIX)


# Context manager to manage the lifespan of the FastAPI application
@asynccontextmanager
async def lifespan_manager(_app: FastAPI):
    """
    Manages the lifespan of the FastAPI application. This includes startup
    and shutdown logic for the application.

    Args:
        _app (FastAPI): The FastAPI application instance.
    """
    # Startup logic
    logger.info(f"Application {AppConfigs.APP_IDENTIFIER} is starting.")
    _app.state.startup_message = f"[{AppConfigs.NAMESPACE}:{AppConfigs.PIPELINE}] is starting..."

    yield

    # Shutdown logic
    _app.state.shutdown_message = f"[{AppConfigs.NAMESPACE}:{AppConfigs.PIPELINE}] is shutting down..."
    logger.info("Application shutting down...")


# Function to create and configure the FastAPI application with Redis and routers
def create_application() -> FastAPI:
    """
    Creates and configures the FastAPI application, including the routers and
    external service connections (like Redis).

    Returns:
        FastAPI: The fully configured FastAPI application.
    """
    builder = application()

    # Initialize Redis client connection
    Redis.RedisClient.connect()

    # Include routers for the application
    include_application_routers(builder)

    return builder


# Create the FastAPI application instance
app = create_application()


# Exception handler to manage validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Custom exception handler for RequestValidationError to format validation errors.

    Args:
        request: The request object that caused the exception.
        exc: The exception that was raised.

    Returns:
        JSONResponse: A formatted response with validation errors.
    """
    return JSONResponse(
        status_code=422,
        content={
            "errors": exc.errors(),
            "body": exc.body
        },
    )
