from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth_router import get_current_user
from db import get_async_session
from .groups_models import GroupResponse, GroupCreate
from models import Group
from .serializers import serialize_group

groups_router = APIRouter(tags=["groups"])


@groups_router.post("/create_group", response_model=GroupResponse)
async def create_group(
        group: GroupCreate,
        user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
):
    group_data = group.dict()
    group_data["author_id"] = user["id"]
    new_group = Group(**group_data)

    async with db.begin():
        db.add(new_group)
        await db.commit()

    async with db.begin():
        await db.refresh(new_group)

    return serialize_group(new_group)