"""
Script to update plain text passwords to hashed passwords in the database.
Run this script once after initial database setup.
"""

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash


def update_passwords():
    """Update all plain text passwords to hashed versions"""
    db = SessionLocal()

    try:
        # Get all users
        users = db.query(User).all()

        print(f"Found {len(users)} users in database")
        updated_count = 0

        for user in users:
            # Check if password is already hashed (bcrypt hashes are 60 chars)
            if len(user.pass_user) < 20:
                old_password = user.pass_user
                user.pass_user = get_password_hash(old_password)
                updated_count += 1
                print(f"✓ Updated password for user: {user.id_user}")
            else:
                print(f"- Password already hashed for user: {user.id_user}")

        db.commit()
        print(f"\n✓ Successfully updated {updated_count} passwords")
        print("All passwords are now securely hashed!")

    except Exception as e:
        print(f"✗ Error updating passwords: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=== Password Hash Update Script ===\n")
    update_passwords()
