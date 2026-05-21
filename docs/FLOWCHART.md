# 活動報名系統 — 流程圖設計文件

> **版本**：v1.0  
> **建立日期**：2026-05-21  
> **對應文件**：[PRD.md](file:///c:/Users/User/web_app_development2/docs/PRD.md)、[ARCHITECTURE.md](file:///c:/Users/User/web_app_development2/docs/ARCHITECTURE.md)  

---

本文件提供「活動報名系統」的流程圖與功能對照表，包含一般報名者與管理者的操作流程，以及前後端系統元件之間的資料流與處理程序。

## 1. 使用者流程圖（User Flow）

使用者流程圖描述了**一般用戶（報名者）**與**後台管理者**在系統中的操作路徑與邏輯分支。

```mermaid
flowchart LR
    A([使用者開啟網頁]) --> B{角色身分？}
    
    %% 一般用戶路徑
    B -->|一般用戶| C[前台首頁 / - 填寫報名表單]
    C --> D{是否選擇參加？}
    D -->|否| E[隱藏餐盒與葷素欄位] --> F[填寫姓名、備註並提交]
    D -->|是| G[顯示是否需要餐盒欄位] --> H{是否需要餐盒？}
    H -->|否| I[隱藏葷素欄位] --> F
    H -->|是| J[顯示並選擇葷素欄位] --> F
    
    F --> K{輸入資料驗證？}
    K -->|驗證失敗| L[頁面顯示錯誤提示] --> C
    K -->|驗證成功| M[提交表單 POST /]
    M --> N[重導向到成功頁 /success] --> O([顯示報名摘要與成功提示])
    
    %% 管理者路徑
    B -->|管理者| P[登入頁 /admin/login]
    P --> Q[輸入帳密並提交]
    Q --> R{驗證是否通過？}
    R -->|否| S[提示帳密錯誤] --> P
    R -->|是| T[登入成功，儲存 Session] --> U[後台總覽頁 /admin/dashboard]
    
    U --> V{要執行什麼操作？}
    
    %% 管理者操作：編輯
    V -->|編輯報名資料| W[編輯頁 /admin/edit/id]
    W --> X[修改欄位並送出]
    X --> Y{驗證是否通過？}
    Y -->|否| Z[編輯頁顯示錯誤提示] --> W
    Y -->|是| AA[更新資料庫] --> U
    
    %% 管理者操作：刪除
    V -->|刪除報名資料| AB[點擊刪除並確認]
    AB --> AC[送出刪除請求]
    AC --> AD[資料庫刪除紀錄] --> U
    
    %% 管理者操作：匯出 CSV
    V -->|匯出 CSV| AE[點擊匯出]
    AE --> AF[下載 CSV 檔案] --> U
    
    %% 管理者操作：登出
    V -->|登出| AG[點擊登出]
    AG --> AH[清除 Session] --> P
```

---

## 2. 系統序列圖（Sequence Diagram）

### 2.1 一般用戶：提交報名表單流程

此序列圖描述一般用戶填寫並提交表單，資料通過前端驗證、後端處理、Model 層寫入 SQLite 資料庫，最後跳轉至報名成功頁面的完整流程。

```mermaid
sequenceDiagram
    actor User as 一般用戶 (報名者)
    participant Browser as 瀏覽器 (Browser)
    participant Flask as Flask 路由 (routes/public.py)
    participant Model as Model (models/registration.py)
    participant DB as SQLite (database.db)

    User->>Browser: 填寫表單並點擊「送出報名」
    opt 瀏覽器前端驗證
        Browser->>Browser: 檢查必填欄位 (姓名、出席意願)
    end
    
    alt 前端驗證通過
        Browser->>Flask: POST / (提交表單資料)
        activate Flask
        
        Flask->>Flask: 後端資料格式與條件欄位驗證
        
        alt 後端驗證成功
            Flask->>Model: create_registration(data)
            activate Model
            Model->>DB: INSERT INTO registrations (...)
            activate DB
            DB-->>Model: 寫入成功，回傳新紀錄 ID
            deactivate DB
            Model-->>Flask: 回傳註冊紀錄 ID
            deactivate Model
            
            Flask-->>Browser: 302 Redirect to /success?id=ID
            deactivate Flask
            
            Browser->>Flask: GET /success?id=ID
            activate Flask
            Flask->>Model: get_registration_by_id(id)
            activate Model
            Model->>DB: SELECT * FROM registrations WHERE id = ?
            activate DB
            DB-->>Model: 回傳報名資料
            deactivate DB
            Model-->>Flask: 回傳資料物件/字典
            deactivate Model
            Flask->>Flask: 使用 templates/success.html 渲染頁面
            Flask-->>Browser: 200 OK (HTML 頁面與報名摘要)
            deactivate Flask
            Browser-->>User: 顯示報名成功頁面與摘要資訊
        else 後端驗證失敗
            Flask-->>Browser: 200 OK (重新渲染 index.html，顯示錯誤提示)
            Browser-->>User: 顯示錯誤提示，請重新填寫
        end
    else 前端驗證失敗
        Browser-->>User: 顯示瀏覽器內建必填提示
    end
```

### 2.2 管理者：登入與總覽後台流程

此序列圖描述管理者進行登入驗證、儲存會話（Session）狀態，並載入後台首頁進行數據統計與展現的完整過程。

```mermaid
sequenceDiagram
    actor Admin as 管理者
    participant Browser as 瀏覽器 (Browser)
    participant Flask as Flask 路由 (routes/admin.py)
    participant Model as Model (models/user.py)
    participant DB as SQLite (database.db)

    Admin->>Browser: 輸入帳號密碼並點擊「登入」
    Browser->>Flask: POST /admin/login (username, password)
    activate Flask
    Flask->>Model: verify_user(username, password)
    activate Model
    Model->>DB: SELECT password_hash FROM users WHERE username = ?
    activate DB
    DB-->>Model: 回傳密碼雜湊值
    deactivate DB
    Model->>Model: 使用 check_password_hash 比對密碼
    Model-->>Flask: 回傳驗證結果 (True/False)
    deactivate Model
    
    alt 驗證成功
        Flask->>Flask: 設定 session['admin_logged_in'] = True
        Flask-->>Browser: 302 Redirect to /admin/dashboard
        Browser->>Flask: GET /admin/dashboard
        Flask->>Flask: 檢查 session 狀態 (驗證通過)
        Flask->>Model: get_all_registrations()
        activate Model
        Model->>DB: SELECT * FROM registrations
        activate DB
        DB-->>Model: 回傳所有報名紀錄
        deactivate DB
        Model-->>Flask: 回傳紀錄列表
        deactivate Model
        Flask->>Flask: 統計報名數據 (參加人數、餐盒、葷素比例)
        Flask->>Flask: 使用 templates/admin/dashboard.html 渲染
        Flask-->>Browser: 200 OK (後台總覽頁)
        Browser-->>Admin: 顯示後台管理介面與統計數據
    else 驗證失敗
        Flask-->>Browser: 200 OK (重新渲染 login.html，顯示錯誤訊息)
        deactivate Flask
        Browser-->>Admin: 顯示「帳號或密碼錯誤」提示
    end
```

### 2.3 管理者：編輯報名資料流程

此序列圖描述管理者進入編輯頁面修改報名資料，並儲存更新至資料庫的流程。

```mermaid
sequenceDiagram
    actor Admin as 管理者
    participant Browser as 瀏覽器 (Browser)
    participant Flask as Flask 路由 (routes/admin.py)
    participant Model as Model (models/registration.py)
    participant DB as SQLite (database.db)

    Admin->>Browser: 於後台點擊「編輯」某筆紀錄 (ID = id)
    Browser->>Flask: GET /admin/edit/<id>
    activate Flask
    Flask->>Flask: 檢查登入狀態 (login_required)
    Flask->>Model: get_registration_by_id(id)
    activate Model
    Model->>DB: SELECT * FROM registrations WHERE id = ?
    activate DB
    DB-->>Model: 回傳報名詳細資料
    deactivate DB
    Model-->>Flask: 回傳資料物件/字典
    deactivate Model
    Flask->>Flask: 使用 templates/admin/edit.html 渲染
    Flask-->>Browser: 200 OK (編輯表單頁面)
    deactivate Flask
    Browser-->>Admin: 顯示已帶入舊資料的編輯表單

    Admin->>Browser: 修改資料並點擊「儲存修改」
    Browser->>Flask: POST /admin/edit/<id> (提交修改後資料)
    activate Flask
    Flask->>Flask: 檢查登入狀態 (login_required)
    Flask->>Flask: 後端驗證修改資料
    alt 驗證成功
        Flask->>Model: update_registration(id, data)
        activate Model
        Model->>DB: UPDATE registrations SET name=?, status=?, ... WHERE id=?
        activate DB
        DB-->>Model: 更新成功
        deactivate DB
        Model-->>Flask: 回傳成功
        deactivate Model
        Flask-->>Browser: 302 Redirect to /admin/dashboard
        deactivate Flask
        Browser->>Flask: GET /admin/dashboard
        activate Flask
        Note over Flask,DB: 重新讀取資料並渲染總覽頁面
        Flask-->>Browser: 200 OK (更新後的總覽頁面)
        deactivate Flask
        Browser-->>Admin: 顯示修改成功的資料列表
    else 驗證失敗
        Flask-->>Browser: 200 OK (重新渲染 edit.html，顯示錯誤提示)
        Browser-->>Admin: 顯示錯誤提示，保持在編輯頁
    end
```

---

## 3. 功能清單對照表

本表格列出系統目前規畫的所有功能、對應的 URL 路徑、HTTP 方法及存取權限。

| 功能名稱 | URL 路徑 | HTTP 方法 | 存取權限 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| **填寫報名表單** | `/` | `GET` | 公開 (所有用戶) | 顯示報名表單頁面，包含姓名、出席意願、餐盒需求與葷素選擇等欄位。 |
| **送出報名表單** | `/` | `POST` | 公開 (所有用戶) | 接收報名資料，驗證條件欄位（如是否需要餐盒與葷素選擇）並寫入資料庫，成功後重導向至成功頁。 |
| **報名成功回饋** | `/success` | `GET` | 公開 (所有用戶) | 顯示報名成功確認訊息，並展示報名資料摘要。 |
| **管理者登入頁** | `/admin/login` | `GET` | 公開 (所有用戶) | 顯示管理者登入介面。 |
| **執行管理者登入** | `/admin/login` | `POST` | 公開 (所有用戶) | 驗證管理者帳密，成功則寫入 session 並重導向至後台總覽頁。 |
| **執行管理者登出** | `/admin/logout` | `POST` / `GET` | 管理者 (登入後) | 清除管理者登入的 session 狀態，並重導向回登入頁。 |
| **後台資料總覽** | `/admin/dashboard`| `GET` | 管理者 (登入後) | 顯示所有報名紀錄表格、出席人數統計、餐盒數量統計、葷素比例統計，並提供編輯、刪除與匯出按鈕。 |
| **編輯報名資料頁**| `/admin/edit/<int:id>`| `GET` | 管理者 (登入後) | 讀取指定 ID 的報名資料，並以編輯表單呈現。 |
| **送出編輯資料** | `/admin/edit/<int:id>`| `POST` | 管理者 (登入後) | 接收修改後的資料，驗證後更新至資料庫，成功則重導向回總覽頁。 |
| **刪除報名資料** | `/admin/delete/<int:id>`| `POST` | 管理者 (登入後) | 刪除資料庫中指定 ID 的報名紀錄，成功後重導向回總覽頁。 |
| **匯出 CSV 檔案** | `/admin/export` | `GET` | 管理者 (登入後) | 將資料庫中所有報名資料生成為 CSV 檔案格式並提供下載。 |

---

> 📌 本流程圖文件已將 PRD 的功能需求與 ARCHITECTURE.md 的專案路由架構完全對接。確認無誤後，即可進入資料庫設計（`/db-design`）與實作階段。
