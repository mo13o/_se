# create-booknest-cloudflare

用一個 `npx` 指令建立完整的 BookNest 線上書店專案。產生的專案使用原生 HTML、CSS、JavaScript、Cloudflare Workers 與 Cloudflare D1，適合課程作業、教學與展示。

## 建立專案

```bash
npx create-booknest-cloudflare my-bookstore
cd my-bookstore
npm install
npm run db:migrate:local
npm run dev
```

本機網站預設由 Wrangler 顯示實際網址，通常是 `http://127.0.0.1:8787`。

## 功能

- 書籍列表、分類、搜尋及價格排序
- 書籍詳細頁
- 購物車與模擬訂單
- D1 訂單儲存與庫存扣減
- 後端管理員登入驗證
- 書籍 CRUD、庫存與訂單管理
- 15 本展示書籍與完整 migrations

## 部署至 Cloudflare

```bash
npx wrangler login
npm run db:create
npm run db:migrate:remote
npm run deploy
```

`db:create` 會建立 `booknest-db`，並將正式 D1 ID 寫入新專案的 `wrangler.jsonc`。請勿把 `.wrangler`、登入資訊或其他機密資料加入版本控制。

## 預設後台帳號

- 帳號：`admin`
- 密碼：`BookNest123!`

這組帳密只供課堂展示；正式使用前應建立新的 migration 來更換密碼雜湊。

## 系統需求

- Node.js 18 以上
- npm
- Cloudflare 帳號（正式部署時需要）

## 示範網站

[BookNest Cloudflare Demo](https://booknest.daisyhuang1224.workers.dev)

## 授權

MIT
