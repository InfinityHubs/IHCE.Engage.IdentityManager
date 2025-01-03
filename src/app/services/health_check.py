import logging
from fastapi import Depends

# Initialize logging
logger = logging.getLogger(__name__)

class HealthCheckService:
    def __init__(self):
        # Initialize any necessary state here
        pass

    async def application_liveness_check(self):
        """Check the liveness of the application."""
        logger.info("Checking liveness of the application")
        return True

    async def application_readiness_check(self):
        """Check the readiness of the application."""
        logger.info("Checking readiness of the application")
        return True

    # Dependency Injection functions
    def liveness(self, liveness_check: bool = Depends(application_liveness_check)):
        """Inject liveness check dependency."""
        return liveness_check

    def readiness(self, readiness_check: bool = Depends(application_readiness_check)):
        """Inject readiness check dependency."""
        return readiness_check

# Initialize the health check service
health_check_service = HealthCheckService()

# Dependency Injection functions
def liveness(liveness_check: bool = Depends(health_check_service.application_liveness_check)):
    return liveness_check

def readiness(readiness_check: bool = Depends(health_check_service.application_readiness_check)):
    return readiness_check
