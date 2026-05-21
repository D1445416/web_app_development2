import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db

class User:
    def __init__(self, id, username, password_hash, created_at):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            created_at=row['created_at']
        )

    @staticmethod
    def create(username, password):
        """
        建立新的管理者帳號，密碼會經由 Werkzeug 進行雜湊加密。
        """
        db = get_db()
        cursor = db.cursor()
        password_hash = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            db.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # 帳號重複
            return None

    @staticmethod
    def get_by_username(username):
        """
        依帳號查詢管理者。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return User.from_row(row)

    @staticmethod
    def verify_user(username, password):
        """
        驗證使用者帳號密碼是否正確，通過則回傳 User 物件。
        """
        user = User.get_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    @staticmethod
    def get_by_id(user_id):
        """
        根據 ID 查詢管理者。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return User.from_row(row)

    @staticmethod
    def update_password(user_id, new_password):
        """
        更新管理者密碼（重新進行雜湊加密）。
        """
        db = get_db()
        cursor = db.cursor()
        new_hash = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_hash, user_id)
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def delete(user_id):
        """
        刪除指定 ID 的管理者。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        return cursor.rowcount > 0
