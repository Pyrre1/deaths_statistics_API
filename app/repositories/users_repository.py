from app.repositories.base_repository import BaseRepository


class UsersRepository(BaseRepository):
    """Repository for user database operations."""

    def get_by_username(self, username: str):
        """Fetch a user by username."""
        return self.fetch_one(
            "SELECT * FROM users WHERE username = %s AND is_active = TRUE;",
            (username,),
        )

    def get_by_id(self, user_id: int):
        """Fetch a user by ID."""
        return self.fetch_one(
            "SELECT * FROM users WHERE id = %s AND is_active = TRUE;",
            (user_id,),
        )

    def insert_one(self, username: str, password_hash: str) -> int:
        """Insert a new user and return the new user's ID"""
        result = self.fetch_one_write(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            RETURNING id;
            """,
            (username, password_hash),
        )
        return result["id"]

    def delete_by_id(self, user_id: int) -> None:
        """Delete a user by ID (used for account deletion)"""
        self.execute(
            "DELETE FROM users WHERE id = %s;",
            (user_id,),
        )


class RefreshTokenRepository(BaseRepository):
    """Repository for refresh token database operations"""

    def save_token(self, user_id: int, token_hash: str, expires_at) -> None:
        """Store a hashed refresh token"""
        self.execute(
            """
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES (%s, %s, %s);
            """,
            (user_id, token_hash, expires_at),
        )

    def get_by_hash(self, token_hash: str):
        """Fetch a refresh token by its hash"""
        return self.fetch_one(
            """
            SELECT refresh_tokens.*, users.username
            FROM refresh_tokens
            JOIN users ON refresh_tokens.user_id = users.id
            WHERE refresh_tokens.token_hash = %s
            AND refresh_tokens.expires_at > NOW()
            AND users.is_active = TRUE;
            """,
            (token_hash,),
        )

    def delete_by_hash(self, token_hash: str) -> None:
        """Delete a refresh token - used on logout or rotation"""
        self.execute(
            "DELETE FROM refresh_tokens WHERE token_hash = %s;",
            (token_hash,),
        )

    def delete_by_user_id(self, user_id: int) -> None:
        """Delete all refresh tokens for a user - used on account deletion"""
        self.execute(
            "DELETE FROM refresh_tokens WHERE user_id = %s;",
            (user_id,),
        )
