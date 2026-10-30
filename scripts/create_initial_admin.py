from __future__ import annotations

import argparse
from getpass import getpass

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User, UserRole
from app.security import hash_password


def create_admin(username: str, email: str, full_name: str, password: str):
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    with Session(engine) as session:
        if session.query(User).filter((User.username == username) | (User.email == email)).first():
            raise ValueError("An admin with that username or email already exists")
        admin = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        print(f"Created system administrator: {username}")


def main():
    parser = argparse.ArgumentParser(description="Create the initial system administrator")
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", required=True)
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    password = args.password or getpass("Enter admin password: ")
    create_admin(args.username, args.email, args.full_name, password)


if __name__ == "__main__":
    main()
