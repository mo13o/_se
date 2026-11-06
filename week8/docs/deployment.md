# 部署與試用

## 本機
`docker compose up --build`，前端 5173、API 8000。第一次啟動自動 migration。

## 正式環境檢查
- 改用 PostgreSQL、HTTPS、Secure Cookie，限制 CORS origin。
- 將 session／邀請／匯出接上集中式 rate limit；設定日誌、監控與每日備份。
- 先執行 `pytest -q`、`npm test`、`npm run build`，再做還原演練。
- 以虛構 seed 試跑，不得使用真實課表或姓名。

## 試用
邀請 3–5 組團隊試用 2–4 週，僅衡量留存、完成任務數、週活躍與回饋，不宣稱已有營收或客戶驗證。
