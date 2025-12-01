import os
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

# Initialize JWKS Client
# We use PyJWKClient to handle fetching and caching of the public keys from Auth0
jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
jwks_client = PyJWKClient(jwks_url)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the Auth0 JWT token.
    
    1. Checks for a development environment bypass.
    2. Fetches the public key from Auth0 (cached).
    3. Decodes and validates the token signature, audience, and issuer.
    """
    token = credentials.credentials
    
    # Development Bypass
    # This allows developers to test endpoints without a valid Auth0 token
    # ONLY if the environment is explicitly set to 'local_dev'
    if os.getenv("ENVIRONMENT") == "local_dev":
         return {"sub": "mock_user_id", "email": "mock@example.com"}

    try:
        # Get the Signing Key
        # This will look up the 'kid' from the token header in the cached JWKS
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode & Verify
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/",
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token is expired"
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        # Catch-all for other errors to ensure we don't leak internal details
        # but still return a 401/500 as appropriate
        print(f"Authentication error: {e}") # Log the error for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate credentials"
        )
