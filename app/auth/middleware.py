from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.user import User, UserRole


def require_roles(*roles: UserRole) -> Callable:
    """Dependency factory that restricts access to specific roles."""

    async def _check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check_role
