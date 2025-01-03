import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from enum import Enum
from src.app.utils.Db import Base,engine

class ProspectusStages(Enum):
    INIT_TENANT_PROSPECTUS_ONBOARDING = "init.tenant.prospectus.onboarding"
    INIT_TENANT_ADMIN_EMAIL_ACTIVATION = "init.tenant.admin.email.activation"
    INIT_TENANT_ADMIN_EMAIL_VERIFICATION = "init.tenant.admin.email.verification"
    INIT_TENANT_PROSPECTUS_INFRASTRUCTURE = "init.tenant.prospectus.infrastructure"

class SubscriptionPlan(Enum):
    TRAIL = 'TRAIL'
    STARTER = 'STARTER'
    BUSINESS = 'BUSINESS',
    ENTERPRISE = 'ENTERPRISE'

class Prospectus(Base):
    __tablename__: str = 'Prospectus'

    # UUID as primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    subscription = Column(String, nullable=False)
    status = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_delete = Column(Boolean, default=False, nullable=False)

    # Requester details
    requester_first_name = Column(String, nullable=False)
    requester_last_name = Column(String, nullable=False)
    requester_email = Column(String, unique=True, nullable=False)
    requester_phone_number_country_code = Column(String, nullable=True)
    requester_phone_number = Column(String, nullable=True)
    requester_designation = Column(String, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Prospectus(id={self.id}, organization_name={self.title}, is_active={self.is_active})>"

Base.metadata.create_all(engine)