# Cloudflare 部署教學

本專案使用目前建議的 `wrangler.jsonc`、Workers Static Assets 與 D1 migration。

## 1. 環境準備

```powershell
npm install
npx wrangler login
npx wrangler whoami
```

`wrangler login` 會開啟瀏覽器，登入 Cloudflare 後按 Allow。

## 2. 建立正式 D1

```powershell
npx wrangler d1 create booknest-db --location apac
```

複製輸出的 `database_id`，替換 `wrangler.jsonc` 中的全零 UUID。不要修改 binding 名稱 `DB`。

## 3. 建立正式資料表與測試資料

```powershell
npx wrangler d1 migrations apply booknest-db --remote
npx wrangler d1 migrations list booknest-db --remote
npx wrangler d1 execute booknest-db --remote --command "SELECT COUNT(*) AS books FROM books;"
```

應顯示 15 本書且沒有待套用 migration。

## 4. 部署 Worker

```powershell
npm test
npx wrangler deploy
```

成功後 Wrangler 會顯示類似：

```text
https://booknest.<你的-workers-dev-子網域>.workers.dev
```

這就是教授可以直接開啟的公開網址。後台位於 `/admin.html`。

## 5. 正式環境驗證

```powershell
curl https://你的網址.workers.dev/api/health
curl https://你的網址.workers.dev/api/books
```

再用瀏覽器完成 `docs/DEMO.md` 的展示流程。

## 常見錯誤

| 錯誤 | 原因 | 解法 |
|---|---|---|
| `You are not authenticated` | 尚未登入 | 執行 `npx wrangler login` |
| D1 binding/UUID 錯誤 | 尚未替換全零 UUID | 使用 `d1 create` 回傳的 UUID |
| `no such table` | 遠端 migration 尚未套用 | 執行 `d1 migrations apply --remote` |
| 本機連接埠改成 8788 | 8787 已被占用 | 使用終端機實際顯示的網址 |
| 管理 API 401 | Session 過期或 Cookie 不存在 | 重新登入後台 |
| `ISBN 已存在` | ISBN 有 UNIQUE 限制 | 使用不同 ISBN |
| 訂單庫存不足 | 庫存已被其他訂單扣減 | 重新整理購物車並調整數量 |
| 圖片未顯示 | 外部圖片網址失效 | 在後台改成有效 HTTPS 圖片網址 |

## 安全提醒

課程展示帳號是 `admin / BookNest123!`。正式公開前應產生新的 PBKDF2 雜湊並更新 migration 或資料庫，切勿使用展示密碼保存重要資料。

