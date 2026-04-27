"""
Usage:
    python make_admin.py user@example.com
    python make_admin.py user@example.com --revoke

Promotes (or revokes) admin access for the account with the given email.
"""
import sys

from website import create_app
from website.modles import User, db


def main():
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email> [--revoke]")
        sys.exit(1)

    email = sys.argv[1].strip()
    revoke = "--revoke" in sys.argv

    app = create_app()
    with app.app_context():
        user = User.query.filter(db.func.lower(User.email) == email.lower()).first()
        if not user:
            print(f"No account found with email: {email}")
            sys.exit(1)

        user.is_admin = not revoke
        db.session.commit()

        action = "revoked" if revoke else "granted"
        print(f"Admin access {action} for {user.email} (ID {user.id}).")


if __name__ == "__main__":
    main()
