# 資料庫與備份

SQLite 開發資料位於 `backend/data/taskflow.db`；所有 schema 由 Alembic `0001`～`0008` 依序建立，並啟用 foreign keys。正式多人部署應改 PostgreSQL。

備份：
```powershell
cd backend
python -m scripts.backup data/taskflow.db --output backups
```
還原：停止服務，保留目前資料庫備份，再將指定備份複製回 `data/taskflow.db`，執行 `alembic upgrade head` 後啟動並檢查 `/api/v1/health`。不得在服務寫入中直接覆蓋資料庫。
