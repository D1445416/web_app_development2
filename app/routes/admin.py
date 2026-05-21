import csv
import io
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response, make_response, abort
from app.models.registration import Registration
from app.models.user import User

# 定義後台 Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def login_required(f):
    """
    檢查管理者登入狀態的裝飾器。
    若 session['admin_logged_in'] 未設定，則重導向至 /admin/login。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("請先登入系統以存取管理後台。", "danger")
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET'])
def login():
    """
    顯示管理者登入頁面。
    若管理者已處於登入狀態，則直接重導向至 /admin/dashboard。
    """
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/login.html', username='')

@admin_bp.route('/login', methods=['POST'])
def do_login():
    """
    執行管理者登入驗證。
    
    1. 接收表單 username 與 password。
    2. 呼叫 User.verify_user 驗證帳密。
    3. 成功：在 session 中設定 admin_logged_in=True 與 username，重導向至 /admin/dashboard。
    4. 失敗：將錯誤訊息寫入 flash 並重新渲染 login 頁面。
    """
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        flash("請輸入帳號與密碼。", "danger")
        return render_template('admin/login.html', username=username)

    user = User.verify_user(username, password)
    if user:
        session['admin_logged_in'] = True
        session['username'] = user.username
        flash(f"登入成功！歡迎回來，{user.username}。", "success")
        return redirect(url_for('admin.dashboard'))
    else:
        flash("帳號或密碼錯誤，請重新輸入。", "danger")
        return render_template('admin/login.html', username=username)

@admin_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    執行管理者登出。
    清除 session 中的登入狀態資訊，重導向至 /admin/login。
    """
    session.pop('admin_logged_in', None)
    session.pop('username', None)
    flash("您已安全登出系統。", "success")
    return redirect(url_for('admin.login'))

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
    registrations = Registration.get_all()
    stats = Registration.get_stats()
    return render_template('admin/dashboard.html', registrations=registrations, stats=stats)

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
    registration = Registration.get_by_id(id)
    if not registration:
        abort(404)
    return render_template('admin/edit.html', registration=registration)

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
    registration = Registration.get_by_id(id)
    if not registration:
        abort(404)

    name = request.form.get('name', '').strip()
    status = request.form.get('status', '').strip()
    needs_lunchbox = request.form.get('needs_lunchbox', '').strip()
    dietary_preference = request.form.get('dietary_preference', '').strip()
    notes = request.form.get('notes', '').strip()

    errors = []
    if not name:
        errors.append("姓名不可為空。")
    if not status:
        errors.append("請選擇出席意願。")
    elif status not in ('是', '否'):
        errors.append("出席意願選項無效。")

    if status == '是':
        if not needs_lunchbox:
            errors.append("請選擇是否需要餐盒。")
        elif needs_lunchbox not in ('是', '否'):
            errors.append("餐盒需求選項無效。")
        elif needs_lunchbox == '是':
            if not dietary_preference:
                errors.append("請選擇葷食或素食。")
            elif dietary_preference not in ('葷', '素'):
                errors.append("葷素偏好選項無效。")
        else:
            dietary_preference = None
    else:
        needs_lunchbox = None
        dietary_preference = None

    if errors:
        for error in errors:
            flash(error, 'danger')
        # 重新建構一個臨時的 registration 物件用來顯示於編輯表單中，保留已填寫內容
        temp_registration = Registration(
            id=id,
            name=name,
            status=status,
            needs_lunchbox=needs_lunchbox,
            dietary_preference=dietary_preference,
            notes=notes,
            created_at=registration.created_at,
            updated_at=registration.updated_at
        )
        return render_template('admin/edit.html', registration=temp_registration)

    success = Registration.update(
        registration_id=id,
        name=name,
        status=status,
        needs_lunchbox=needs_lunchbox,
        dietary_preference=dietary_preference,
        notes=notes
    )

    if success:
        flash(f"已成功更新 {name} 的報名紀錄。", "success")
        return redirect(url_for('admin.dashboard'))
    else:
        flash("更新失敗，資料庫寫入異常。", "danger")
        return render_template('admin/edit.html', registration=registration)

@admin_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """
    刪除指定的報名紀錄。
    此路由受 login_required 保護。
    
    1. 呼叫 Registration.delete 進行刪除。
    2. 刪除完成後，302 重導向回 /admin/dashboard。
    """
    registration = Registration.get_by_id(id)
    if not registration:
        abort(404)
        
    success = Registration.delete(id)
    if success:
        flash(f"已成功刪除 {registration.name} 的報名紀錄。", "success")
    else:
        flash("刪除失敗，資料庫操作異常。", "danger")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/export', methods=['GET'])
@login_required
def export_csv():
    """
    將所有報名紀錄匯出為 CSV 檔案下載。
    此路由受 login_required 保護。
    
    1. 呼叫 Registration.get_all 取得所有報名紀錄。
    2. 產生 CSV 格式的檔案內容，加入 UTF-8 BOM 標頭防止 Excel 開啟時中文亂碼。
    3. 以 Response 回傳，Content-Disposition 設為附件下載。
    """
    registrations = Registration.get_all()
    
    # 建立記憶體中的 CSV 寫入器
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 寫入 CSV 標頭
    writer.writerow(['報名ID', '姓名', '出席狀態', '是否需要餐盒', '葷素選擇', '備註', '提交時間', '更新時間'])
    
    # 寫入資料行
    for reg in registrations:
        writer.writerow([
            reg.id,
            reg.name,
            reg.status,
            reg.needs_lunchbox if reg.needs_lunchbox else '—',
            reg.dietary_preference if reg.dietary_preference else '—',
            reg.notes if reg.notes else '—',
            reg.created_at,
            reg.updated_at
        ])
    
    # 取得 CSV 字串
    csv_data = output.getvalue()
    output.close()
    
    # 加上 UTF-8 BOM (\ufeff) 避免 Windows Excel 開啟時產生亂碼
    bom_csv_data = '\ufeff' + csv_data
    
    # 建立 Response 回傳
    response = make_response(bom_csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=registrations.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    
    return response
