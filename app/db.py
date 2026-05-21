import sqlite3
import os
import click
from flask import g, current_app
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        # 取得資料庫路徑，預設在 instance/database.db
        db_path = current_app.config.get('DATABASE')
        if not db_path:
            # 如果沒有設定，則使用預設路徑
            db_path = os.path.join(current_app.instance_path, 'database.db')
            
        # 確保 instance 資料夾存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """清除現有資料並建立新資料表。"""
    db = get_db()
    
    # 讀取 schema.sql 檔案
    schema_path = os.path.join(
        current_app.root_path, '..', 'database', 'schema.sql'
    )
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
        
    click.echo('已成功初始化資料庫。')

def init_app(app):
    """註冊資料庫連線的清理函式與 CLI 指令。"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
