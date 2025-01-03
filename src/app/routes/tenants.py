from typing import List, Optional
from uuid import UUID
from src.app.utils import Db
from fastapi import APIRouter, Query, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from src.app.services.prospectus import ProspectusService
from src.app.schema.Prospectus import OnboardingNewProspectus, IdentityActivationResponse, OnboardingNewProspectusResponse

# Initialize the router for Tenant-related APIs
router = APIRouter(tags=["Tenant-Prospectus"], prefix="/tenant-prospectus")

# Tenants routes
# Route: Create a new tenant prospectus
@router.post("", status_code=status.HTTP_201_CREATED, response_model=OnboardingNewProspectusResponse)
async def create_tenant_prospectus(
        prospectus: OnboardingNewProspectus,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(Db.session)
):
    """
    Endpoint to onboard a new tenant prospectus.
    """
    return await ProspectusService(db_session).onboarding_new_prospectus(background_tasks, prospectus)

# Route: Retrieve a paginated list of tenant prospectus
@router.get("", status_code=status.HTTP_200_OK, response_model=List[OnboardingNewProspectusResponse])
async def list_all_tenants(
        page: int = Query(1, ge=1, description="Page number for pagination"),
        limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
        db_session: Session = Depends(Db.session)
):
    """
    Retrieve a paginated list of tenant prospectus with optional filters.

    ## Description
    - This endpoint fetches and returns a list of tenants.
    - It retrieves the details of all tenants currently onboarded in the system. If no tenants exist, the response will be an empty list (`[]`).

    ### Empty Response Example
    - If no tenants are found/exists:
      ```json
      []
      ```

    ## Behavior
    - **No Data Available**: Returns an empty JSON array (`[]`).
    - **Successful Retrieval**: Returns a JSON array of OnboardingNewTenantResponse objects `List[OnboardingNewTenantResponse]`.
    - **Access Control**: This endpoint is accessible only to authorized users (dependencies for authentication can be added).

    ## Returns
    - `List[OnboardingNewTenantResponse]`: Paginated list of tenant data.
    """
    return await ProspectusService(db_session).list_prospectus(page, limit)

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Optional[OnboardingNewProspectusResponse])
async def get_tenant_by_id(
        id: UUID,
        db_session: Session = Depends(Db.session)
):
    """
    Retrieve a single tenant prospectus by ID.

    ## Description
    - This endpoint fetches and returns the details of a single tenant prospectus using its unique identifier (UUID).
    - If the tenant does not exist, the response will return `null`.

    ### Empty Response Example
    - If the tenant with the given ID does not exist:
      ```json
      null
      ```

    ## Behavior
    - **No Data Available**: Returns `null` if no tenant is found.
    - **Successful Retrieval**: Returns the details of the requested tenant prospectus.
    - **Access Control**: This endpoint is accessible only to authorized users (dependencies for authentication can be added).

    ## Returns
    - `Optional[OnboardingNewProspectusResponse]`: Details of the requested tenant prospectus, or `null` if not found.
    """
    return await ProspectusService(db_session).get_prospectus(id)

# Route: Promote tenant prospectus status
@router.put("/{id}/promote-status", status_code=status.HTTP_200_OK, response_model=OnboardingNewProspectusResponse)
async def promote_tenant_prospectus(
        id: UUID,
        db_session: Session = Depends(Db.session)
):
    return await ProspectusService(db_session).promote_tenant_prospectus(id)

@router.get("/{id}/identity-activation", status_code=status.HTTP_200_OK, response_model=IdentityActivationResponse)
async def identity_activation(
        id: UUID,
        db_session: Session = Depends(Db.session)
):
    return await ProspectusService(db_session).identity_activation(id)

@router.get("/{id}/identity-verification/{key}", status_code=status.HTTP_200_OK, response_model=str)
async def identity_verification(
        id: UUID,
        key: str,
        db_session: Session = Depends(Db.session)
):
    return await ProspectusService(db_session).identity_verification(id, key)


