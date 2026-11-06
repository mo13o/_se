# TaskFlow Level 3

目前已依 P0～P7 完成可執行的 Level 3 展示版；Level 1 原型完整保留於 `legacy/`。

## 一鍵啟動
```powershell
docker compose up --build
```
前端：http://127.0.0.1:5173；API：http://127.0.0.1:8000；API 文件：http://127.0.0.1:8000/docs。
停止：`docker compose down`。資料保留在 `taskflow_data` volume。

## 測試
```powershell
cd backend
pytest -q
cd ../frontend
npm test
npm run build
```

本機開發：後端安裝 `backend/requirements.txt`，執行 `alembic upgrade head` 與 `uvicorn app.main:app --reload`；前端執行 `npm install`、`npm run dev`。

原始規劃書、技術決策、階段進度在 `docs/`。舊資料安全匯入屬 P1。

## P1 任務功能

目前可新增、編輯、刪除、完成／恢復任務，並使用搜尋、分類／狀態／優先級篩選、排序及儀表板統計。所有資料均透過 FastAPI 寫入 SQLite。

## 匯入舊 Level 1 資料

先啟動 migration，再執行：

```powershell
cd backend
python -m scripts.migrate_legacy --legacy-db "C:\完整路徑\tasks.db" --database-url "sqlite:///./data/taskflow.db" --report "migration-report.json"
```

工具會以唯讀方式開啟舊資料庫、先建立時間戳備份，再匯入資料並輸出 JSON 報告。相同資料可安全重跑，`legacy_source_id` 會避免重複匯入。請勿把正式資料庫或報告提交至 Git。

## P1 API
- `GET/POST /api/v1/tasks`
- `GET/PATCH/DELETE /api/v1/tasks/{task_id}`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/health`

列表支援 `search`、`category`、`status`、`priority`、`sort`、`order`、`limit`、`offset`。

# Level 3 完整功能

登入後上方導覽可進入任務、課程、行事曆、團隊、專案看板／甘特及通知。完整 API 與下載功能見 `/docs`。

## Demo seed
```powershell
cd backend
python -m scripts.seed
```
帳號：`demo@taskflow.local`，密碼：`DemoPassword123`（只限本機虛構資料，正式環境請刪除或修改）。

## 舊資料匯入（Level 3）
先註冊目標帳號，再執行：
```powershell
python -m scripts.migrate_legacy --legacy-db "C:\完整路徑\tasks.db" --owner-email "你的帳號@example.com" --database-url "sqlite:///./data/taskflow.db" --report migration-report.json
```

## 文件
- `docs/api-contract.md`：端點摘要
- `docs/database.md`：資料庫、備份與還原
- `docs/deployment.md`：部署與試用
- `docs/progress.md`：P0～P7 實際測試結果
- `docs/teacher-review.md`：老師檢閱動線、功能對照與展示重點
