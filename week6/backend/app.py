import os

import psycopg
from flask import Flask, jsonify, request


app = Flask(__name__)
DATABASE_URL = os.environ["DATABASE_URL"]


def connect():
    return psycopg.connect(DATABASE_URL)


@app.get("/api/health")
def health():
    try:
        with connect() as connection:
            connection.execute("SELECT 1")
        return jsonify(status="healthy", database="connected")
    except Exception as error:
        return jsonify(status="unhealthy", error=str(error)), 503


@app.get("/api/messages")
def list_messages():
    with connect() as connection:
        rows = connection.execute(
            "SELECT id, content, created_at FROM messages ORDER BY id DESC LIMIT 20"
        ).fetchall()
    return jsonify([
        {"id": row[0], "content": row[1], "created_at": row[2].isoformat()}
        for row in rows
    ])


@app.post("/api/messages")
def create_message():
    content = (request.get_json(silent=True) or {}).get("content", "").strip()
    if not content:
        return jsonify(error="訊息不可為空白"), 400
    if len(content) > 200:
        return jsonify(error="訊息不可超過 200 個字元"), 400

    with connect() as connection:
        row = connection.execute(
            "INSERT INTO messages (content) VALUES (%s) RETURNING id, content, created_at",
            (content,),
        ).fetchone()
    return jsonify(
        id=row[0], content=row[1], created_at=row[2].isoformat()
    ), 201
