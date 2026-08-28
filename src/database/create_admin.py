"""
src/database/create_admin.py
=============================

Creates the initial Admin account for the hospital system.

This is a setup script.
It is NOT a public API endpoint.
"""

import asyncio
import getpass

from sqlalchemy import select

from src.database.base_engine import AsyncSessionLocal
from src.database.models import User
from src.auth_service.security import hash_password


async def create_admin() -> None:

    print("\n=== Hospital Admin Setup ===\n")

    email = input("Admin email:").strip()
    username = input("Admin username:").strip()
    full_name = input("Admin full name:").strip()

    password = getpass.getpass("Admin password:")
    confirm_password = getpass.getpass("Confirm password:")

    # ---------------------------------------------------------
    # 1. Validate password
    # ---------------------------------------------------------

   
    if password != confirm_password:
        print("❌ Passwords do not match.")
        return

    if len(password) < 8:
        print("❌ Password must contain at least 8 characters.")
        return

    # ---------------------------------------------------------
    # 2. Connect to database
    # ---------------------------------------------------------

    async with AsyncSessionLocal() as db:

        # -----------------------------------------------------
        # 3. Check email
        # -----------------------------------------------------

        result = await db.execute(
            select(User).where(User.email == email)
        )

        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("❌ An account with this email already exists.")
            return

        # -----------------------------------------------------
        # 4. Check username
        # -----------------------------------------------------

        result = await db.execute(
            select(User).where(User.username == username)
        )

        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("❌ This username is already taken.")
            return

        # -----------------------------------------------------
        # 5. Hash password
        # -----------------------------------------------------

        hashed_password = hash_password(password)

        # -----------------------------------------------------
        # 6. Create Admin
        # -----------------------------------------------------

        admin = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name or None,
            role="ADMIN",
            is_active=True,
        )

        db.add(admin)

        # -----------------------------------------------------
        # 7. Save to database
        # -----------------------------------------------------

        await db.commit()
        await db.refresh(admin)

        print("\n✅ Admin created successfully!")
        print(f"Email: {admin.email}")
        print(f"Username: {admin.username}")
        print(f"Role: {admin.role}")
        print(f"Active: {admin.is_active}")


if __name__ == "__main__":
    asyncio.run(create_admin())