import os
import time
from datetime import timezone

import psycopg
from flask import Flask, flash, redirect, render_template, request, url_for
from psycopg.rows import dict_row

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-demo-change-this-key")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "taskboard"),
    "user": os.getenv("POSTGRES_USER", "taskuser"),
    "password": os.getenv("POSTGRES_PASSWORD", "taskpass"),
    "row_factory": dict_row,
    "connect_timeout": 3,
}


def get_connection():
    return psycopg.connect(**DB_CONFIG)


def initialise_database():
    """Wait for PostgreSQL and create the app table on first startup."""
    last_error = None
    for attempt in range(1, 31):
        try:
            with get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id BIGSERIAL PRIMARY KEY,
                        title VARCHAR(160) NOT NULL,
                        completed BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
            print("Database is ready; tasks table is available.", flush=True)
            return
        except psycopg.OperationalError as exc:
            last_error = exc
            print(f"Waiting for PostgreSQL ({attempt}/30): {exc}", flush=True)
            time.sleep(2)
    raise RuntimeError("Could not connect to PostgreSQL after 30 attempts") from last_error


initialise_database()


@app.get("/")
def index():
    with get_connection() as conn:
        tasks = conn.execute(
            "SELECT id, title, completed, created_at FROM tasks ORDER BY created_at DESC, id DESC"
        ).fetchall()
    total = len(tasks)
    completed = sum(1 for task in tasks if task["completed"])
    return render_template(
        "index.html", tasks=tasks, total=total, completed=completed, pending=total - completed
    )


@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Enter a task before adding it.", "error")
    elif len(title) > 160:
        flash("Task names must be 160 characters or fewer.", "error")
    else:
        with get_connection() as conn:
            conn.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
        flash("Task added.", "success")
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE tasks SET completed = NOT completed WHERE id = %s", (task_id,)
        )
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    flash("Task deleted.", "success")
    return redirect(url_for("index"))


@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1").fetchone()
        return {"status": "healthy", "database": "connected"}, 200
    except psycopg.Error:
        return {"status": "unhealthy", "database": "unavailable"}, 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
