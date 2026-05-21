import os
from flask import Flask

def create_app(test_config=None):
    """建立並設定 Flask 應用程式的 App Factory。"""
    # 建立 Flask 實例，啟用相對於實例資料夾的設定
    app = Flask(__name__, instance_relative_config=True)
    
    # 預設設定
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )

    if test_config is None:
        # 如果存在 config.py，從中載入設定
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 載入測試設定
        app.config.from_mapping(test_config)

    # 確保實例資料夾存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化資料庫連線與 CLI 指令
    from app import db
    db.init_app(app)

    # 註冊 Blueprints
    from app.routes import public_bp, admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    return app
