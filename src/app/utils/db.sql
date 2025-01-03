-- Create the Prospectus table if it doesn't already exist
CREATE TABLE IF NOT EXISTS "Prospectus" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(255) NOT NULL DEFAULT 'init.tenant.prospectus.onboarding',
    subscription VARCHAR(50) NOT NULL DEFAULT 'TRAIL',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_delete BOOLEAN NOT NULL DEFAULT FALSE,
    requester_first_name VARCHAR(255) NOT NULL,
    requester_last_name VARCHAR(255) NOT NULL,
    requester_email VARCHAR(255) NOT NULL UNIQUE,
    requester_phone_number_country_code VARCHAR(10),
    requester_phone_number VARCHAR(20),
    requester_designation VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Add check constraints for valid subscription and status values
DO $$
BEGIN
    -- Adding status enum-like constraint if not exists
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'prospectus_status_check') THEN
        ALTER TABLE "Prospectus" ADD CONSTRAINT "prospectus_status_check"
        CHECK (status IN ('init.tenant.prospectus.onboarding', 'init.tenant.admin.email.activation',
                          'init.tenant.admin.email.verification', 'init.tenant.prospectus.infrastructure'));
    END IF;

    -- Adding subscription enum-like constraint if not exists
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'prospectus_subscription_check') THEN
        ALTER TABLE "Prospectus" ADD CONSTRAINT "prospectus_subscription_check"
        CHECK (subscription IN ('TRAIL', 'STARTER', 'BUSINESS', 'ENTERPRISE'));
    END IF;
END $$;
