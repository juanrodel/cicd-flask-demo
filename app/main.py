import logging
import os

import psycopg
import redis
from flask import Flask, jsonify, request

app = Flask(__name__)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


def get_db():
    password_file = os.environ.get("DB_PASSWORD_FILE")
    if password_file:
        with open(password_file) as f:
            password = f.read().strip()
        return psycopg.connect(
            host=os.environ["DB_HOST"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=password,
        )
    return psycopg.connect(DATABASE_URL)


def get_cache():
    return redis.Redis.from_url(REDIS_URL)


@app.get("/")
def index():
    return jsonify(message="Hello from CI/CD", version="1.0.0")


@app.get("/health")
def health():
    # Test if the process is up without dependencies
    return jsonify(status="ok")


@app.get("/ready")
def ready():
    # Test to see if we can reach Postgres and Redis
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        get_cache().ping()
    except Exception:
        logger.exception("Health check failed")
        return jsonify(status="unavailable"), 503
    else:
        return jsonify(status="ready")


@app.get("/visits")
def visits():
    count = get_cache().incr("visits")
    return jsonify(visits=count)


@app.get("/notes")
def list_notes():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, body, created_at FROM notes ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return jsonify(
        [{"id": r[0], "body": r[1], "created_at": r[2].isoformat()} for r in rows]
    )


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    body = (data.get("body") or "").strip()
    if not body or len(body) > 500:
        return jsonify(error="body is required (max 500 chars)"), 400
    with get_db() as conn:
        row = conn.execute(
            "INSERT INTO notes (body) VALUES (%s) RETURNING id, created_at",
            (body,),
        ).fetchone()
    return jsonify(id=row[0], body=body, created_at=row[1].isoformat()), 201