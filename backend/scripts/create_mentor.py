"""Create (or promote) a mentor account and its public profile.

Usage:

    python scripts/create_mentor.py --email mentor@example.com \
        --password secret123 --first-name مریم --last-name کریمی \
        --headline "برنامه درسی و مطالعه" --bio "..."

Existing accounts are promoted to ``mentor`` and have their profile upserted;
no account is ever demoted. The password only applies to newly created users.
"""

import argparse
import asyncio
import sys
from collections.abc import Sequence

from sqlalchemy import select

from app.infrastructure.db.models import MentorProfile, User
from app.infrastructure.db.session import SessionFactory
from app.schemas.auth import normalize_email
from app.services.identity import register_user

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or promote a mentor account with a public profile."
    )
    parser.add_argument("--email", required=True)
    parser.add_argument(
        "--password",
        help="Password for a newly created account (ignored for existing users).",
    )
    parser.add_argument("--username")
    parser.add_argument("--first-name", required=True)
    parser.add_argument("--last-name", required=True)
    parser.add_argument("--phone-number", default="09000000000")
    parser.add_argument("--headline")
    parser.add_argument("--bio")
    return parser.parse_args(argv)


async def _upsert(email: str, args: argparse.Namespace) -> int:
    async with SessionFactory() as session:
        user = await session.scalar(select(User).where(User.email == email))

        if user is None:
            if not args.password:
                print(
                    "error: --password is required to create a new account",
                    file=sys.stderr,
                )
                return EXIT_FAILURE

            try:
                user = await register_user(
                    session,
                    email=email,
                    password=args.password,
                    username=args.username or email.split("@", 1)[0],
                    first_name=args.first_name,
                    last_name=args.last_name,
                    phone_number=args.phone_number,
                )
            except Exception as exc:  # noqa: BLE001 - the CLI reports the reason
                print(f"error: could not create account: {exc}", file=sys.stderr)
                return EXIT_FAILURE

        user.role = "mentor"

        profile = await session.scalar(
            select(MentorProfile).where(MentorProfile.user_id == user.id)
        )
        if profile is None:
            session.add(
                MentorProfile(
                    user_id=user.id,
                    headline=args.headline,
                    bio=args.bio,
                )
            )
        else:
            profile.headline = args.headline
            profile.bio = args.bio

        await session.commit()

    print(f"Mentor ready: {email}")
    return EXIT_SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        email = normalize_email(args.email)
    except ValueError:
        print(f"error: invalid email address {args.email!r}", file=sys.stderr)
        return EXIT_FAILURE

    return asyncio.run(_upsert(email, args))


if __name__ == "__main__":
    sys.exit(main())
