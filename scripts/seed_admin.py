from app.auth.auth_service import AuthService
from app.dependencies.connection import get_db_connection


def main():
    db = get_db_connection()
    auth_service = AuthService(db)

    username = "admin"
    password = "change_me1234"

    existing = auth_service.users_repo.get_by_username(username)
    if existing:
        print(f"User '{username}' already exists. No action taken.")
        return

    password_hash = auth_service.hash_password(password)
    user_id = auth_service.users_repo.insert_one(username, password_hash)
    print(f"Created admin user '{username}' with ID {user_id}")
    print("Remember to change the password before deploying!")


if __name__ == "__main__":
    main()
