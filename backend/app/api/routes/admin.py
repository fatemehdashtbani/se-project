"""Admin panel routes (F-037). HTTP concerns only."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_role
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_session
from app.schemas.admin import (
    AccountFlagRequest,
    AdminDashboardResponse,
    AdminMentorListResponse,
    AdminMessageResponse,
    AdminUserListResponse,
    AdminUserResponse,
    BroadcastCreate,
    BroadcastListResponse,
    BroadcastResponse,
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
    ConversationListResponse,
    ConversationMessagesResponse,
    MentorAssignmentRequest,
    SystemLogListResponse,
    SystemLogResponse,
    TemplateCreate,
    TemplateListResponse,
    TemplateResponse,
    TemplateUpdate,
    TemporaryPasswordResponse,
)
from app.services import admin as admin_service
from app.services.admin import list_users as service_list_users

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
AdminDep = Annotated[User, Depends(require_role("admin"))]


def _user_response(user: User, routines_count: int) -> AdminUserResponse:
    """Map an account row and its routine count to the admin table schema."""
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        role=user.role,
        timezone=user.timezone,
        is_active=user.is_active,
        is_banned=user.is_banned,
        created_at=user.created_at,
        routines_count=routines_count,
    )


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def read_dashboard(admin: AdminDep, session: SessionDep) -> AdminDashboardResponse:
    """Return the platform overview counters and activity chart data."""
    return AdminDashboardResponse.model_validate(await admin_service.get_dashboard(session))


@router.get("/users", response_model=AdminUserListResponse)
async def read_users(
    admin: AdminDep,
    session: SessionDep,
    search: Annotated[str | None, Query(max_length=120)] = None,
    role: Annotated[str | None, Query(pattern="^(user|mentor|admin)$")] = None,
    status_filter: Annotated[
        str | None, Query(alias="status", pattern="^(active|disabled|banned)$")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AdminUserListResponse:
    """List accounts with search, role and status filters."""
    rows, total = await service_list_users(
        session,
        search=search,
        role=role,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return AdminUserListResponse(
        items=[_user_response(user, count) for user, count in rows],
        total=total,
    )


@router.post("/users/{user_id}/ban", response_model=AdminUserResponse)
async def ban_user(
    user_id: uuid.UUID,
    payload: AccountFlagRequest,
    admin: AdminDep,
    session: SessionDep,
) -> AdminUserResponse:
    """Ban or unban an account."""
    user = await admin_service.set_user_banned(session, admin, user_id, payload.value)
    return _user_response(user, 0)


@router.post("/users/{user_id}/activation", response_model=AdminUserResponse)
async def activate_user(
    user_id: uuid.UUID,
    payload: AccountFlagRequest,
    admin: AdminDep,
    session: SessionDep,
) -> AdminUserResponse:
    """Enable or disable an account."""
    user = await admin_service.set_user_active(session, admin, user_id, payload.value)
    return _user_response(user, 0)


@router.post(
    "/users/{user_id}/reset-password", response_model=TemporaryPasswordResponse
)
async def reset_password(
    user_id: uuid.UUID, admin: AdminDep, session: SessionDep
) -> TemporaryPasswordResponse:
    """Replace an account password with a random temporary one."""
    temporary_password = await admin_service.reset_user_password(session, admin, user_id)
    return TemporaryPasswordResponse(temporary_password=temporary_password)


@router.get("/mentors", response_model=AdminMentorListResponse)
async def read_mentors(
    admin: AdminDep, session: SessionDep
) -> AdminMentorListResponse:
    """List every active mentor and their client load."""
    items = await admin_service.list_mentors(session)
    return AdminMentorListResponse(items=items, total=len(items))


@router.post("/mentors/{mentor_id}/remove", status_code=status.HTTP_204_NO_CONTENT)
async def remove_mentor(
    mentor_id: uuid.UUID, admin: AdminDep, session: SessionDep
) -> None:
    """Demote a mentor and end their active mentorships."""
    await admin_service.remove_mentor(session, admin, mentor_id)


@router.post("/mentors/assign", status_code=status.HTTP_204_NO_CONTENT)
async def assign_mentor(
    payload: MentorAssignmentRequest, admin: AdminDep, session: SessionDep
) -> None:
    """Assign a mentor to a user."""
    await admin_service.assign_mentor(
        session, admin, user_id=payload.user_id, mentor_id=payload.mentor_id
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def read_conversations(
    admin: AdminDep, session: SessionDep
) -> ConversationListResponse:
    """List mentor/client threads available for supervision."""
    items = await admin_service.list_conversations(session)
    return ConversationListResponse(items=items, total=len(items))


@router.get("/conversations/messages", response_model=ConversationMessagesResponse)
async def read_conversation_messages(
    admin: AdminDep,
    session: SessionDep,
    user_id: Annotated[uuid.UUID, Query()],
    mentor_id: Annotated[uuid.UUID, Query()],
) -> ConversationMessagesResponse:
    """Return one mentor/client thread for moderation."""
    items = await admin_service.get_conversation(
        session, user_id=user_id, mentor_id=mentor_id
    )
    return ConversationMessagesResponse(
        user_id=user_id,
        mentor_id=mentor_id,
        items=[AdminMessageResponse(**item) for item in items],
    )


@router.get("/templates", response_model=TemplateListResponse)
async def read_templates(
    admin: AdminDep, session: SessionDep
) -> TemplateListResponse:
    """List every routine template."""
    templates = await admin_service.list_templates(session)
    items = [TemplateResponse.model_validate(template) for template in templates]
    return TemplateListResponse(items=items, total=len(items))


@router.post(
    "/templates",
    status_code=status.HTTP_201_CREATED,
    response_model=TemplateResponse,
)
async def create_template(
    payload: TemplateCreate, admin: AdminDep, session: SessionDep
) -> TemplateResponse:
    """Create a ready-made routine template."""
    template = await admin_service.create_template(
        session,
        admin,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        duration_days=payload.duration_days,
        is_published=payload.is_published,
    )
    return TemplateResponse.model_validate(template)


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    payload: TemplateUpdate,
    admin: AdminDep,
    session: SessionDep,
) -> TemplateResponse:
    """Update the supplied fields of one template."""
    template = await admin_service.update_template(
        session, admin, template_id, payload.model_dump(exclude_unset=True)
    )
    return TemplateResponse.model_validate(template)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: uuid.UUID, admin: AdminDep, session: SessionDep
) -> None:
    """Delete one template."""
    await admin_service.delete_template(session, admin, template_id)


@router.get("/categories", response_model=CategoryListResponse)
async def read_categories(
    admin: AdminDep, session: SessionDep
) -> CategoryListResponse:
    """List every habit category."""
    categories = await admin_service.list_categories(session)
    items = [CategoryResponse.model_validate(category) for category in categories]
    return CategoryListResponse(items=items, total=len(items))


@router.post(
    "/categories",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryResponse,
)
async def create_category(
    payload: CategoryCreate, admin: AdminDep, session: SessionDep
) -> CategoryResponse:
    """Define a habit category."""
    category = await admin_service.create_category(
        session,
        admin,
        name=payload.name,
        description=payload.description,
        color=payload.color,
    )
    return CategoryResponse.model_validate(category)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    admin: AdminDep,
    session: SessionDep,
) -> CategoryResponse:
    """Update the supplied fields of one category."""
    category = await admin_service.update_category(
        session, admin, category_id, payload.model_dump(exclude_unset=True)
    )
    return CategoryResponse.model_validate(category)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID, admin: AdminDep, session: SessionDep
) -> None:
    """Delete one habit category."""
    await admin_service.delete_category(session, admin, category_id)


@router.get("/broadcasts", response_model=BroadcastListResponse)
async def read_broadcasts(
    admin: AdminDep, session: SessionDep
) -> BroadcastListResponse:
    """List sent announcements."""
    broadcasts = await admin_service.list_broadcasts(session)
    recipients = await admin_service.count_users(session)
    items = [
        BroadcastResponse(
            id=broadcast.id,
            title=broadcast.title,
            body=broadcast.body,
            audience=broadcast.audience,
            recipients=recipients,
            created_at=broadcast.created_at,
        )
        for broadcast in broadcasts
    ]
    return BroadcastListResponse(items=items, total=len(items))


@router.post(
    "/broadcasts",
    status_code=status.HTTP_201_CREATED,
    response_model=BroadcastResponse,
)
async def create_broadcast(
    payload: BroadcastCreate, admin: AdminDep, session: SessionDep
) -> BroadcastResponse:
    """Send a platform-wide announcement."""
    broadcast = await admin_service.create_broadcast(
        session, admin, title=payload.title, body=payload.body
    )
    recipients = await admin_service.count_users(session)
    return BroadcastResponse(
        id=broadcast.id,
        title=broadcast.title,
        body=broadcast.body,
        audience=broadcast.audience,
        recipients=recipients,
        created_at=broadcast.created_at,
    )


@router.delete("/broadcasts/{broadcast_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_broadcast(
    broadcast_id: uuid.UUID, admin: AdminDep, session: SessionDep
) -> None:
    """Retract one announcement."""
    await admin_service.delete_broadcast(session, admin, broadcast_id)


@router.get("/logs", response_model=SystemLogListResponse)
async def read_logs(
    admin: AdminDep,
    session: SessionDep,
    level: Annotated[
        str | None, Query(pattern="^(error|warning|info|audit)$")
    ] = None,
    search: Annotated[str | None, Query(max_length=120)] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SystemLogListResponse:
    """List system log entries, newest first."""
    rows, total = await admin_service.list_logs(
        session, level=level, search=search, limit=limit, offset=offset
    )
    return SystemLogListResponse(
        items=[SystemLogResponse.model_validate(row) for row in rows],
        total=total,
    )
