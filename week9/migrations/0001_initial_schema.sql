PRAGMA foreign_keys = ON;

-- 書籍分類
CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) BETWEEN 1 AND 50)
);

-- 書籍資料；is_active = 0 代表下架，保留資料以維持訂單歷史
CREATE TABLE books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 200),
  author TEXT NOT NULL CHECK (length(trim(author)) BETWEEN 1 AND 100),
  publisher TEXT NOT NULL CHECK (length(trim(publisher)) BETWEEN 1 AND 100),
  isbn TEXT NOT NULL UNIQUE CHECK (length(isbn) BETWEEN 10 AND 17),
  category_id INTEGER NOT NULL,
  price INTEGER NOT NULL CHECK (price >= 0),
  stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
  description TEXT NOT NULL DEFAULT '',
  image_url TEXT NOT NULL DEFAULT '',
  is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  FOREIGN KEY (category_id) REFERENCES categories(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 訂單主檔；金額以新台幣整數儲存，避免浮點誤差
CREATE TABLE orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_number TEXT NOT NULL UNIQUE,
  customer_name TEXT NOT NULL CHECK (length(trim(customer_name)) BETWEEN 1 AND 100),
  customer_email TEXT NOT NULL CHECK (length(trim(customer_email)) BETWEEN 3 AND 254),
  total_amount INTEGER NOT NULL CHECK (total_amount >= 0),
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- 訂單明細保留購買當下單價，不受日後書價修改影響
CREATE TABLE order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  book_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price INTEGER NOT NULL CHECK (unit_price >= 0),
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
  UNIQUE (order_id, book_id)
);

-- 管理員密碼只保存 PBKDF2 雜湊字串，絕不保存明文
CREATE TABLE admins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE CHECK (length(trim(username)) BETWEEN 3 AND 50),
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_books_category_active ON books(category_id, is_active);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
