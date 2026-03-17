# database.py
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path("trainer.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
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


def save_result(
    employee_name: str,
    shift: str,
    mode: int,
    score_percent: int,
    errors_count: int,
    seed: int | None,
    created_at: str
) -> None:
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


def get_results_by_employee(employee_name: str) -> List[Dict[str, Any]]:
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


def get_last_results(limit: int = 20) -> List[Dict[str, Any]]:
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
