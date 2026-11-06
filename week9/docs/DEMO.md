# 教授驗收展示流程

1. 開啟公開 `workers.dev` 網址，說明前端與 API 使用同一個 Worker。
2. 確認首頁顯示 15 本 D1 書籍。
3. 搜尋「SQL」，展示書名／作者搜尋。
4. 選擇「程式設計」與「價格低到高」。
5. 開啟一本書，說明 `GET /api/books/:id`。
6. 加入購物車，修改數量並觀察總額。
7. 填入展示姓名與 Email，建立模擬訂單。
8. 記下畫面的訂單編號。
9. 登入 `/admin.html`。
10. 到訂單紀錄確認相同訂單編號。
11. 新增一本展示書籍。
12. 修改其價格或庫存，回前台重新整理確認。
13. 下架該書，回前台確認不再顯示。

## D1 指令驗證

```powershell
npx wrangler d1 execute booknest-db --remote --command "SELECT order_number, customer_name, total_amount, status FROM orders ORDER BY id DESC LIMIT 5;"
```

## 課堂講解重點

- 前端 `fetch()` 只呼叫 Worker API，無法直接連 D1。
- Worker 使用參數化 SQL，避免 SQL Injection。
- 訂單金額由後端依資料庫價格重新計算。
- 訂單、明細與扣庫存在同一個 D1 batch。
- 管理權限由後端 Session 驗證，不是只隱藏按鈕。

