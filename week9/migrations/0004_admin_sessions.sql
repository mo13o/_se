CREATE TABLE admin_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  admin_id INTEGER NOT NULL,
  token_hash TEXT NOT NULL UNIQUE,
  expires_at TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
);
CREATE INDEX idx_admin_sessions_expires ON admin_sessions(expires_at);

-- 本機展示帳號：admin / BookNest123!（資料庫只保存 PBKDF2 雜湊）
INSERT INTO admins (username, password_hash)
VALUES ('admin', 'pbkdf2$210000$Csqzy1TSKsSkWUsKj0uYgg==$g4XkqIkGDSWlhbhg/538DFkftYJwhg6ONh3yY71EBtw=');
