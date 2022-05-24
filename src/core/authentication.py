import logging
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPBasicCredentials
from fastapi.security import HTTPBearer
from pydantic import BaseModel

logger = logging.getLogger(__name__)

security = HTTPBearer()


class User(BaseModel):
    id: UUID


async def get_user(credentials: HTTPBasicCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, 'super-secret-key', algorithms=["HS256"])
        user_id: str = payload['sub']['user_id']
        current_user = User(id=user_id)
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization token expired')
    except jwt.exceptions.MissingRequiredClaimError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect claims, check the audience and issuer.')
    except Exception as error:
        logger.error(error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unable to parse authentication token')
    return current_user
