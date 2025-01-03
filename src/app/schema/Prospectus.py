from pydantic import BaseModel, constr
from src.app.model.Prospectus import SubscriptionPlan, ProspectusStages
from typing import Optional
from uuid import UUID

# Schema for creating a new prospectus
class OnboardingNewProspectus(BaseModel):
    """
    Fields required for creating a new prospectus.
    """
    title: constr(strip_whitespace=True, min_length=3, max_length=25) = ""
    slug: constr(strip_whitespace=True, min_length=3, max_length=25) = ""
    subscription: constr(strip_whitespace=True, min_length=3, max_length=25) = ""
    requester_first_name: constr(strip_whitespace=True, min_length=1, max_length=50) = ""
    requester_last_name: constr(strip_whitespace=True, min_length=1, max_length=50) = ""
    requester_email: constr(strip_whitespace=True, min_length=10, max_length=50) = ""
    requester_phone_number_country_code: Optional[constr(min_length=1, max_length=5)] = ""
    requester_phone_number: Optional[constr(min_length=10, max_length=15)] = ""
    requester_designation: constr(strip_whitespace=True, min_length=1, max_length=50) = ""


# Schema for creating a new prospectus
class GenerateEmailActivationUrl(BaseModel):
    """
    Fields required for creating a new Email Activation Url.
    """
    slug: constr(strip_whitespace=True, min_length=3, max_length=25) = ""
    requester_email: constr(strip_whitespace=True, min_length=10, max_length=50) = ""

class OnboardingNewProspectusResponse(BaseModel):
    """
    Read-only schema for returning OnboardingNewProspectus details, including system-generated fields.
    """
    id: UUID
    title: str
    slug: str
    status: str

    class Config:
        from_attributes = True

class IdentityActivationResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    status: str
    activation_link: str

    class Config:
        from_attributes = True