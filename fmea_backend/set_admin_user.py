#!/usr/bin/env python3
"""
Script to grant admin rights to a user by email address.
Usage: python set_admin_user.py <email>
"""

import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from database import SessionLocal, Base
from models.user import User
from crud import user as user_crud

# Override DATABASE_URL to use local database file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fmea.db")
if DATABASE_URL.startswith("sqlite:////app"):
    # Use local database file instead
    DATABASE_URL = "sqlite:///./fmea.db"

from sqlalchemy.orm import sessionmaker
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure database is initialized
Base.metadata.create_all(bind=engine)

def set_admin_by_email(email: str, create_if_missing: bool = True) -> bool:
    """Set user role to admin by email address. Creates user if missing."""
    db: Session = SessionLocal()
    try:
        user = user_crud.get_user_by_email(db, email)
        
        if not user:
            if not create_if_missing:
                print(f"❌ User with email '{email}' not found in database.")
                return False
            
            # Create user with admin role
            print(f"ℹ️  User '{email}' not found. Creating user with admin role...")
            from auth.security import get_password_hash
            from datetime import datetime, timezone
            
            # Generate a default username from email
            username = email.split("@")[0]
            # Ensure username is unique
            existing_user = user_crud.get_user_by_username(db, username)
            if existing_user:
                username = f"{username}_{email.split('@')[1].split('.')[0]}"
            
            # Create user with admin role
            new_user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash("TempPassword123!"),  # User should change this
                full_name=email.split("@")[0].replace(".", " ").title(),
                role="admin",
                is_active=True,
                is_verified=True,
                created_at=datetime.now(timezone.utc)
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"✅ Successfully created user with admin rights: {email}")
            print(f"   User ID: {new_user.id}")
            print(f"   Username: {new_user.username}")
            print(f"   Full Name: {new_user.full_name}")
            print(f"   Role: {new_user.role}")
            print(f"   ⚠️  Default password: TempPassword123! (user should change this)")
            return True
        
        # Check current role
        if user.role == "admin":
            print(f"✅ User '{email}' already has admin role.")
            print(f"   User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Full Name: {user.full_name or 'N/A'}")
            return True
        
        # Update role to admin
        success = user_crud.change_user_role(db, user.id, "admin")
        if success:
            print(f"✅ Successfully granted admin rights to user: {email}")
            print(f"   User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Full Name: {user.full_name or 'N/A'}")
            print(f"   Role changed from '{user.role}' to 'admin'")
            return True
        else:
            print(f"❌ Failed to update user role.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_admin_user.py <email>")
        print("Example: python set_admin_user.py john@fotonconsulting.com")
        sys.exit(1)
    
    email = sys.argv[1]
    success = set_admin_by_email(email)
    sys.exit(0 if success else 1)

