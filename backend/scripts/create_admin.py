"""Promote an existing user to the admin role.

Usage: ``python scripts/create_admin.py --email someone@example.com``

Never creates accounts and never handles passwords: ``admin`` is granted only
by an operator with database access (ADR-0006). Re-running for an existing
admin is a no-op that exits 0.
"""

import argparse
import asyncio
import sys
from collections.abc import Sequence

from app.infrastructure.db.session import SessionFactory
from app.schemas.auth import normalize_email
from app.services.identity import UserNotFoundError, promote_to_admin

EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote an existing user to admin.")
    parser.add_argument(
        "--email",
        required=True,
        help="Email of an already-registered user.",
    )
    return parser.parse_args(argv)


async def _promote(email: str) -> int:
    async with SessionFactory() as session:
        try:
            changed = await promote_to_admin(session, email=email)
        except UserNotFoundError:
            print(f"error: no user found with email {email}", file=sys.stderr)
            return EXIT_FAILURE

        if changed:
            print(f"Promoted {email} to admin.")
        else:
            print(f"{email} is already an admin; nothing to do.")

        return EXIT_SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        email = normalize_email(args.email)
    except ValueError:
        print(f"error: invalid email address {args.email!r}", file=sys.stderr)
        return EXIT_FAILURE

    return asyncio.run(_promote(email))


if __name__ == "__main__":
    sys.exit(main())
