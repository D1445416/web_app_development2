from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response
from app.models.registration import Registration
from app.models.user import User

# 定義後台 Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def login_required(f):
    """
    檢查管理者登入狀態的裝飾器。
    若 session['admin_logged_in'] 未設定，則重導向至 /admin/login。
    """
    pass

@admin_bp.route('/login', methods=['GET'])
def login():
    """
    顯示管理者登入頁面。
    若管理者已處於登入狀態，則直接重導向至 /admin/dashboard。
    """
    pass

@admin_bp.route('/login', methods=['POST'])
def do_login():
    """
    執行管理者登入驗證。
    
    1. 接收表單 username 與 password。
    2. 呼叫 User.verify_user 驗證帳密。
    3. 成功：在 session 中設定 admin_logged_in=True 與 username，重導向至 /admin/dashboard。
    4. 失敗：將錯誤訊息寫入 flash 並重新渲染 login 頁面。
    """
    pass

@admin_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    執行管理者登出。
    清除 session 中的登入狀態資訊，重導向至 /admin/login。
    """
    pass

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    顯示後台管理總覽頁面。
    此路由受 login_required 保護。
    
    1. 呼叫 Registration.get_all 取得所有報名列表。
    2. 呼叫 Registration.get_stats 取得統計資訊。
    3. 渲染 admin/dashboard.html 並帶入數據。
    """
    pass

@admin_bp.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit(id):
    """
    顯示編輯特定報名紀錄的表單頁面。
    此路由受 login_required 保護。
    
    1. 呼叫 Registration.get_by_id 取得舊資料。
    2. 若查無資料，回傳 404 錯誤。
    3. 若成功，渲染 admin/edit.html 並填入舊資料。
    """
    pass

@admin_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def do_edit(id):
    """
    執行特定報名紀錄的更新。
    此路由受 login_required 保護。
    
    1. 驗證修改後的表單資料。
    2. 呼叫 Registration.update 更新 DB。
    3. 成功：重導向至 /admin/dashboard。
    4. 失敗：重新渲染 admin/edit.html 並顯示錯誤。
    """
    pass

@admin_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """
    刪除指定的報名紀錄。
    此路由受 login_required 保護。
    
    1. 呼叫 Registration.delete 進行刪除。
    2. 刪除完成後，302 重導向回 /admin/dashboard。
    """
    pass

@admin_bp.route('/export', methods=['GET'])
@login_required
def export_csv():
    """
    將所有報名紀錄匯出為 CSV 檔案下載。
    此路由受 login_required 保護。
    
    1. 呼叫 Registration.get_all 取得所有報名紀錄。
    2. 產生 CSV 格式的檔案內容，加入 BOM 標頭防止中文亂碼。
    3. 以 Response 回傳，Content-Disposition 設為附件下載。
    """
    pass
