# 技術決策

## P0
- 完整保留 `legacy/`；新架構置於 `frontend/` 與 `backend/`。
- SQLite 透過 SQLAlchemy 2 與 Alembic 管理，正式多人部署預留 PostgreSQL。
- P0 migration 僅建立 `system_metadata`；Level 1 新 schema 留待 P1。
- API 使用 `/api/v1`；P0 前端只顯示真實健康狀態。

## P1
- P1 尚無帳號，因此任務表先不加入 `owner_id`；P2 建立使用者時，以 migration 新增 owner 關聯並將既有 P1 任務指派給升級時建立／指定的帳號。
- `legacy_source_id` 使用 UNIQUE 保證舊資料匯入可重跑而不重複。
- 舊資料庫以 SQLite read-only URI 開啟，匯入前建立時間戳備份，並輸出 JSON 數量報告。
- 任務類別與優先級在新 API 使用穩定英文代碼，UI 維持繁體中文。
