# database.py
import sqlite3
from pathlib import Path

DB_PATH = Path("trainer.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            shift TEXT NOT NULL,
            mode INTEGER NOT NULL,
            score_percent INTEGER NOT NULL,
            errors_count INTEGER NOT NULL,
            seed INTEGER,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_result(employee_name, shift, mode, score_percent, errors_count, seed, created_at):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO results (
            employee_name,
            shift,
            mode,
            score_percent,
            errors_count,
            seed,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_name,
        shift,
        mode,
        score_percent,
        errors_count,
        seed,
        created_at
    ))

    conn.commit()
    conn.close()


def get_results_by_employee(employee_name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM results
        WHERE employee_name = ?
        ORDER BY id DESC
    """, (employee_name,))

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_last_results(limit=10):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM results
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_top_employees(limit=10):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            employee_name,
            COUNT(*) AS attempts,
            MAX(score_percent) AS best_score,
            ROUND(AVG(score_percent), 1) AS avg_score
        FROM results
        GROUP BY employee_name
        ORDER BY best_score DESC, avg_score DESC, attempts DESC
        LIMIT ?
    """, (limit,))

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_employee_summary(employee_name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*) AS attempts,
            COALESCE(MAX(score_percent), 0) AS best_score,
            COALESCE(ROUND(AVG(score_percent), 1), 0) AS avg_score
        FROM results
        WHERE employee_name = ?
    """, (employee_name,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"attempts": 0, "best_score": 0, "avg_score": 0}

    return dict(row)
