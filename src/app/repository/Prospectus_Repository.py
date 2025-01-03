from typing import List, Type, Optional
from sqlalchemy.orm import Session
from src.app.schema.Prospectus import OnboardingNewProspectus, OnboardingNewProspectusResponse
from src.app.model.Prospectus import Prospectus, ProspectusStages
from sqlalchemy import or_
from uuid import UUID
import logging

# Initialize logging
logger = logging.getLogger(__name__)

class ProspectusRepository:
    def __init__(self, db_session: Session):
        """
        Initializes the repository with a database session.

        Args:
            db_session (Session): SQLAlchemy database session.
        """
        self.db_session = db_session

    async def create_prospectus(self, payload: OnboardingNewProspectus) -> Prospectus:
        try:
            # Construct the new prospectus object
            prospectus = Prospectus()
            prospectus.title = payload.title
            prospectus.slug = payload.slug
            prospectus.subscription = payload.subscription
            prospectus.requester_first_name = payload.requester_first_name
            prospectus.requester_last_name = payload.requester_last_name
            prospectus.requester_email = payload.requester_email
            prospectus.requester_phone_number = payload.requester_phone_number
            prospectus.requester_designation = payload.requester_designation
            prospectus.status = ProspectusStages.INIT_TENANT_PROSPECTUS_ONBOARDING.value
            prospectus.requester_phone_number_country_code = payload.requester_phone_number_country_code

            # Log the tenant creation attempt
            logger.info(f"Attempting to create a new prospectus with title '{prospectus.title}'.")

            # Add the tenant to the session and commit the transaction
            self.db_session.add(prospectus)
            self.db_session.commit()

            # Refresh the prospectus instance to populate generated fields (e.g., id)
            self.db_session.refresh(prospectus)

            # Log successful tenant creation
            logger.info(f"Prospectus '{prospectus.title}' successfully created with ID {prospectus.id}.")

            return prospectus

        except Exception as e:
            # Log unexpected errors
            logger.error(f"An unexpected error occurred while creating a tenant: {str(e)}")
            raise

    async def get_prospectus(self, page: int, limit: int) -> list[Type[Prospectus]]:
        """
        Retrieve a paginated list of prospectus.

        Args:
            page (int): Offset for pagination.
            limit (int): Maximum number of items to fetch.

        Returns:
            List[OnboardingNewProspectusResponse]: List of prospectus data.
        """
        prospectus = (
            self.db_session.query(Prospectus)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return prospectus

    async def get_prospectus_by_id(self, id: UUID) -> Optional[Prospectus]:
        """
        Retrieve a single prospectus by its UUID.

        Args:
            id (UUID): The UUID of the prospectus to retrieve.

        Returns:
            Optional[Prospectus]: The prospectus data if found, or None if not found.
        """
        prospectus = self.db_session.query(Prospectus).filter(Prospectus.id == id).first()
        return prospectus

    async def promote_prospectus_status(self,id: UUID, status: str) -> Prospectus:
        try:
            prospectus = self.db_session.query(Prospectus).filter(Prospectus.id == id).first()
            prospectus.status = status

            # Log the tenant creation attempt
            logger.info(f"Attempting to promote the prospectus status: '{status}'.")

            # Add the tenant to the session and commit the transaction
            self.db_session.commit()

            # Refresh the prospectus instance to populate generated fields (e.g., id)
            self.db_session.refresh(prospectus)

            print(f"{prospectus}")

            # Log successful tenant creation
            logger.info(f"Prospectus '{prospectus.title}' successfully updated with status {prospectus.status}.")

            return prospectus

        except Exception as e:
            # Log unexpected errors
            logger.error(f"An unexpected error occurred while promoting prospectus status: {str(e)}")
            raise

    async def check_duplicate_prospectus(self, slug: Optional[str], requester_email: Optional[str]) -> Optional[Prospectus]:
        """
        Check for duplicate prospectus based on slug or requester email.

        Args:
            slug (Optional[str]): The slug to check.
            requester_email (Optional[str]): The email to check.

        Returns:
            Optional[Prospectus]: The prospectus if a match is found, otherwise None.
        """
        query = self.db_session.query(Prospectus)

        if slug is not None and requester_email is not None:
            query = query.filter(or_(Prospectus.slug == slug, Prospectus.requester_email == requester_email))
        elif slug is not None:
            query = query.filter(Prospectus.slug == slug)
        elif requester_email is not None:
            query = query.filter(Prospectus.requester_email == requester_email)

        return query.first()