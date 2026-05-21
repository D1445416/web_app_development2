import sqlite3
from app.db import get_db

class Registration:
    def __init__(self, id, name, status, needs_lunchbox, dietary_preference, notes, created_at, updated_at):
        """
        初始化報名紀錄實例。
        """
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
        """
        將 SQLite Row 物件轉換成 Registration 實例。
        """
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
        
        參數:
            name (str): 報名者姓名
            status (str): 出席意願 ('是' 或 '否')
            needs_lunchbox (str, optional): 是否需要餐盒 ('是' 或 '否')
            dietary_preference (str, optional): 葷素偏好 ('葷' 或 '素')
            notes (str, optional): 備註說明
            
        回傳:
            int: 新增紀錄的 ID，若失敗則回傳 None
        """
        try:
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
        except sqlite3.Error as e:
            print(f"Database error in Registration.create: {e}")
            return None

    @staticmethod
    def get_all():
        """
        取得所有報名紀錄，依提交時間排序（新到舊）。
        
        回傳:
            list[Registration]: 報名紀錄列表，若失敗則回傳空列表
        """
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM registrations ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [Registration.from_row(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Database error in Registration.get_all: {e}")
            return []

    @staticmethod
    def get_by_id(registration_id):
        """
        根據 ID 查詢特定報名紀錄。
        
        參數:
            registration_id (int): 報名紀錄 ID
            
        回傳:
            Registration: 報名紀錄物件，若查無資料或發生錯誤則回傳 None
        """
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM registrations WHERE id = ?", (registration_id,))
            row = cursor.fetchone()
            return Registration.from_row(row)
        except sqlite3.Error as e:
            print(f"Database error in Registration.get_by_id: {e}")
            return None

    @staticmethod
    def update(registration_id, name, status, needs_lunchbox=None, dietary_preference=None, notes=None):
        """
        修改指定 ID 的報名紀錄，並更新 updated_at 時間。
        
        參數:
            registration_id (int): 報名紀錄 ID
            name (str): 報名者姓名
            status (str): 出席意願 ('是' 或 '否')
            needs_lunchbox (str, optional): 是否需要餐盒 ('是' 或 '否')
            dietary_preference (str, optional): 葷素偏好 ('葷' 或 '素')
            notes (str, optional): 備註說明
            
        回傳:
            bool: 是否更新成功 (True/False)
        """
        try:
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
        except sqlite3.Error as e:
            print(f"Database error in Registration.update: {e}")
            return False

    @staticmethod
    def delete(registration_id):
        """
        刪除特定 ID 的報名紀錄。
        
        參數:
            registration_id (int): 報名紀錄 ID
            
        回傳:
            bool: 是否刪除成功 (True/False)
        """
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM registrations WHERE id = ?", (registration_id,))
            db.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error in Registration.delete: {e}")
            return False

    @staticmethod
    def get_stats():
        """
        取得報名統計數據，包括：
        - total_count: 總報名筆數
        - attend_count: 參加人數
        - lunchbox_count: 需要餐盒數
        - meat_count: 葷食人數
        - veg_count: 素食人數
        
        回傳:
            dict: 統計數據字典，若發生錯誤則回傳全 0 的預設字典
        """
        try:
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
            cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = '是' AND needs_lunchbox = '存' OR (status = '是' AND needs_lunchbox = '是' AND dietary_preference = '素')")
            # 修正上方的 SQL 條件，應與原先一致：
            cursor.execute("SELECT COUNT(*) FROM registrations WHERE status = '是' AND needs_lunchbox = '是' AND dietary_preference = '素'")
            veg_count = cursor.fetchone()[0]
            
            return {
                'total_count': total_count,
                'attend_count': attend_count,
                'lunchbox_count': lunchbox_count,
                'meat_count': meat_count,
                'veg_count': veg_count
            }
        except sqlite3.Error as e:
            print(f"Database error in Registration.get_stats: {e}")
            return {
                'total_count': 0,
                'attend_count': 0,
                'lunchbox_count': 0,
                'meat_count': 0,
                'veg_count': 0
            }
