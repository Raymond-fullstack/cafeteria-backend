from fastapi import Depends, HTTPException, status

from app.models import User
from app.security import get_current_user


def require_roles(*allowed_roles: str):
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of the roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_dependency
