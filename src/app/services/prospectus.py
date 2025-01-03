import logging
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from src.app.schema.Prospectus import OnboardingNewProspectus, OnboardingNewProspectusResponse, IdentityActivationResponse
from src.app.model.Prospectus import Prospectus, ProspectusStages
from src.app.repository.Prospectus_Repository import ProspectusRepository
from src.app.utils.HMAC import HmacAuthenticator
from src.app.utils.Redis import RedisClient
from src.app.utils.Mailer import EmailClient, EmailTemplates, EmailSender
from src.config import AppConfigs

# Initialize logging
logger = logging.getLogger(__name__)

class ProspectusService:
    def __init__(self, db_session: Session):
        """
        Initializes the ProspectusService with a database session.

        Args:
            db_session (Session): SQLAlchemy database session.
        """
        self.db_session = db_session
        self.prospectus_repository = ProspectusRepository(db_session)

    async def onboarding_new_prospectus(self, background_tasks: BackgroundTasks, prospectus: OnboardingNewProspectus ) -> OnboardingNewProspectusResponse:
        """
        Handles the onboarding of a new prospectus.
        """
        try:
            # Log the onboarding request
            logger.info(f"Starting the onboarding process for new prospectus '{prospectus.title}'.")

            # Check if the prospectus slug and requester email id is unique
            check_duplicate_slug = await self.prospectus_repository.check_duplicate_prospectus(prospectus.slug, None)
            if check_duplicate_slug:
                logger.error(f"Slug '{prospectus.slug}' is already in use.")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"The slug '{prospectus.slug}' is already in use. Please choose a different slug."
                )

            # Validate the requester email
            check_duplicate_email = await self.prospectus_repository.check_duplicate_prospectus(None,prospectus.requester_email)
            if check_duplicate_email:
                logger.error(f"Requester email '{prospectus.requester_email}' is already in use.")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"The requester email '{prospectus.requester_email}' is already in use. Please use a different email."
                )

            # Delegate the creation of the tenant to the repository
            new_prospectus: Prospectus = await self.prospectus_repository.create_prospectus(prospectus)

            if new_prospectus:
                background_tasks.add_task(self.promote_tenant_prospectus, id=new_prospectus.id)
            else:
                logger.info(f"Skipping tenant prospectus promotion, Check the below details \n{new_prospectus}")

            # Map the created tenant to the response schema
            response = OnboardingNewProspectusResponse(
                id = new_prospectus.id,
                slug = new_prospectus.slug,
                title = new_prospectus.title,
                status = new_prospectus.status
            )

            # Log successful onboarding
            logger.info(f"Prospectus '{new_prospectus.title}' successfully onboarded with ID {new_prospectus.id}.")

            return response

        except Exception as e:
            # Log unexpected exceptions
            logger.error(f"An unexpected error occurred during tenant onboarding: {str(e)}")
            raise

    async def list_prospectus(self, page: int, limit: int) -> List[OnboardingNewProspectusResponse]:
        """
        Retrieve paginated list of Prospectus.

        Args:
            page (int): The page number for pagination.
            limit (int): The number of items per page.

        Returns:
            List[OnboardingNewProspectusResponse]: Paginated prospectus data.
        """
        dataset = await self.prospectus_repository.get_prospectus(page, limit)
        return [OnboardingNewProspectusResponse.model_validate(item) for item in dataset]

    async def get_prospectus(self, id: UUID) -> Optional[OnboardingNewProspectusResponse]:
        """
        Retrieve paginated list of Prospectus.

        Args:
            id (UUID): The page number for pagination.

        Returns:
            List[OnboardingNewProspectusResponse]: Paginated prospectus data.
            :param id:
        """
        return await self.prospectus_repository.get_prospectus_by_id(id)

    async def promote_tenant_prospectus(self,id: UUID) -> OnboardingNewProspectusResponse:
        try:
            # Delegate the creation of the tenant to the repository
            prospectus: Prospectus = await self.prospectus_repository.get_prospectus_by_id(id)

            # Define the stage transitions
            transitions = {
                ProspectusStages.INIT_TENANT_PROSPECTUS_ONBOARDING: ProspectusStages.INIT_TENANT_ADMIN_EMAIL_ACTIVATION,
                ProspectusStages.INIT_TENANT_ADMIN_EMAIL_ACTIVATION: ProspectusStages.INIT_TENANT_ADMIN_EMAIL_VERIFICATION,
                ProspectusStages.INIT_TENANT_ADMIN_EMAIL_VERIFICATION: ProspectusStages.INIT_TENANT_PROSPECTUS_INFRASTRUCTURE,
            }

            # Determine the next stage
            next_stage = transitions.get(ProspectusStages(prospectus.status))
            if not next_stage:
                raise ValueError(f"Invalid or terminal stage: {ProspectusStages(prospectus.status)}")

            # Update the prospectus status to the next stage
            updated_prospectus: Prospectus = await self.prospectus_repository.promote_prospectus_status(id, next_stage.value)

            # Generate identity activation link for the prospectus
            if updated_prospectus.status == ProspectusStages.INIT_TENANT_ADMIN_EMAIL_ACTIVATION.value:
                await self.identity_activation(id = updated_prospectus.id)

            # Map the created tenant to the response schema
            response = OnboardingNewProspectusResponse(
                id = updated_prospectus.id,
                slug = updated_prospectus.slug,
                title = updated_prospectus.title,
                status = updated_prospectus.status
            )

            return response

        except Exception as e:
            # Log unexpected exceptions
            logger.error(f"An unexpected error occurred during promoting tenant prospectus: {str(e)}")
            raise

    async def identity_activation(self, id: UUID) -> IdentityActivationResponse:
        """
        Activates identity by generating a secure token if the prospectus is in the correct stage.

        Args:
            id (UUID): The unique identifier for the prospectus.

        Returns:
            str: A generated activation token.

        Raises:
            HTTPException: If the prospectus is not in the expected stage or an error occurs.
        """
        # Retrieve the prospectus by ID
        prospectus: Prospectus = await self.prospectus_repository.get_prospectus_by_id(id)

        # Validate the prospectus
        if prospectus is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid prospectus id.")

        # Check if the prospectus is in the expected stage
        if prospectus.status == ProspectusStages.INIT_TENANT_ADMIN_EMAIL_ACTIVATION.value:
            # Generate and return the activation token
            key = await HmacAuthenticator().generate_token(id= prospectus.id, email=prospectus.requester_email, slug=prospectus.slug)
            await RedisClient.add(f"acl.tp.iv-{prospectus.id}", key, AppConfigs.HMAC_TOKEN_EXPIRATION_SECONDS)

            # Structure the activation link
            activation_link = f"{AppConfigs.SSO_MFA_URL}/auth/identity-verification/{key}?utm_source=tp.iv&utm_scope=email&utm_id={prospectus.id}"

            # Send an Identity Activation email
            template = EmailTemplates.load("Identity_Activation")

            emailprovider = await EmailClient().notify(
                subject=template.Subject,
                sender=EmailSender().NoReply,
                recipient=prospectus.requester_email,
                message=(lambda: (
                    template.Content
                    .replace("##LINK##", activation_link)
                    .replace("##EMAIL##", prospectus.requester_email)
                    .replace("##NAME##", f"{prospectus.requester_first_name} {prospectus.requester_last_name}")
                ))(),
            )

            print(emailprovider)

            response = IdentityActivationResponse(
                id = prospectus.id,
                slug = prospectus.slug,
                title = prospectus.title,
                status = prospectus.status,
                activation_link = activation_link
            )

            logger.info(f"Identity activation link successfully generated for prospectus '{prospectus.title}' \n{activation_link}\n")

            return response
        else:
            # Raise an error if the status does not match the expected stage
            print(f"Unexpected status: {prospectus.status}. Expected: {ProspectusStages.INIT_TENANT_ADMIN_EMAIL_ACTIVATION.value}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The prospectus is not in the correct stage for activation. Please try again later."
            )

    async def identity_verification(self, id: UUID, key: str) -> str:
        """
        Verifies identity by generating a secure token if the prospectus is in the correct stage.

        Args:
            id (UUID): The unique identifier for the prospectus.
            key (str): The activation key to validate.

        Returns:
            str: A message indicating the verification status.

        Raises:
            HTTPException: If the prospectus is not in the expected stage or the key is invalid.
        """
        # Retrieve the prospectus by ID
        prospectus = await self.prospectus_repository.get_prospectus_by_id(id)

        # Validate the prospectus
        if prospectus:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid prospectus id.")

        # Validate the current stage of the prospectus
        if prospectus.status != ProspectusStages.INIT_TENANT_PROSPECTUS_INFRASTRUCTURE.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The prospectus is not in the correct stage for verification. Please try again later."
            )

        # Fetch the cached key for the given prospectus
        partial_cached_key = await RedisClient.fetch(f"acl.tp.iv-{prospectus.id}")

        if partial_cached_key != key:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email activation link expired.")

        # Verify the token and return a success message
        email = await HmacAuthenticator().verify_token(key)
        return f"Email {email} verified successfully!"
