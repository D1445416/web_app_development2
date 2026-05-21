import sqlite3
from app.db import get_db

class Registration:
    def __init__(self, id, name, status, needs_lunchbox, dietary_preference, notes, created_at, updated_at):
        self.id = id
        self.name = name
        self.status = status
        self.needs_lunchbox = needs_lunchbox
        self.dietary_preference = dietary_preference
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Registration(
            id=row['id'],
            name=row['name'],
            status=row['status'],
            needs_lunchbox=row['needs_lunchbox'],
            dietary_preference=row['dietary_preference'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    @staticmethod
    def create(name, status, needs_lunchbox=None, dietary_preference=None, notes=None):
        """
        建立新的報名紀錄。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO registrations (name, status, needs_lunchbox, dietary_preference, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, status, needs_lunchbox, dietary_preference, notes)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all():
        """
        取得所有報名紀錄，依提交時間排序（新到舊）。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM registrations ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [Registration.from_row(row) for row in rows]

    @staticmethod
    def get_by_id(registration_id):
        """
        根據 ID 查詢特定報名紀錄。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM registrations WHERE id = ?", (registration_id,))
        row = cursor.fetchone()
        return Registration.from_row(row)

    @staticmethod
    def update(registration_id, name, status, needs_lunchbox=None, dietary_preference=None, notes=None):
        """
        修改指定 ID 的報名紀錄，並更新 updated_at 時間。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE registrations
            SET name = ?, status = ?, needs_lunchbox = ?, dietary_preference = ?, notes = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (name, status, needs_lunchbox, dietary_preference, notes, registration_id)
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def delete(registration_id):
        """
        刪除特定 ID 的報名紀錄。
        """
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM registrations WHERE id = ?", (registration_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def get_stats():
        """
        取得報名統計數據：
        - total_count: 總報名筆數
        - attend_count: 參加人數
        - lunchbox_count: 需要餐盒數
        - meat_count: 葷食人數
        - veg_count: 素食人數
        """
        db = get_db()
        cursor = db.cursor()
        
        # 總報名筆數
        cursor.execute("SELECT COUNT(*) FROM registrations")
        total_count = cursor.fetchone()[0]
        
        # 參加人數
        cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = '是'")
        attend_count = cursor.fetchone()[0]
        
        # 需要餐盒數
        cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = '是' AND needs_lunchbox = '是'")
        lunchbox_count = cursor.fetchone()[0]
        
        # 葷食人數
        cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = '是' AND needs_lunchbox = '是' AND dietary_preference = '葷'")
        meat_count = cursor.fetchone()[0]
        
        # 素食人數
        cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = '是' AND needs_lunchbox = '是' AND dietary_preference = '素'")
        veg_count = cursor.fetchone()[0]
        
        return {
            'total_count': total_count,
            'attend_count': attend_count,
            'lunchbox_count': lunchbox_count,
            'meat_count': meat_count,
            'veg_count': veg_count
        }
