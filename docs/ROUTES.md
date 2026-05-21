# 活動報名系統 — 路由與頁面設計文件

> **版本**：v1.0  
> **建立日期**：2026-05-21  
> **對應文件**：[PRD.md](file:///c:/Users/User/web_app_development2/docs/PRD.md)、[FLOWCHART.md](file:///c:/Users/User/web_app_development2/docs/FLOWCHART.md)、[DB_DESIGN.md](file:///c:/Users/User/web_app_development2/docs/DB_DESIGN.md)、[ARCHITECTURE.md](file:///c:/Users/User/web_app_development2/docs/ARCHITECTURE.md)  

---

本文件規劃了「活動報名系統」的所有 Web 路由（Routes），包括前台報名、後台管理、登入驗證、資料編輯、刪除以及 CSV 匯出功能。

## 1. 路由總覽表格

本專案使用 Flask Blueprint 分為 **前台模組（Public）** 與 **後台模組（Admin）**。

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| **前台報名首頁** | `GET` | `/` | `templates/index.html` | 顯示活動報名表單頁面 |
| **提交報名表單** | `POST` | `/` | — | 接收報名資料，驗證並寫入 DB，成功後重導向 |
| **報名成功回饋** | `GET` | `/success` | `templates/success.html` | 顯示報名成功訊息與填寫的摘要資訊 |
| **管理者登入頁** | `GET` | `/admin/login` | `templates/admin/login.html` | 顯示管理者登入介面 |
| **執行管理者登入** | `POST` | `/admin/login` | — | 驗證帳密，成功則設定 Session，失敗留在登入頁 |
| **執行管理者登出** | `GET` / `POST` | `/admin/logout` | — | 清除 Session，重導向至登入頁 |
| **後台資料總覽** | `GET` | `/admin/dashboard` | `templates/admin/dashboard.html`| 顯示所有報名紀錄與統計數據（需登入） |
| **編輯報名資料頁**| `GET` | `/admin/edit/<int:id>` | `templates/admin/edit.html` | 顯示特定 ID 報名紀錄的編輯表單（需登入） |
| **送出編輯資料** | `POST` | `/admin/edit/<int:id>` | — | 接收並更新修改後的報名資料，重導向（需登入） |
| **刪除報名資料** | `POST` | `/admin/delete/<int:id>`| — | 刪除特定 ID 報名紀錄，重導向（需登入） |
| **匯出 CSV 檔案** | `GET` | `/admin/export` | — | 產生並下載 CSV 格式的報名資料檔案（需登入） |

---

## 2. 每個路由的詳細說明

### 2.1 前台模組（Public Blueprint）

#### 1. 顯示報名表單
- **URL**: `/`
- **Method**: `GET`
- **輸入**: 無
- **處理邏輯**: 載入並渲染報名頁面。前端 JS（`form.js`）負責依「是否參加」及「是否需要餐盒」來動態顯示/隱藏相關欄位。
- **輸出**: 渲染 `templates/index.html`。
- **錯誤處理**: 伺服器端錯誤（500）顯示預設錯誤頁面。

#### 2. 提交報名資料
- **URL**: `/`
- **Method**: `POST`
- **輸入**: 
  - 表單欄位：`name` (必填)、`status` (必填)、`needs_lunchbox` (選填)、`dietary_preference` (選填)、`notes` (選填)
- **處理邏輯**: 
  1. 驗證 `name` 與 `status` 是否為空。
  2. 驗證條件邏輯：若 `status` 為 `'是'`，`needs_lunchbox` 必須填寫；若 `needs_lunchbox` 為 `'是'`，`dietary_preference` 必須填寫。
  3. 呼叫 [Registration.create](file:///c:/Users/User/web_app_development2/app/models/registration.py) 寫入資料庫。
- **輸出**: 
  - 成功：302 重導向至 `/success?id=<new_id>`
  - 驗證失敗：重新渲染 `templates/index.html`，帶入錯誤訊息與已填寫資料。
- **錯誤處理**: 
  - 資料庫寫入異常時，顯示錯誤訊息並重新渲染首頁表單。

#### 3. 顯示報名成功頁
- **URL**: `/success`
- **Method**: `GET`
- **輸入**: URL 查詢參數 `id`
- **處理邏輯**: 
  1. 呼叫 [Registration.get_by_id(id)](file:///c:/Users/User/web_app_development2/app/models/registration.py) 查詢報名紀錄。
- **輸出**: 
  - 成功：渲染 `templates/success.html`，顯示該報名者的資料摘要（姓名、出席狀況、餐飲偏好）。
  - 找不到紀錄：重導向回首頁 `/`。
- **錯誤處理**: 
  - 若 `id` 參數不存在或無效，重導向回首頁 `/`。

---

### 2.2 後台模組（Admin Blueprint）

*註：以下除登入外，所有路由皆須具備 `login_required` 權限驗證。未登入者皆重導向至 `/admin/login`。*

#### 1. 管理者登入頁面
- **URL**: `/admin/login`
- **Method**: `GET`
- **輸入**: 無
- **處理邏輯**: 若已登入則直接導向至 `/admin/dashboard`；若未登入則顯示登入頁面。
- **輸出**: 渲染 `templates/admin/login.html`。

#### 2. 執行管理者登入
- **URL**: `/admin/login`
- **Method**: `POST`
- **輸入**: 
  - 表單欄位：`username` (必填)、`password` (必填)
- **處理邏輯**: 
  1. 呼叫 [User.verify_user(username, password)](file:///c:/Users/User/web_app_development2/app/models/user.py) 驗證帳密。
  2. 若驗證成功，將 `admin_logged_in = True` 與 `username` 寫入 `session`。
- **輸出**: 
  - 成功：302 重導向至 `/admin/dashboard`
  - 失敗：重新渲染 `templates/admin/login.html`，顯示「帳號或密碼錯誤」提示。

#### 3. 執行管理者登出
- **URL**: `/admin/logout`
- **Method**: `GET` / `POST`
- **輸入**: 無
- **處理邏輯**: 清除 `session` 中的管理者登入狀態。
- **輸出**: 302 重導向至 `/admin/login`。

#### 4. 後台資料總覽
- **URL**: `/admin/dashboard`
- **Method**: `GET`
- **輸入**: 無
- **處理邏輯**: 
  1. 呼叫 [Registration.get_all()](file:///c:/Users/User/web_app_development2/app/models/registration.py) 取得所有報名列表。
  2. 呼叫 [Registration.get_stats()](file:///c:/Users/User/web_app_development2/app/models/registration.py) 取得統計數據（總數、出席數、餐盒數、葷/素比例）。
- **輸出**: 渲染 `templates/admin/dashboard.html`，將報名列表與統計數據帶入頁面展示。

#### 5. 編輯報名資料頁面
- **URL**: `/admin/edit/<int:id>`
- **Method**: `GET`
- **輸入**: URL 路徑參數 `id`
- **處理邏輯**: 
  1. 呼叫 [Registration.get_by_id(id)](file:///c:/Users/User/web_app_development2/app/models/registration.py) 取得該報名紀錄。
- **輸出**: 
  - 成功：渲染 `templates/admin/edit.html`，並將舊資料帶入表單。
  - 失敗 (404)：若查無此 ID，回傳 404 錯誤頁面。

#### 6. 提交編輯報名資料
- **URL**: `/admin/edit/<int:id>`
- **Method**: `POST`
- **輸入**: 
  - URL 路徑參數 `id`
  - 表單欄位：`name`、`status`、`needs_lunchbox`、`dietary_preference`、`notes`
- **處理邏輯**: 
  1. 驗證欄位合法性（與前台提交之條件邏輯相同）。
  2. 呼叫 [Registration.update(id, ...)](file:///c:/Users/User/web_app_development2/app/models/registration.py) 更新資料庫。
- **輸出**: 
  - 成功：302 重導向至 `/admin/dashboard`
  - 驗證失敗：重新渲染 `templates/admin/edit.html`，並顯示錯誤訊息。

#### 7. 刪除報名資料
- **URL**: `/admin/delete/<int:id>`
- **Method**: `POST`
- **輸入**: URL 路徑參數 `id`
- **處理邏輯**: 
  1. 呼叫 [Registration.delete(id)](file:///c:/Users/User/web_app_development2/app/models/registration.py) 進行刪除。
- **輸出**: 302 重導向至 `/admin/dashboard`。
- **錯誤處理**: 若刪除失敗，於總覽頁顯示錯誤提示。

#### 8. 匯出 CSV 檔案
- **URL**: `/admin/export`
- **Method**: `GET`
- **輸入**: 無
- **處理邏輯**: 
  1. 呼叫 [Registration.get_all()](file:///c:/Users/User/web_app_development2/app/models/registration.py) 取得所有報名紀錄。
  2. 透過 Python `csv` 模組將資料寫入記憶體中的 StringIO 物件。
  3. 設定 Response 的 Content-Type 為 `text/csv` 並帶有 `Content-Disposition: attachment; filename=registrations.csv`。
- **輸出**: 提供 CSV 檔案下載。

---

## 3. Jinja2 模板清單

所有模板皆置於 `app/templates/` 中。

1. **[base.html](file:///c:/Users/User/web_app_development2/app/templates/base.html)** (基底模板)
   - 包含 `<head>`（全站 RWD Meta、CSS 引用、Google Fonts 引用）、全站導覽列（一般與後台切換）及頁尾 Footer。
   - 提供 `{% block content %}` 與 `{% block extra_js %}` 供子模板繼承。
2. **[index.html](file:///c:/Users/User/web_app_development2/app/templates/index.html)** (報名表單頁)
   - 繼承自 `base.html`。
   - 呈現報名表單，並引入 `form.js` 以控制欄位條件顯示與即時錯誤提示。
3. **[success.html](file:///c:/Users/User/web_app_development2/app/templates/success.html)** (報名成功確認頁)
   - 繼承自 `base.html`。
   - 顯示成功 Tick 動畫與已提交的姓名、出席意願、餐偏好摘要。
4. **[admin/login.html](file:///c:/Users/User/web_app_development2/app/templates/admin/login.html)** (管理者登入頁)
   - 繼承自 `base.html`。
   - 提供管理者帳號密碼登入表單，具備錯誤訊息欄位。
5. **[admin/dashboard.html](file:///c:/Users/User/web_app_development2/app/templates/admin/dashboard.html)** (後台總覽頁)
   - 繼承自 `base.html`。
   - 上方以區塊卡片（Card）呈現統計數字與視覺化比例。
   - 下方為報名明細表格，包含 RWD 捲軸、刪除確認 Dialog 與編輯、匯出按鈕。
6. **[admin/edit.html](file:///c:/Users/User/web_app_development2/app/templates/admin/edit.html)** (編輯報名資料頁)
   - 繼承自 `base.html`。
   - 顯示帶有舊資料的編輯表單，共用 `form.js` 的條件控制邏輯。
