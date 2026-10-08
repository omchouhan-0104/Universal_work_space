# from typing import Annotated

# import jwt
# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
# from sqlalchemy.orm import Session

# from app.core.config import settings
# from app.database.session import get_db
# from app.models.user import User


# security = HTTPBearer()


# def get_current_user(
#     credentials: Annotated[
#         HTTPAuthorizationCredentials,
#         Depends(security),
#     ],
#     db: Session = Depends(get_db),
# ) -> User:
#     token = credentials.credentials

#     try:
#         payload = jwt.decode(
#             token,
#             settings.SECRET_KEY,
#             algorithms=[settings.ALGORITHM],
#         )

#         user_id = payload.get("sub")

#         if user_id is None:
#             raise ValueError("Token subject missing")

#         user = db.get(User, int(user_id))

#         if user is None:
#             raise ValueError("User not found")

#         if not user.is_active:
#             raise ValueError("Inactive user")

#         return user

#     except (jwt.InvalidTokenError, ValueError):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#         )

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise ValueError("Token subject missing")

        user = db.get(
            User,
            int(user_id),
        )

        if user is None:
            raise ValueError("User not found")

        if not user.is_active:
            raise ValueError("Inactive user")

        return user

    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )