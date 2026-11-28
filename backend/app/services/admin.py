"""Admin panel services: dashboard, accounts, mentorship, content, logs (F-037).

Every mutation here is privileged: routers gate them with ``require_role("admin")``
and each one appends an audit entry so the action stays traceable (AGENTS.md 10).
"""

import secrets
import uuid
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password
from app.infrastructure.db.models import (
    Broadcast,
    CalendarEvent,
    ChecklistItem,
    HabitCategory,
    MentorApplication,
    MentorGrant,
    MentorMessage,
    MentorProfile,
    MentorProgram,
    Note,
    RefreshToken,
    Routine,
    RoutineTemplate,
    SystemLog,
    User,
)

ACTIVITY_DAYS = 14

_CONTENT_MODELS: tuple[type[Any], ...] = (
    Routine,
    ChecklistItem,
    Note,
    CalendarEvent,
)


class AdminUserNotFoundError(AppError):
    """Raised when an administrative action targets an unknown account."""

    status_code = 404
    code = "USER_NOT_FOUND"
    message = "User not found."


class AdminSelfActionError(AppError):
    """Raised when an administrator would act on their own account."""

    status_code = 400
    code = "CANNOT_TARGET_SELF"
    message = "You cannot apply this action to your own account."


class AdminProtectedAccountError(AppError):
    """Raised when an action would lock out another administrator."""

    status_code = 403
    code = "ADMIN_ACCOUNT_PROTECTED"
    message = "Administrator accounts cannot be banned or disabled."


class TemplateNotFoundError(AppError):
    """Raised for unknown routine templates."""

    status_code = 404
    code = "TEMPLATE_NOT_FOUND"
    message = "Routine template not found."


class CategoryNotFoundError(AppError):
    """Raised for unknown habit categories."""

    status_code = 404
    code = "CATEGORY_NOT_FOUND"
    message = "Habit category not found."


class BroadcastNotFoundError(AppError):
    """Raised for unknown broadcasts."""

    status_code = 404
    code = "BROADCAST_NOT_FOUND"
    message = "Broadcast not found."


class DuplicateCategoryError(AppError):
    """Raised when a category name is already defined."""

    status_code = 409
    code = "CATEGORY_ALREADY_EXISTS"
    message = "A category with this name already exists."


def display_name(user: User) -> str:
    """Return the name an administrator sees for an account."""
    parts = [part for part in (user.first_name, user.last_name) if part]
    if parts:
        return " ".join(parts)
    if user.username:
        return user.username
    return user.email.split("@", 1)[0]


def as_utc(value: datetime) -> datetime:
    """Return ``value`` as an aware UTC instant (SQLite stores naive values)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


async def record_log(
    session: AsyncSession,
    *,
    level: str,
    event: str,
    message: str,
    actor_id: uuid.UUID | None = None,
    status_code: int | None = None,
    method: str | None = None,
    path: str | None = None,
) -> None:
    """Append one audit/error entry to the system log."""
    session.add(
        SystemLog(
            level=level,
            event=event,
            message=message,
            actor_id=actor_id,
            status_code=status_code,
            method=method,
            path=path,
        )
    )
    await session.commit()


async def _count(session: AsyncSession, model: type[Any], *conditions: Any) -> int:
    """Count rows of ``model`` matching ``conditions``."""
    query = select(func.count()).select_from(model)
    for condition in conditions:
        query = query.where(condition)
    return int(await session.scalar(query) or 0)


def _local_date(value: datetime) -> date:
    """Group a stored instant by its UTC calendar date."""
    return as_utc(value).date()


async def get_dashboard(session: AsyncSession) -> dict[str, Any]:
    """Collect every dashboard counter plus the recent activity series."""
    today = datetime.now(UTC).date()
    first_day = today - timedelta(days=ACTIVITY_DAYS - 1)
    window_start = datetime.combine(first_day, time.min, tzinfo=UTC)

    total_users = await _count(session, User)
    active_users = await _count(session, User, User.is_active.is_(True))
    banned_users = await _count(session, User, User.is_banned.is_(True))
    total_routines = await _count(session, Routine, Routine.deleted_at.is_(None))
    total_mentors = await _count(session, User, User.role == "mentor")
    pending_requests = await _count(
        session, MentorApplication, MentorApplication.status == "pending"
    )
    total_programs = await _count(session, MentorProgram)
    active_mentorships = await _count(session, MentorGrant, MentorGrant.revoked_at.is_(None))
    total_templates = await _count(session, RoutineTemplate)
    total_categories = await _count(session, HabitCategory)
    total_broadcasts = await _count(session, Broadcast)

    signup_rows = (
        await session.execute(
            select(User.created_at).where(User.created_at >= window_start)
        )
    ).scalars()
    signups_by_day: dict[date, int] = {}
    for created_at in signup_rows:
        key = _local_date(created_at)
        signups_by_day[key] = signups_by_day.get(key, 0) + 1

    routines_by_day: dict[date, int] = {}
    activity_by_day: dict[date, set[uuid.UUID]] = {}

    routine_rows = await session.execute(
        select(Routine.user_id, Routine.created_at).where(
            Routine.created_at >= window_start,
            Routine.deleted_at.is_(None),
        )
    )
    for user_id, created_at in routine_rows.all():
        key = _local_date(created_at)
        routines_by_day[key] = routines_by_day.get(key, 0) + 1
        activity_by_day.setdefault(key, set()).add(user_id)

    for model in (ChecklistItem, Note, CalendarEvent):
        rows = await session.execute(
            select(model.user_id, model.created_at).where(
                model.created_at >= window_start
            )
        )
        for user_id, created_at in rows.all():
            key = _local_date(created_at)
            activity_by_day.setdefault(key, set()).add(user_id)

    activity = [
        {
            "date": first_day + timedelta(days=offset),
            "signups": signups_by_day.get(first_day + timedelta(days=offset), 0),
            "routines": routines_by_day.get(first_day + timedelta(days=offset), 0),
            "active_users": len(activity_by_day.get(first_day + timedelta(days=offset), set())),
        }
        for offset in range(ACTIVITY_DAYS)
    ]

    return {
        "total_users": total_users,
        "active_users": active_users,
        "banned_users": banned_users,
        "total_routines": total_routines,
        "total_mentors": total_mentors,
        "pending_mentor_requests": pending_requests,
        "total_mentor_programs": total_programs,
        "active_mentorships": active_mentorships,
        "active_today": len(activity_by_day.get(today, set())),
        "total_templates": total_templates,
        "total_categories": total_categories,
        "total_broadcasts": total_broadcasts,
        "activity": activity,
    }


async def list_users(
    session: AsyncSession,
    *,
    search: str | None = None,
    role: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[tuple[User, int]], int]:
    """Return a page of accounts with their routine counts, newest first."""
    query = select(User, func.count(Routine.id)).outerjoin(
        Routine, (Routine.user_id == User.id) & (Routine.deleted_at.is_(None))
    )
    count_query = select(func.count()).select_from(User)

    conditions: list[Any] = []
    if search:
        term = f"%{search.strip()}%"
        conditions.append(
            or_(
                User.email.ilike(term),
                User.username.ilike(term),
                User.first_name.ilike(term),
                User.last_name.ilike(term),
            )
        )
    if role is not None:
        conditions.append(User.role == role)
    if status == "banned":
        conditions.append(User.is_banned.is_(True))
    elif status == "disabled":
        conditions.append(User.is_active.is_(False))
    elif status == "active":
        conditions.append(User.is_active.is_(True))
        conditions.append(User.is_banned.is_(False))

    for condition in conditions:
        query = query.where(condition)
        count_query = count_query.where(condition)

    query = (
        query.group_by(User.id)
        .order_by(User.created_at.desc(), User.id)
        .limit(limit)
        .offset(offset)
    )

    rows = await session.execute(query)
    total = int(await session.scalar(count_query) or 0)
    return [(user, int(count)) for user, count in rows.all()], total


async def _get_account(session: AsyncSession, user_id: uuid.UUID) -> User:
    """Load one account or raise USER_NOT_FOUND."""
    user = await session.get(User, user_id)
    if user is None:
        raise AdminUserNotFoundError
    return user


def _guard_target(admin: User, target: User) -> None:
    """Refuse destructive actions on the administrator's own account or peers."""
    if admin.id == target.id:
        raise AdminSelfActionError
    if target.role == "admin":
        raise AdminProtectedAccountError


async def _revoke_sessions(session: AsyncSession, user_id: uuid.UUID) -> None:
    """Revoke every live refresh-token family of an account."""
    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
        .execution_options(synchronize_session=False)
    )


async def set_user_banned(
    session: AsyncSession, admin: User, user_id: uuid.UUID, banned: bool
) -> User:
    """Ban or unban one account; banning ends its sessions immediately."""
    target = await _get_account(session, user_id)
    _guard_target(admin, target)

    target.is_banned = banned
    if banned:
        await _revoke_sessions(session, target.id)

    await record_log(
        session,
        level="audit",
        event="user.banned" if banned else "user.unbanned",
        message=(
            f"{display_name(admin)} {'banned' if banned else 'unbanned'} "
            f"{target.email}"
        ),
        actor_id=admin.id,
    )
    await session.commit()
    await session.refresh(target)
    return target


async def set_user_active(
    session: AsyncSession, admin: User, user_id: uuid.UUID, is_active: bool
) -> User:
    """Enable or disable one account; disabling ends its sessions."""
    target = await _get_account(session, user_id)
    _guard_target(admin, target)

    target.is_active = is_active
    if not is_active:
        await _revoke_sessions(session, target.id)

    await record_log(
        session,
        level="audit",
        event="user.enabled" if is_active else "user.disabled",
        message=(
            f"{display_name(admin)} "
            f"{'enabled' if is_active else 'disabled'} {target.email}"
        ),
        actor_id=admin.id,
    )
    await session.commit()
    await session.refresh(target)
    return target


async def reset_user_password(
    session: AsyncSession, admin: User, user_id: uuid.UUID
) -> str:
    """Replace an account's password with a random temporary one.

    The plaintext value is returned once, to the administrator who requested it,
    and is never written to the log or stored anywhere.
    """
    target = await _get_account(session, user_id)
    if target.id == admin.id:
        raise AdminSelfActionError

    temporary_password = secrets.token_urlsafe(9)
    target.password_hash = hash_password(temporary_password)
    await _revoke_sessions(session, target.id)

    await record_log(
        session,
        level="audit",
        event="user.password_reset",
        message=f"{display_name(admin)} reset the password of {target.email}",
        actor_id=admin.id,
    )
    await session.commit()
    return temporary_password


async def list_mentors(session: AsyncSession) -> list[dict[str, Any]]:
    """Return every mentor account with their client count."""
    rows = await session.execute(
        select(User, MentorProfile, func.count(MentorGrant.id))
        .outerjoin(MentorProfile, MentorProfile.user_id == User.id)
        .outerjoin(
            MentorGrant,
            (MentorGrant.mentor_id == User.id) & (MentorGrant.revoked_at.is_(None)),
        )
        .where(User.role == "mentor")
        .group_by(User.id, MentorProfile.id)
        .order_by(User.created_at, User.id)
    )

    return [
        {
            "id": user.id,
            "name": display_name(user),
            "email": user.email,
            "headline": profile.headline if profile else None,
            "bio": profile.bio if profile else None,
            "clients_count": int(clients),
            "created_at": user.created_at,
        }
        for user, profile, clients in rows.all()
    ]


async def remove_mentor(session: AsyncSession, admin: User, mentor_id: uuid.UUID) -> None:
    """Demote a mentor back to a regular account and revoke their grants.

    Historical messages and programs are kept: they belong to the users who
    received them, and deleting them would destroy conversation history.
    """
    mentor = await session.get(User, mentor_id)
    if mentor is None or mentor.role != "mentor":
        raise AdminUserNotFoundError

    mentor.role = "user"

    profile = await session.scalar(
        select(MentorProfile).where(MentorProfile.user_id == mentor.id)
    )
    if profile is not None:
        await session.delete(profile)

    await session.execute(
        update(MentorGrant)
        .where(MentorGrant.mentor_id == mentor.id, MentorGrant.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
        .execution_options(synchronize_session=False)
    )

    await record_log(
        session,
        level="audit",
        event="mentor.removed",
        message=f"{display_name(admin)} removed mentor {mentor.email}",
        actor_id=admin.id,
    )
    await session.commit()


async def assign_mentor(
    session: AsyncSession,
    admin: User,
    *,
    user_id: uuid.UUID,
    mentor_id: uuid.UUID,
) -> None:
    """Grant a mentor access to a user on the user's behalf."""
    user = await _get_account(session, user_id)
    mentor = await session.get(User, mentor_id)
    if mentor is None or mentor.role != "mentor":
        raise AdminUserNotFoundError
    if user.id == mentor.id:
        raise AppError(
            "A mentor cannot be assigned to themselves.",
            code="INVALID_ASSIGNMENT",
            status_code=400,
        )

    await session.execute(
        update(MentorGrant)
        .where(
            MentorGrant.user_id == user.id,
            MentorGrant.mentor_id != mentor.id,
            MentorGrant.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
        .execution_options(synchronize_session=False)
    )

    grant = await session.scalar(
        select(MentorGrant).where(
            MentorGrant.user_id == user.id,
            MentorGrant.mentor_id == mentor.id,
        )
    )
    if grant is None:
        session.add(MentorGrant(user_id=user.id, mentor_id=mentor.id))
    elif grant.revoked_at is not None:
        grant.revoked_at = None
        grant.granted_at = datetime.now(UTC)

    await record_log(
        session,
        level="audit",
        event="mentor.assigned",
        message=(
            f"{display_name(admin)} assigned mentor {mentor.email} to {user.email}"
        ),
        actor_id=admin.id,
    )
    await session.commit()


async def list_conversations(session: AsyncSession) -> list[dict[str, Any]]:
    """Return every mentor/client thread for supervision."""
    rows = await session.execute(
        select(
            MentorMessage.user_id,
            MentorMessage.mentor_id,
            func.count(MentorMessage.id),
            func.max(MentorMessage.created_at),
        )
        .group_by(MentorMessage.user_id, MentorMessage.mentor_id)
        .order_by(func.max(MentorMessage.created_at).desc())
    )
    pairs = rows.all()
    if not pairs:
        return []

    ids = {pair[0] for pair in pairs} | {pair[1] for pair in pairs}
    people = {
        user.id: user
        for user in (await session.scalars(select(User).where(User.id.in_(ids)))).all()
    }

    return [
        {
            "user_id": user_id,
            "user_name": display_name(people[user_id]) if user_id in people else "—",
            "user_email": people[user_id].email if user_id in people else "—",
            "mentor_id": mentor_id,
            "mentor_name": display_name(people[mentor_id])
            if mentor_id in people
            else "—",
            "mentor_email": people[mentor_id].email if mentor_id in people else "—",
            "messages_count": int(count),
            "last_message_at": last_at,
        }
        for user_id, mentor_id, count, last_at in pairs
    ]


async def get_conversation(
    session: AsyncSession, *, user_id: uuid.UUID, mentor_id: uuid.UUID
) -> list[dict[str, Any]]:
    """Return one thread in chronological order for moderation."""
    messages = list(
        (
            await session.scalars(
                select(MentorMessage)
                .where(
                    MentorMessage.user_id == user_id,
                    MentorMessage.mentor_id == mentor_id,
                )
                .order_by(MentorMessage.created_at, MentorMessage.id)
            )
        ).all()
    )
    if not messages:
        return []

    sender_ids = {message.sender_id for message in messages}
    senders = {
        user.id: user
        for user in (
            await session.scalars(select(User).where(User.id.in_(sender_ids)))
        ).all()
    }

    return [
        {
            "id": message.id,
            "sender_id": message.sender_id,
            "sender_name": display_name(senders[message.sender_id])
            if message.sender_id in senders
            else "—",
            "body": message.body,
            "created_at": message.created_at,
        }
        for message in messages
    ]


async def list_templates(session: AsyncSession) -> list[RoutineTemplate]:
    """Return every template, newest first."""
    return list(
        (
            await session.scalars(
                select(RoutineTemplate).order_by(
                    RoutineTemplate.created_at.desc(), RoutineTemplate.id
                )
            )
        ).all()
    )


async def create_template(
    session: AsyncSession,
    admin: User,
    *,
    title: str,
    description: str | None,
    category: str | None,
    duration_days: int | None,
    is_published: bool,
) -> RoutineTemplate:
    """Publish a new ready-made routine template."""
    template = RoutineTemplate(
        title=title,
        description=description,
        category=category,
        duration_days=duration_days,
        is_published=is_published,
    )
    session.add(template)
    await record_log(
        session,
        level="audit",
        event="template.created",
        message=f"{display_name(admin)} created template {title}",
        actor_id=admin.id,
    )
    await session.commit()
    await session.refresh(template)
    return template


async def _get_template(
    session: AsyncSession, template_id: uuid.UUID
) -> RoutineTemplate:
    """Load one template or raise TEMPLATE_NOT_FOUND."""
    template = await session.get(RoutineTemplate, template_id)
    if template is None:
        raise TemplateNotFoundError
    return template


async def update_template(
    session: AsyncSession,
    admin: User,
    template_id: uuid.UUID,
    values: dict[str, Any],
) -> RoutineTemplate:
    """Apply the supplied template fields."""
    template = await _get_template(session, template_id)
    for field, value in values.items():
        setattr(template, field, value)

    await record_log(
        session,
        level="audit",
        event="template.updated",
        message=f"{display_name(admin)} updated template {template.title}",
        actor_id=admin.id,
    )
    await session.commit()
    await session.refresh(template)
    return template


async def delete_template(
    session: AsyncSession, admin: User, template_id: uuid.UUID
) -> None:
    """Delete one template."""
    template = await _get_template(session, template_id)
    title = template.title
    await session.delete(template)

    await record_log(
        session,
        level="audit",
        event="template.deleted",
        message=f"{display_name(admin)} deleted template {title}",
        actor_id=admin.id,
    )
    await session.commit()


async def list_categories(session: AsyncSession) -> list[HabitCategory]:
    """Return every habit category, alphabetical."""
    return list(
        (await session.scalars(select(HabitCategory).order_by(HabitCategory.name))).all()
    )


async def create_category(
    session: AsyncSession,
    admin: User,
    *,
    name: str,
    description: str | None,
    color: str,
) -> HabitCategory:
    """Define a new habit category."""
    existing = await session.scalar(
        select(HabitCategory.id).where(func.lower(HabitCategory.name) == name.lower())
    )
    if existing is not None:
        raise DuplicateCategoryError

    category = HabitCategory(name=name, description=description, color=color)
    session.add(category)
    await record_log(
        session,
        level="audit",
        event="category.created",
        message=f"{display_name(admin)} created category {name}",
        actor_id=admin.id,
    )
    await session.commit()
    await session.refresh(category)
    return category


async def _get_category(session: AsyncSession, category_id: uuid.UUID) -> HabitCategory:
    """Load one category or raise CATEGORY_NOT_FOUND."""
    category = await session.get(HabitCategory, category_id)
    if category is None:
        raise CategoryNotFoundError
    return category


async def update_category(
    session: AsyncSession,
    admin: User,
    category_id: uuid.UUID,
    values: dict[str, Any],
) -> HabitCategory:
    """Apply the supplied category fields."""
    category = await _get_category(session, category_id)
    for field, value in values.items():
        setattr(category, field, value)

    await record_log(
        session,
        level="audit",
        event="category.updated",
        message=f"{display_name(admin)} updated category {category.name}",
        actor_id=admin.id,
    )
    await session.commit()
    await session.refresh(category)
    return category


async def delete_category(
    session: AsyncSession, admin: User, category_id: uuid.UUID
) -> None:
    """Delete one habit category."""
    category = await _get_category(session, category_id)
    name = category.name
    await session.delete(category)

    await record_log(
        session,
        level="audit",
        event="category.deleted",
        message=f"{display_name(admin)} deleted category {name}",
        actor_id=admin.id,
    )
    await session.commit()


async def list_broadcasts(session: AsyncSession) -> list[Broadcast]:
    """Return sent announcements, newest first."""
    return list(
        (
            await session.scalars(
                select(Broadcast).order_by(Broadcast.created_at.desc(), Broadcast.id)
            )
        ).all()
    )


async def create_broadcast(
    session: AsyncSession, admin: User, *, title: str, body: str
) -> Broadcast:
    """Send a platform-wide announcement to every account."""
    broadcast = Broadcast(title=title, body=body, audience="all", created_by=admin.id)
    session.add(broadcast)
    await record_log(
        session,
        level="audit",
        event="broadcast.sent",
        message=f"{display_name(admin)} sent broadcast {title}",
        actor_id=admin.id,
    )
    await session.commit()
    await session.refresh(broadcast)
    return broadcast


async def delete_broadcast(
    session: AsyncSession, admin: User, broadcast_id: uuid.UUID
) -> None:
    """Retract one announcement."""
    broadcast = await session.get(Broadcast, broadcast_id)
    if broadcast is None:
        raise BroadcastNotFoundError
    title = broadcast.title
    await session.delete(broadcast)

    await record_log(
        session,
        level="audit",
        event="broadcast.deleted",
        message=f"{display_name(admin)} deleted broadcast {title}",
        actor_id=admin.id,
    )
    await session.commit()


async def count_users(session: AsyncSession) -> int:
    """Return the number of accounts a broadcast reached."""
    return await _count(session, User)


async def list_logs(
    session: AsyncSession,
    *,
    level: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[SystemLog], int]:
    """Return a page of system log entries, newest first."""
    query = select(SystemLog)
    count_query = select(func.count()).select_from(SystemLog)

    conditions: list[Any] = []
    if level is not None:
        conditions.append(SystemLog.level == level)
    if search:
        term = f"%{search.strip()}%"
        conditions.append(
            or_(
                SystemLog.message.ilike(term),
                SystemLog.event.ilike(term),
                SystemLog.path.ilike(term),
            )
        )

    for condition in conditions:
        query = query.where(condition)
        count_query = count_query.where(condition)

    rows = await session.scalars(
        query.order_by(SystemLog.created_at.desc(), SystemLog.id)
        .limit(limit)
        .offset(offset)
    )
    total = int(await session.scalar(count_query) or 0)
    return list(rows), total
