from fastapi import Header
from app.core.exceptions import unauthorized

async def get_current_user_id(x_user_id: int | None = Header(default=None)):
    if not x_user_id:
        raise unauthorized()
    return x_user_id
