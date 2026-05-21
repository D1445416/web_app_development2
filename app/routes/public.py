from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.registration import Registration

# 定義前台 Blueprint
public_bp = Blueprint('public', __name__)

@public_bp.route('/', methods=['GET'])
def index():
    """
    顯示活動報名表單頁面。
    若有先前驗證失敗或重新整理帶來的參數，將傳入模板以保留使用者已填寫的內容。
    """
    return render_template(
        'index.html',
        name='',
        status='',
        needs_lunchbox='',
        dietary_preference='',
        notes=''
    )

@public_bp.route('/', methods=['POST'])
def submit_registration():
    """
    接收報名表單資料並執行驗證。
    
    1. 驗證 name 與 status 是否必填。
    2. 驗證條件邏輯 (若 status='是'，needs_lunchbox 必填; 若 needs_lunchbox='是'，dietary_preference 必填)。
    3. 驗證成功：呼叫 Registration.create 寫入資料庫，並 302 重導向至 success 頁面。
    4. 驗證失敗：將錯誤訊息寫入 flash 並重新渲染 index.html，保留已填寫內容。
    """
    name = request.form.get('name', '').strip()
    status = request.form.get('status', '').strip()
    needs_lunchbox = request.form.get('needs_lunchbox', '').strip()
    dietary_preference = request.form.get('dietary_preference', '').strip()
    notes = request.form.get('notes', '').strip()

    errors = []
    
    # 基礎必填驗證
    if not name:
        errors.append("請輸入姓名。")
    if not status:
        errors.append("請選擇是否參加。")
    elif status not in ('是', '否'):
        errors.append("出席意願選項無效。")

    # 出席時的餐盒邏輯驗證
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
            # 確保有需要餐盒時，偏好被正常設定；反之設為 None
        else:
            dietary_preference = None
    else:
        # 不出席時，不需要餐盒與葷素選擇
        needs_lunchbox = None
        dietary_preference = None

    if errors:
        for error in errors:
            flash(error, 'danger')
        # 重新渲染並帶回使用者剛才填寫的內容
        return render_template(
            'index.html',
            name=name,
            status=status,
            needs_lunchbox=needs_lunchbox or '',
            dietary_preference=dietary_preference or '',
            notes=notes
        )

    # 寫入資料庫
    registration_id = Registration.create(
        name=name,
        status=status,
        needs_lunchbox=needs_lunchbox,
        dietary_preference=dietary_preference,
        notes=notes
    )

    if registration_id:
        flash("報名成功！感謝您的參與。", "success")
        return redirect(url_for('public.success', id=registration_id))
    else:
        flash("報名失敗，伺服器資料庫寫入異常，請稍後再試。", "danger")
        return render_template(
            'index.html',
            name=name,
            status=status,
            needs_lunchbox=needs_lunchbox or '',
            dietary_preference=dietary_preference or '',
            notes=notes
        )

@public_bp.route('/success', methods=['GET'])
def success():
    """
    顯示報名成功確認頁面。
    
    1. 取得 URL 查詢參數中的 id。
    2. 呼叫 Registration.get_by_id 查詢紀錄。
    3. 若存在，渲染 success.html 並呈現報名摘要。
    4. 若不存在，重導向至 index 首頁。
    """
    registration_id = request.args.get('id', type=int)
    if not registration_id:
        flash("未提供有效的報名 ID。", "warning")
        return redirect(url_for('public.index'))

    registration = Registration.get_by_id(registration_id)
    if not registration:
        flash("找不到該筆報名紀錄。", "danger")
        return redirect(url_for('public.index'))

    return render_template('success.html', registration=registration)
