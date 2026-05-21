from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.registration import Registration

# 定義前台 Blueprint
public_bp = Blueprint('public', __name__)

@public_bp.route('/', methods=['GET'])
def index():
    """
    顯示活動報名表單頁面。
    如果使用者有先前提交失敗的暫存資料或錯誤訊息，會經由 flash 或變數帶入模板中。
    """
    pass

@public_bp.route('/', methods=['POST'])
def submit_registration():
    """
    接收報名表單資料。
    
    1. 驗證 name 與 status 是否必填。
    2. 驗證條件邏輯 (若 status='是'，needs_lunchbox 必填; 若 needs_lunchbox='是'，dietary_preference 必填)。
    3. 驗證成功：呼叫 Registration.create 寫入資料庫，並 302 重導向至 success 頁面。
    4. 驗證失敗：將錯誤訊息與已填寫資料傳回 index 頁面進行錯誤提示。
    """
    pass

@public_bp.route('/success', methods=['GET'])
def success():
    """
    顯示報名成功確認頁面。
    
    1. 取得 URL 查詢參數中的 id。
    2. 呼叫 Registration.get_by_id 查詢紀錄。
    3. 若存在，渲染 success.html 並呈現報名摘要。
    4. 若不存在，重導向至 index 首頁。
    """
    pass
