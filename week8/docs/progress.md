# 開發進度

## P0：盤點與基礎建置
狀態：已實作，等待使用者確認。

完成：原型封存、React/TypeScript/Vite、FastAPI/SQLAlchemy、SQLite/Alembic、Docker Compose、環境範例與基本測試。

未完成：P1 Level 1 遷移與舊資料匯入；P2～P7 依規劃書順序進行。

已知限制：P0 新架構不提供任務 CRUD；可操作舊功能仍在 `legacy/`。

測試結果：Alembic upgrade 通過；後端 pytest 2/2 通過（另有 1 個第三方 deprecation warning）；前端 Vitest 1/1 通過；TypeScript/Vite production build 通過；API、資料庫、前端與 OpenAPI 實際啟動檢查皆回傳 HTTP 200。Docker Compose 設定驗證通過，但此執行環境無權連線 Docker Desktop daemon，因此未在本機完成容器啟動。


## P1：Level 1 遷移

狀態：已完成，等待使用者確認。

### 完成
- 新架構任務 CRUD 與 SQLite 永久儲存。
- 類別、狀態、優先級篩選；標題／說明搜尋；截止日、優先級、建立時間排序；分頁。
- 總數、待完成、完成、逾期、三日內到期與完成率統計。
- React 表單、編輯、完成切換、刪除確認、Loading／Empty／Error／Success 狀態與手機版面。
- `0002_p1_tasks` migration、DB CHECK、索引、統一驗證錯誤。
- 舊 `tasks.db` 唯讀匯入：先備份、欄位映射、匯入報告、重跑去重。

### 測試結果
- Alembic P0 → P1 migration：通過。
- 後端 pytest：6/6 通過；涵蓋 CRUD、持久化、搜尋、篩選、排序、統計、驗證與舊資料匯入一致性／冪等性。
- 前端 Vitest：2/2 通過；production TypeScript/Vite build 通過。
- 真實啟動煙霧測試：POST 建立後 GET 可查得同一 SQLite 資料；統計正確；前端與 OpenAPI 均 HTTP 200。測試資料已刪除。
- 已知非阻擋警告：Starlette TestClient 使用的 AnyIO alias 發出第三方 deprecation warning。

### 下一階段
P2：帳號、登入／登出、個人資料隔離、課程與課表。尚未開始。

## P2：帳號、課程與課表
狀態：完成。Argon2id、Cookie session、CSRF、登入節流、修改密碼、個人資料隔離、課程 CRUD、課表與重疊確認均已實作。兩帳號隔離測試通過。

## P3：行事曆與提醒
狀態：完成。日期事件 API、93 天限制、逾期／三日內通知去重與已讀完成；重複載入不產生重複通知測試通過。

## P4：團隊與專案
狀態：完成。團隊、Owner/Admin/Member、限時雜湊邀請、成員、專案及里程碑完成；非成員存取回傳 404，Owner 保護規則已實作。

## P5：看板與甘特
狀態：完成。團隊任務、單一指派、todo/in_progress/review/done、留言、日期資料與簡易甘特介面完成；被指派 Member 可更新，跨團隊不可讀。

## P6：報表與通知
狀態：完成。專案統計、UTF-8 BOM CSV、含中文 PDF 週報、通知與 audit schema 完成；有權限可下載、非成員無法下載。

## P7：整合與部署
狀態：完成。乾淨 SQLite 由 0001～0008 migration 建立成功，schema stage=P7，共 16 張系統表。Seed、備份／還原、Docker Compose、CI、部署與試用文件已完成。

### 最終測試（2026-10-30）
- 後端 pytest：9/9 通過（Auth、CSRF、隔離、課表、通知、邀請、看板、留言、報表、IDOR）。
- 前端 Vitest：2/2 通過；TypeScript/Vite production build 通過。
- Alembic 乾淨資料庫 0001→0008：通過，P7 marker 正確。
- 真實啟動：API、SQLite、前端、OpenAPI 均 HTTP 200。
- Docker Compose config：通過；目前自動化執行環境無權連線 Docker Desktop daemon，容器實際啟動需由本機 Docker Desktop 執行。
- 唯一警告：Starlette TestClient 的 AnyIO alias 第三方 deprecation warning，不影響功能。

### 已知限制
- SQLite 適合本機／小型試用；正式多人服務需依部署文件切換 PostgreSQL、HTTPS、Secure Cookie 與集中式 rate limit。
- 前端看板／甘特採 MVP 簡化呈現，未做複雜相依排程或即時協同編輯，符合規格非目標。
