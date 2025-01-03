import hashlib
import hmac
import base64
import time
import binascii
from uuid import UUID
import logging
from fastapi import HTTPException, status


from src.app.model.Prospectus import Prospectus
from src.config import AppConfigs

# Initialize logging
logger = logging.getLogger(__name__)

class HmacAuthenticator:
    def __init__(self):
        pass

    async def generate_token(self, id:UUID, email: str, slug: str) -> str:
        """
        Generate a secure, time-bound, URL-safe token.

        Args:
            email (str): The email address of the user.
            id (str): A unique identifier (UUID format).
            slug (str): Contextual information for the token.

        Returns:
            str: A URL-safe, HMAC-signed token.
        """
        expiration_seconds: int = AppConfigs.HMAC_TOKEN_EXPIRATION_SECONDS
        # Calculate the expiration timestamp
        timestamp = int(time.time()) + expiration_seconds

        # Create the message to sign
        message = f"{id}:{email}:{slug}:{timestamp}".encode()

        # Ensure the secret key is encoded to bytes
        secret_key = AppConfigs.HMAC_SECRET_KEY.encode()

        # Generate the HMAC signature
        signature = hmac.new(secret_key, message, hashlib.sha256).digest()

        # Encode the message and signature into a URL-safe token
        token = base64.urlsafe_b64encode(message + b"." + signature).decode()

        return token

    async def verify_token(self, key: str) -> str:
        """Verify the token's integrity and expiration."""
        try:
            # Decode the token and split into message and signature
            decoded = base64.urlsafe_b64decode(key.encode())
            message, signature = decoded.rsplit(b".", 1)

            # Ensure the secret key is encoded to bytes
            secret_key = AppConfigs.HMAC_SECRET_KEY.encode()

            # Recalculate the signature
            expected_signature = hmac.new(secret_key, message, hashlib.sha256).digest()

            # Verify the signature
            if not hmac.compare_digest(signature, expected_signature):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid identity activation key.")

            # Extract the email and timestamp from the message
            id, email, slug, timestamp = message.decode().split(":")
            timestamp = int(timestamp)

            # Check expiration
            if time.time() > timestamp:
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Identity activation key has been expired.")

            return email
        except binascii.Error as e:
            # Catch base64 decoding errors
            print(f"Error during decoding: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid identity activation key.")
