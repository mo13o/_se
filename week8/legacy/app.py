"""TaskFlow: local-first assignment/project task tracker (Python standard library only)."""
from datetime import date, datetime, timedelta
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import os
import sqlite3

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('TASKFLOW_DB', str(ROOT / 'tasks.db')))


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def initialize():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '作業',
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT '中',
            notes TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')


def valid_task(payload):
    title = str(payload.get('title', '')).strip()
    due_date = str(payload.get('due_date', '')).strip()
    category = str(payload.get('category', '作業')).strip()
    priority = str(payload.get('priority', '中')).strip()
    notes = str(payload.get('notes', '')).strip()
    if not title or len(title) > 100:
        raise ValueError('任務名稱必須介於 1～100 個字元')
    if category not in ('作業', '考試', '專題', '其他'):
        raise ValueError('類別不正確')
    if priority not in ('高', '中', '低'):
        raise ValueError('優先度不正確')
    try:
        date.fromisoformat(due_date)
    except ValueError:
        raise ValueError('截止日期格式錯誤，請使用 YYYY-MM-DD')
    if len(notes) > 1000:
        raise ValueError('備註最多 1000 個字元')
    return (title, category, due_date, priority, notes)


def list_tasks():
    with connect() as db:
        return [dict(r) for r in db.execute('''SELECT * FROM tasks
            ORDER BY completed ASC, due_date ASC,
            CASE priority WHEN '高' THEN 0 WHEN '中' THEN 1 ELSE 2 END, id DESC''')]


def add_task(data):
    fields = valid_task(data)
    with connect() as db:
        cur = db.execute('INSERT INTO tasks (title, category, due_date, priority, notes) VALUES (?,?,?,?,?)', fields)
        return cur.lastrowid


def update_task(task_id, data):
    fields = valid_task(data)
    with connect() as db:
        cur = db.execute('UPDATE tasks SET title=?, category=?, due_date=?, priority=?, notes=? WHERE id=?', (*fields, task_id))
        return cur.rowcount > 0


def toggle_task(task_id):
    with connect() as db:
        cur = db.execute('UPDATE tasks SET completed=1-completed WHERE id=?', (task_id,))
        return cur.rowcount > 0


def delete_task(task_id):
    with connect() as db:
        cur = db.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        return cur.rowcount > 0


def summary(tasks, today=None):
    today = today or date.today()
    pending = [t for t in tasks if not t['completed']]
    return {
        'total': len(tasks),
        'done': len(tasks) - len(pending),
        'pending': len(pending),
        'overdue': sum(date.fromisoformat(t['due_date']) < today for t in pending),
        'soon': sum(today <= date.fromisoformat(t['due_date']) <= today + timedelta(days=3) for t in pending),
        'rate': round((len(tasks) - len(pending)) / len(tasks) * 100) if tasks else 0,
    }


class Handler(BaseHTTPRequestHandler):
    def respond(self, code, content, content_type='application/json; charset=utf-8'):
        data = content if isinstance(content, bytes) else content.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def api(self, code, result):
        self.respond(code, json.dumps(result, ensure_ascii=False))

    def body(self):
        size = int(self.headers.get('Content-Length', '0'))
        if size > 16384:
            raise ValueError('資料量過大')
        try:
            result = json.loads(self.rfile.read(size))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError('JSON 格式錯誤')
        if not isinstance(result, dict):
            raise ValueError('內容必須是物件')
        return result

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/':
            self.respond(200, (ROOT / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        elif path == '/api/tasks':
            tasks = list_tasks()
            self.api(200, {'tasks': tasks, 'summary': summary(tasks), 'today': date.today().isoformat()})
        else:
            self.api(404, {'error': '找不到頁面'})

    def do_POST(self):
        self.change('POST')

    def do_PUT(self):
        self.change('PUT')

    def do_DELETE(self):
        self.change('DELETE')

    def change(self, method):
        path = urlparse(self.path).path
        parts = path.strip('/').split('/')
        if not parts or parts[0] != 'api' or len(parts) < 2 or parts[1] != 'tasks':
            return self.api(404, {'error': 'API 不存在'})
        try:
            if method == 'POST' and len(parts) == 2:
                task_id = add_task(self.body())
                return self.api(201, {'id': task_id})
            if len(parts) not in (3, 4) or not parts[2].isdigit():
                return self.api(404, {'error': '路徑不正確'})
            task_id = int(parts[2])
            if method == 'PUT' and len(parts) == 3:
                found = update_task(task_id, self.body())
            elif method == 'POST' and len(parts) == 4 and parts[3] == 'toggle':
                found = toggle_task(task_id)
            elif method == 'DELETE' and len(parts) == 3:
                found = delete_task(task_id)
            else:
                return self.api(405, {'error': '不支援此操作'})
            return self.api(200 if found else 404, {'ok': found, **({} if found else {'error': '找不到任務'})})
        except ValueError as exc:
            self.api(400, {'error': str(exc)})


def main():
    initialize()
    server = ThreadingHTTPServer(('127.0.0.1', 8000), Handler)
    print('TaskFlow 已啟動：http://127.0.0.1:8000')
    print('按 Ctrl+C 結束')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已關閉')
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
