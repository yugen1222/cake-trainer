import os
import calendar
import sqlite3
from datetime import datetime, date
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TIMEZONE = "Asia/Tashkent"
DB_NAME = "checklists.db"

ADMINS = {
    1262780375: "Abbos",
    1852920176: "Madina",
}

MONTH_NAMES_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}

TASKS = {
    "1 смена": [
        {"name": "Провести открывающую встречу", "deadline": "08:30", "photo_required": False},
        {"name": "Распределение по зонам и бейджикам", "deadline": "09:00", "photo_required": True},
        {"name": "Распределить аудио бейджики", "deadline": "09:00", "photo_required": False},
        {"name": "Проверить наличие спец заказов", "deadline": "09:00", "photo_required": False},
        {"name": "ГО лист проверить", "deadline": "10:00", "photo_required": False},
        {"name": "Лист списания проверить", "deadline": "10:00", "photo_required": False},
        {"name": "Сделать обход по магазину", "deadline": "11:00", "photo_required": False},
        {"name": "Провести чек лист проверки и обработки", "deadline": "15:00", "photo_required": True},
        {"name": "Провести голосование по стафу", "deadline": "15:00", "photo_required": False},
        {"name": "Написать заявку на стаф питание", "deadline": "15:00", "photo_required": False},
        {"name": "Проверить торты на ФИФО по бланку", "deadline": "14:00", "photo_required": True},
        {"name": "Сделать обучение по 1 сотруднику", "deadline": "16:00", "photo_required": False},
        {"name": "Проверить работу чек листа морозилки", "deadline": "13:00", "photo_required": False},
        {"name": "При необходимости сделать изменения смен в Верификсе и подтвердить отчет графика", "deadline": "16:00", "photo_required": True},
        {"name": "Посчитать ФОТ за смену", "deadline": "16:00", "photo_required": False},
        {"name": "Провести закрывающую встречу", "deadline": "16:00", "photo_required": False},
    ],
    "2 смена": [
        {"name": "Провести открывающую встречу", "deadline": "16:30", "photo_required": False},
        {"name": "Распределение по зонам и бейджикам", "deadline": "17:00", "photo_required": True},
        {"name": "Распределить бейджики", "deadline": "17:00", "photo_required": False},
        {"name": "Проверить наличие спец заказов", "deadline": "17:00", "photo_required": False},
        {"name": "Сделать обход по магазину", "deadline": "17:00", "photo_required": False},
        {"name": "Провести чек лист проверки и обработки", "deadline": "21:00", "photo_required": True},
        {"name": "Сделать обучение по 1 сотруднику", "deadline": "21:00", "photo_required": False},
        {"name": "Проверить работу чек листа морозилки", "deadline": "18:00", "photo_required": False},
        {"name": "При необходимости сделать изменения смен в Верификсе и подтвердить отчет графика", "deadline": "23:00", "photo_required": True},
        {"name": "Пройтись по всем чек листам", "deadline": "23:00", "photo_required": False},
        {"name": "Убрать списание", "deadline": "23:00", "photo_required": False},
        {"name": "Посчитать ФОТ за смену", "deadline": "23:00", "photo_required": False},
        {"name": "Провести закрывающую смену", "deadline": "23:00", "photo_required": False},
    ],
    "3 смена": [
        {"name": "Разморозка", "deadline": "01:00", "photo_required": False},
        {"name": "Мойка Unox", "deadline": "01:00", "photo_required": False},
        {"name": "Убрать списание", "deadline": "01:00", "photo_required": False},
        {"name": "Закрытие кассы", "deadline": "00:00", "photo_required": False},
        {"name": "ГО лист", "deadline": "08:00", "photo_required": False},
        {"name": "Таскер задачи", "deadline": "08:00", "photo_required": False},
        {"name": "Убрать спец заказы", "deadline": "08:00", "photo_required": False},
        {"name": "Приемка товара", "deadline": "07:00", "photo_required": False},
        {"name": "Выкладка витрин", "deadline": "07:00", "photo_required": False},
        {"name": "Обход всех зон", "deadline": "07:00", "photo_required": False},
        {"name": "При необходимости сделать изменения смен в Верификсе и подтвердить отчет графика", "deadline": "08:00", "photo_required": True},
        {"name": "Разделить пирожные по контейнерам", "deadline": "06:00", "photo_required": True},
        {"name": "Заполнить бланк списания", "deadline": "07:00", "photo_required": False},
        {"name": "Принять накладные в вендоре", "deadline": "06:00", "photo_required": False},
        {"name": "Скинуть все накладные в группу", "deadline": "07:00", "photo_required": False},
        {"name": "Зашив накладных в файловку", "deadline": "08:00", "photo_required": False},
    ],
}


def now_dt():
    return datetime.now(ZoneInfo(TIMEZONE))


def now_str():
    return now_dt().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return now_dt().strftime("%Y-%m-%d")


def now_hm():
    return now_dt().strftime("%H:%M")


def hm_to_minutes(hm: str) -> int:
    h, m = hm.split(":")
    return int(h) * 60 + int(m)


def minutes_to_hm(total: int) -> str:
    total %= 24 * 60
    h = total // 60
    m = total % 60
    return f"{h:02d}:{m:02d}"


def minus_minutes(hm: str, mins: int) -> str:
    return minutes_to_hm(hm_to_minutes(hm) - mins)


def sorted_tasks_for_shift(shift: str):
    indexed = []
    for original_index, task in enumerate(TASKS[shift]):
        indexed.append({
            "original_index": original_index,
            "name": task["name"],
            "deadline": task["deadline"],
            "photo_required": task["photo_required"],
        })
    indexed.sort(key=lambda x: (hm_to_minutes(x["deadline"]), x["original_index"]))
    return indexed


def db_connect():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            telegram_id INTEGER PRIMARY KEY,
            selected_name TEXT,
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS active_shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_str TEXT NOT NULL,
            manager_name TEXT NOT NULL,
            shift TEXT NOT NULL,
            telegram_id INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uniq_active_shift
        ON active_shifts (date_str, manager_name)
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_str TEXT NOT NULL,
            telegram_id INTEGER NOT NULL,
            manager_name TEXT NOT NULL,
            shift TEXT NOT NULL,
            task_index INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            deadline TEXT NOT NULL,
            photo_required INTEGER NOT NULL DEFAULT 0,
            employee_status TEXT NOT NULL,
            photo_file_id TEXT,
            submitted_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uniq_submission
        ON submissions (date_str, manager_name, shift, task_index)
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_photo (
            telegram_id INTEGER PRIMARY KEY,
            manager_name TEXT NOT NULL,
            shift TEXT NOT NULL,
            task_index INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sent_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_str TEXT NOT NULL,
            notif_type TEXT NOT NULL,
            shift TEXT NOT NULL,
            task_index INTEGER,
            manager_name TEXT,
            sent_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS manager_flow_state (
            telegram_id INTEGER PRIMARY KEY,
            manager_name TEXT NOT NULL,
            shift TEXT NOT NULL,
            next_sorted_pos INTEGER NOT NULL DEFAULT 0,
            current_message_id INTEGER,
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_temp_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_str TEXT NOT NULL,
            admin_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def get_all_people():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT name FROM people
        WHERE is_active = 1
        ORDER BY name COLLATE NOCASE
    """)
    rows = cur.fetchall()
    conn.close()
    return [row["name"] for row in rows]


def add_person(name: str):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO people (name, created_at)
        VALUES (?, ?)
    """, (name.strip(), now_str()))
    conn.commit()
    conn.close()


def save_selected_name(telegram_id: int, name: str):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_profile (telegram_id, selected_name, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            selected_name = excluded.selected_name,
            updated_at = excluded.updated_at
    """, (telegram_id, name, now_str()))
    conn.commit()
    conn.close()


def get_selected_name(telegram_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT selected_name FROM user_profile
        WHERE telegram_id = ?
    """, (telegram_id,))
    row = cur.fetchone()
    conn.close()
    return row["selected_name"] if row and row["selected_name"] else None


def delete_selected_name(telegram_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_profile WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()


def set_active_shift(manager_name: str, shift: str, telegram_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO active_shifts (date_str, manager_name, shift, telegram_id, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date_str, manager_name) DO UPDATE SET
            shift = excluded.shift,
            telegram_id = excluded.telegram_id,
            created_at = excluded.created_at
    """, (today_str(), manager_name, shift, telegram_id, now_str()))
    conn.commit()
    conn.close()


def get_active_people_for_shift(shift: str):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT manager_name, telegram_id
        FROM active_shifts
        WHERE date_str = ? AND shift = ?
    """, (today_str(), shift))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_active_shifts_today():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT manager_name, shift, telegram_id
        FROM active_shifts
        WHERE date_str = ?
        ORDER BY manager_name
    """, (today_str(),))
    rows = cur.fetchall()
    conn.close()
    return rows


def save_submission(
    telegram_id: int,
    manager_name: str,
    shift: str,
    task_index: int,
    task_name: str,
    deadline: str,
    photo_required: bool,
    employee_status: str,
    photo_file_id: str | None = None,
):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO submissions (
            date_str, telegram_id, manager_name, shift,
            task_index, task_name, deadline, photo_required,
            employee_status, photo_file_id, submitted_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date_str, manager_name, shift, task_index)
        DO UPDATE SET
            telegram_id = excluded.telegram_id,
            employee_status = excluded.employee_status,
            photo_file_id = excluded.photo_file_id,
            submitted_at = excluded.submitted_at,
            deadline = excluded.deadline,
            photo_required = excluded.photo_required
    """, (
        today_str(),
        telegram_id,
        manager_name,
        shift,
        task_index,
        task_name,
        deadline,
        1 if photo_required else 0,
        employee_status,
        photo_file_id,
        now_str(),
    ))
    conn.commit()
    conn.close()


def get_submission_status(manager_name: str, shift: str, task_index: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT employee_status, photo_file_id
        FROM submissions
        WHERE date_str = ? AND manager_name = ? AND shift = ? AND task_index = ?
        LIMIT 1
    """, (today_str(), manager_name, shift, task_index))
    row = cur.fetchone()
    conn.close()
    return row


def get_submitted_task_indexes(manager_name: str, shift: str):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT task_index FROM submissions
        WHERE date_str = ? AND manager_name = ? AND shift = ?
        ORDER BY task_index
    """, (today_str(), manager_name, shift))
    rows = cur.fetchall()
    conn.close()
    return {row["task_index"] for row in rows}


def get_shift_progress(manager_name: str, shift: str):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT employee_status, COUNT(*) as cnt
        FROM submissions
        WHERE date_str = ? AND manager_name = ? AND shift = ?
        GROUP BY employee_status
    """, (today_str(), manager_name, shift))
    rows = cur.fetchall()
    conn.close()

    done = 0
    not_done = 0
    for row in rows:
        if row["employee_status"] == "Выполнено":
            done = row["cnt"]
        elif row["employee_status"] == "Не выполнено":
            not_done = row["cnt"]

    total = len(TASKS[shift])
    marked = done + not_done
    return total, marked, done, not_done


def get_today_status_summary():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT manager_name, shift, employee_status, COUNT(*) as cnt
        FROM submissions
        WHERE date_str = ?
        GROUP BY manager_name, shift, employee_status
        ORDER BY manager_name, shift
    """, (today_str(),))
    rows = cur.fetchall()
    conn.close()

    summary = {}
    for row in rows:
        key = (row["manager_name"], row["shift"])
        if key not in summary:
            summary[key] = {"done": 0, "not_done": 0}
        if row["employee_status"] == "Выполнено":
            summary[key]["done"] = row["cnt"]
        elif row["employee_status"] == "Не выполнено":
            summary[key]["not_done"] = row["cnt"]

    return summary


def get_manager_period_stats(manager_name: str, date_from: str, date_to: str):
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(DISTINCT date_str || '|' || shift) as shift_count
        FROM submissions
        WHERE manager_name = ? AND date_str BETWEEN ? AND ?
    """, (manager_name, date_from, date_to))
    shift_count = cur.fetchone()["shift_count"] or 0

    cur.execute("""
        SELECT
            COUNT(*) as total_tasks,
            SUM(CASE WHEN employee_status = 'Выполнено' THEN 1 ELSE 0 END) as done_tasks,
            SUM(CASE WHEN employee_status = 'Не выполнено' THEN 1 ELSE 0 END) as not_done_tasks,
            SUM(CASE WHEN photo_required = 1 THEN 1 ELSE 0 END) as photo_total,
            SUM(CASE WHEN photo_required = 1 AND photo_file_id IS NOT NULL AND employee_status = 'Выполнено' THEN 1 ELSE 0 END) as photo_done
        FROM submissions
        WHERE manager_name = ? AND date_str BETWEEN ? AND ?
    """, (manager_name, date_from, date_to))
    row = cur.fetchone()
    conn.close()

    total_tasks = row["total_tasks"] or 0
    done_tasks = row["done_tasks"] or 0
    not_done_tasks = row["not_done_tasks"] or 0
    photo_total = row["photo_total"] or 0
    photo_done = row["photo_done"] or 0
    percent = round((done_tasks / total_tasks) * 100, 1) if total_tasks else 0

    return {
        "manager_name": manager_name,
        "date_from": date_from,
        "date_to": date_to,
        "shift_count": shift_count,
        "total_tasks": total_tasks,
        "done_tasks": done_tasks,
        "not_done_tasks": not_done_tasks,
        "photo_total": photo_total,
        "photo_done": photo_done,
        "percent": percent,
    }


def manager_stats_text(stats: dict):
    return (
        f"📈 Статистика менеджера\n\n"
        f"{stats['manager_name']}\n"
        f"Период: {stats['date_from']} — {stats['date_to']}\n\n"
        f"Всего смен: {stats['shift_count']}\n"
        f"Всего задач: {stats['total_tasks']}\n"
        f"Выполнено: {stats['done_tasks']}\n"
        f"Не выполнено: {stats['not_done_tasks']}\n"
        f"Процент выполнения: {stats['percent']}%\n"
        f"Фото-задач закрыто: {stats['photo_done']}/{stats['photo_total']}"
    )


def set_pending_photo(telegram_id: int, manager_name: str, shift: str, task_index: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pending_photo (telegram_id, manager_name, shift, task_index, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            manager_name = excluded.manager_name,
            shift = excluded.shift,
            task_index = excluded.task_index,
            created_at = excluded.created_at
    """, (telegram_id, manager_name, shift, task_index, now_str()))
    conn.commit()
    conn.close()


def get_pending_photo(telegram_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM pending_photo
        WHERE telegram_id = ?
    """, (telegram_id,))
    row = cur.fetchone()
    conn.close()
    return row


def clear_pending_photo(telegram_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM pending_photo WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()


def was_notification_sent(notif_type: str, shift: str, task_index: int | None = None, manager_name: str | None = None):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM sent_notifications
        WHERE date_str = ?
          AND notif_type = ?
          AND shift = ?
          AND COALESCE(task_index, -1) = COALESCE(?, -1)
          AND COALESCE(manager_name, '') = COALESCE(?, '')
        LIMIT 1
    """, (today_str(), notif_type, shift, task_index, manager_name))
    row = cur.fetchone()
    conn.close()
    return bool(row)


def mark_notification_sent(notif_type: str, shift: str, task_index: int | None = None, manager_name: str | None = None):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sent_notifications (date_str, notif_type, shift, task_index, manager_name, sent_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (today_str(), notif_type, shift, task_index, manager_name, now_str()))
    conn.commit()
    conn.close()


def set_flow_state(telegram_id: int, manager_name: str, shift: str, next_sorted_pos: int, current_message_id: int | None):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO manager_flow_state (telegram_id, manager_name, shift, next_sorted_pos, current_message_id, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            manager_name = excluded.manager_name,
            shift = excluded.shift,
            next_sorted_pos = excluded.next_sorted_pos,
            current_message_id = excluded.current_message_id,
            updated_at = excluded.updated_at
    """, (telegram_id, manager_name, shift, next_sorted_pos, current_message_id, now_str()))
    conn.commit()
    conn.close()


def get_flow_state(telegram_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM manager_flow_state
        WHERE telegram_id = ?
    """, (telegram_id,))
    row = cur.fetchone()
    conn.close()
    return row


def clear_flow_state(telegram_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM manager_flow_state WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()


def save_admin_temp_media(admin_id: int, message_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO admin_temp_media (date_str, admin_id, message_id, created_at)
        VALUES (?, ?, ?, ?)
    """, (today_str(), admin_id, message_id, now_str()))
    conn.commit()
    conn.close()


def get_admin_temp_media(admin_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT message_id
        FROM admin_temp_media
        WHERE date_str = ? AND admin_id = ?
    """, (today_str(), admin_id))
    rows = cur.fetchall()
    conn.close()
    return [row["message_id"] for row in rows]


def clear_admin_temp_media(admin_id: int):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM admin_temp_media
        WHERE date_str = ? AND admin_id = ?
    """, (today_str(), admin_id))
    conn.commit()
    conn.close()


def get_unfinished_tasks():
    result = []
    active_rows = get_all_active_shifts_today()

    for row in active_rows:
        name = row["manager_name"]
        shift = row["shift"]
        submitted = get_submitted_task_indexes(name, shift)

        missing_tasks = []
        for task in sorted_tasks_for_shift(shift):
            if task["original_index"] not in submitted:
                missing_tasks.append(task["name"])

        if missing_tasks:
            result.append({
                "name": name,
                "shift": shift,
                "tasks": missing_tasks,
            })

    return result


def unfinished_tasks_text():
    data = get_unfinished_tasks()

    if not data:
        return "✅ Все задачи пройдены."

    lines = ["📝 Не прошли задачи\n"]
    for item in data:
        lines.append(f"👤 {item['name']} | {item['shift']}")
        for task in item["tasks"]:
            lines.append(f"— {task}")
        lines.append("")
    return "\n".join(lines)


def get_photo_task_statuses():
    conn = db_connect()
    cur = conn.cursor()

    result = []
    active_rows = get_all_active_shifts_today()

    for active in active_rows:
        name = active["manager_name"]
        shift = active["shift"]

        for task in sorted_tasks_for_shift(shift):
            if not task["photo_required"]:
                continue

            cur.execute("""
                SELECT employee_status, photo_file_id
                FROM submissions
                WHERE date_str = ? AND manager_name = ? AND shift = ? AND task_index = ?
                LIMIT 1
            """, (today_str(), name, shift, task["original_index"]))

            row = cur.fetchone()

            if row:
                result.append({
                    "name": name,
                    "shift": shift,
                    "task_name": task["name"],
                    "sent": bool(row["photo_file_id"]),
                    "photo_file_id": row["photo_file_id"],
                    "status": row["employee_status"],
                })
            else:
                result.append({
                    "name": name,
                    "shift": shift,
                    "task_name": task["name"],
                    "sent": False,
                    "photo_file_id": None,
                    "status": None,
                })

    conn.close()
    return result


def photo_tasks_text():
    data = get_photo_task_statuses()

    if not data:
        return "Сегодня фото-задач пока нет."

    lines = ["📸 Фото-задачи\n"]
    current_person = None

    for item in data:
        person_key = f"{item['name']} | {item['shift']}"
        if current_person != person_key:
            lines.append(f"\n👤 {person_key}")
            current_person = person_key

        status_icon = "✅" if item["sent"] else "❌"
        lines.append(f"{status_icon} {item['task_name']}")

    return "\n".join(lines)


def is_admin(user_id: int):
    return user_id in ADMINS


def user_has_name(user_id: int):
    return get_selected_name(user_id) is not None


def is_name_waiting(context: ContextTypes.DEFAULT_TYPE):
    return context.user_data.get("awaiting_new_name") is True


def build_main_menu(user_id: int):
    buttons = []

    if user_has_name(user_id):
        buttons.append([InlineKeyboardButton("📋 Начать смену", callback_data="choose_shift")])
        buttons.append([InlineKeyboardButton("👤 Сменить имя", callback_data="choose_name")])
    else:
        buttons.append([InlineKeyboardButton("👤 Выбрать имя", callback_data="choose_name")])

    if is_admin(user_id):
        buttons.append([InlineKeyboardButton("📊 Статус на сегодня", callback_data="admin_status")])
        buttons.append([InlineKeyboardButton("❗ Кто не отправил", callback_data="admin_not_sent")])
        buttons.append([InlineKeyboardButton("📝 Не прошли задачи", callback_data="admin_unfinished")])
        buttons.append([InlineKeyboardButton("📸 Фото-задачи", callback_data="admin_photo_tasks")])
        buttons.append([InlineKeyboardButton("📈 Статистика менеджера", callback_data="admin_stats_manager")])

    return InlineKeyboardMarkup(buttons)


def build_names_keyboard():
    names = get_all_people()
    buttons = [[InlineKeyboardButton(name, callback_data=f"pick_name|{name}")] for name in names]
    buttons.append([InlineKeyboardButton("➕ Новое имя", callback_data="add_new_name")])
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def build_shifts_keyboard():
    buttons = [[InlineKeyboardButton(shift, callback_data=f"start_shift|{shift}")] for shift in TASKS.keys()]
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def build_stats_manager_keyboard():
    names = get_all_people()
    buttons = [[InlineKeyboardButton(name, callback_data=f"stats_pick_manager|{name}")] for name in names]
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)


def build_task_keyboard(shift: str, task_index: int, photo_required: bool):
    if photo_required:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Отправить фотографию", callback_data=f"task_photo|{shift}|{task_index}")],
            [InlineKeyboardButton("❌ Не сделано", callback_data=f"task_fail|{shift}|{task_index}")]
        ])

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Сделано", callback_data=f"task_done|{shift}|{task_index}"),
            InlineKeyboardButton("❌ Не сделано", callback_data=f"task_fail|{shift}|{task_index}")
        ]
    ])


def build_back_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")]
    ])


def task_message_text(manager_name: str, shift: str, task_index: int):
    tasks_sorted = sorted_tasks_for_shift(shift)
    pos = next(i for i, t in enumerate(tasks_sorted) if t["original_index"] == task_index)
    task = tasks_sorted[pos]
    status = get_submission_status(manager_name, shift, task_index)

    status_line = ""
    if status:
        if status["employee_status"] == "Выполнено":
            if task["photo_required"] and status["photo_file_id"]:
                status_line = "\nСтатус: 📸✅ Фото отправлено"
            else:
                status_line = "\nСтатус: ✅ Сделано"
        elif status["employee_status"] == "Не выполнено":
            status_line = "\nСтатус: ❌ Не сделано"

    text = (
        f"👤 {manager_name}\n"
        f"🕐 {shift}\n\n"
        f"📌 Задача {pos + 1}\n"
        f"{task['name']}\n"
        f"⏰ Дедлайн: {task['deadline']}"
        f"{status_line}"
    )

    if task["photo_required"]:
        text += "\n📸 Нужно фото"

    return text


def status_today_text():
    summary = get_today_status_summary()
    if not summary:
        return "Сегодня пока ничего не отправлено."

    lines = [f"📊 Статус на сегодня ({today_str()})\n"]
    for (name, shift), data in summary.items():
        total = len(TASKS[shift])
        marked = data["done"] + data["not_done"]
        lines.append(
            f"👤 {name} | {shift}\n"
            f"Отмечено: {marked}/{total} | ✅ {data['done']} | ❌ {data['not_done']}"
        )
    return "\n\n".join(lines)


def not_sent_text():
    lines = [f"❗ Кто не отправил ({today_str()})\n"]
    has_any = False

    for shift in TASKS.keys():
        active_people = get_active_people_for_shift(shift)
        if not active_people:
            continue

        shift_lines = []
        for person in active_people:
            name = person["manager_name"]
            total = len(TASKS[shift])
            _, marked, _, _ = get_shift_progress(name, shift)
            if marked < total:
                shift_lines.append(f"— {name} | осталось {total - marked}")

        if shift_lines:
            has_any = True
            lines.append(f"🕐 {shift}:")
            lines.extend(shift_lines)
            lines.append("")

    if not has_any:
        return "✅ Все активные смены на сегодня закрыты."

    return "\n".join(lines)


def build_calendar_keyboard(year: int, month: int, mode: str):
    cal = calendar.monthcalendar(year, month)

    rows = []
    rows.append([
        InlineKeyboardButton("«", callback_data=f"cal_nav|{mode}|{year}|{month}|prev"),
        InlineKeyboardButton(f"{MONTH_NAMES_RU[month]} {year}", callback_data="cal_ignore"),
        InlineKeyboardButton("»", callback_data=f"cal_nav|{mode}|{year}|{month}|next"),
    ])

    rows.append([
        InlineKeyboardButton("Пн", callback_data="cal_ignore"),
        InlineKeyboardButton("Вт", callback_data="cal_ignore"),
        InlineKeyboardButton("Ср", callback_data="cal_ignore"),
        InlineKeyboardButton("Чт", callback_data="cal_ignore"),
        InlineKeyboardButton("Пт", callback_data="cal_ignore"),
        InlineKeyboardButton("Сб", callback_data="cal_ignore"),
        InlineKeyboardButton("Вс", callback_data="cal_ignore"),
    ])

    for week in cal:
        week_buttons = []
        for day in week:
            if day == 0:
                week_buttons.append(InlineKeyboardButton(" ", callback_data="cal_ignore"))
            else:
                d = date(year, month, day).strftime("%Y-%m-%d")
                week_buttons.append(InlineKeyboardButton(str(day), callback_data=f"cal_pick|{mode}|{d}"))
        rows.append(week_buttons)

    rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def shift_month(year: int, month: int, direction: str):
    if direction == "prev":
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    else:
        month += 1
        if month == 13:
            month = 1
            year += 1
    return year, month


async def send_next_task_message(chat_id: int, context: ContextTypes.DEFAULT_TYPE, manager_name: str, shift: str):
    tasks_sorted = sorted_tasks_for_shift(shift)
    state = get_flow_state(chat_id)
    next_pos = state["next_sorted_pos"] if state else 0

    if next_pos >= len(tasks_sorted):
        total, marked, done, not_done = get_shift_progress(manager_name, shift)
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"✅ Все задачи этой смены показаны\n\n"
                f"👤 {manager_name}\n"
                f"🕐 {shift}\n"
                f"Прогресс: {marked}/{total}\n"
                f"✅ Сделано: {done}\n"
                f"❌ Не сделано: {not_done}"
            ),
            reply_markup=build_back_main()
        )
        return

    task = tasks_sorted[next_pos]
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=task_message_text(manager_name, shift, task["original_index"]),
        reply_markup=build_task_keyboard(shift, task["original_index"], task["photo_required"])
    )
    set_flow_state(chat_id, manager_name, shift, next_pos + 1, msg.message_id)


async def finalize_current_task_message(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    manager_name: str,
    shift: str,
    task_index: int
):
    state = get_flow_state(chat_id)
    if not state or not state["current_message_id"]:
        return
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=state["current_message_id"],
            text=task_message_text(manager_name, shift, task_index),
            reply_markup=None
        )
    except Exception:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected_name = get_selected_name(user_id)

    text = "Меню"
    if selected_name:
        text += f"\n\nВаше имя: {selected_name}"

    if is_admin(user_id):
        text += "\nРоль: Управляющий"

    await update.message.reply_text(text, reply_markup=build_main_menu(user_id))


async def reset_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    delete_selected_name(user_id)
    await update.message.reply_text("Имя сброшено.", reply_markup=build_main_menu(user_id))


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "cal_ignore":
        return

    if data == "back_main":
        if is_admin(user_id):
            temp_media = get_admin_temp_media(user_id)
            for msg_id in temp_media:
                try:
                    await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                except Exception:
                    pass
            clear_admin_temp_media(user_id)

        selected_name = get_selected_name(user_id)
        text = "Меню"
        if selected_name:
            text += f"\n\nВаше имя: {selected_name}"
        if is_admin(user_id):
            text += "\nРоль: Управляющий"

        await query.edit_message_text(text, reply_markup=build_main_menu(user_id))
        return

    if data == "choose_name":
        await query.edit_message_text("Выберите имя:", reply_markup=build_names_keyboard())
        return

    if data == "add_new_name":
        context.user_data["awaiting_new_name"] = True
        await query.edit_message_text(
            "Напишите новое имя одним сообщением.\n\nПример: Aziza",
            reply_markup=build_back_main()
        )
        return

    if data.startswith("pick_name|"):
        name = data.split("|", 1)[1]
        save_selected_name(user_id, name)
        context.user_data["awaiting_new_name"] = False
        await query.edit_message_text(
            f"✅ Имя выбрано: {name}",
            reply_markup=build_main_menu(user_id)
        )
        return

    if data == "choose_shift":
        if not user_has_name(user_id):
            await query.edit_message_text("Сначала выберите имя.", reply_markup=build_names_keyboard())
            return
        await query.edit_message_text("Выберите смену:", reply_markup=build_shifts_keyboard())
        return

    if data.startswith("start_shift|"):
        shift = data.split("|", 1)[1]
        manager_name = get_selected_name(user_id)

        if not manager_name:
            await query.edit_message_text("Сначала выберите имя.", reply_markup=build_names_keyboard())
            return

        set_active_shift(manager_name, shift, user_id)
        set_flow_state(user_id, manager_name, shift, 0, None)
        await query.edit_message_text(f"Старт: {shift}")
        await send_next_task_message(user_id, context, manager_name, shift)
        return

    if data.startswith("task_done|"):
        _, shift, task_index = data.split("|")
        task_index = int(task_index)
        manager_name = get_selected_name(user_id)

        task_lookup = next(t for t in sorted_tasks_for_shift(shift) if t["original_index"] == task_index)

        save_submission(
            telegram_id=user_id,
            manager_name=manager_name,
            shift=shift,
            task_index=task_index,
            task_name=task_lookup["name"],
            deadline=task_lookup["deadline"],
            photo_required=task_lookup["photo_required"],
            employee_status="Выполнено",
        )

        await finalize_current_task_message(context, user_id, manager_name, shift, task_index)
        await send_next_task_message(user_id, context, manager_name, shift)
        return

    if data.startswith("task_fail|"):
        _, shift, task_index = data.split("|")
        task_index = int(task_index)
        manager_name = get_selected_name(user_id)

        task_lookup = next(t for t in sorted_tasks_for_shift(shift) if t["original_index"] == task_index)

        save_submission(
            telegram_id=user_id,
            manager_name=manager_name,
            shift=shift,
            task_index=task_index,
            task_name=task_lookup["name"],
            deadline=task_lookup["deadline"],
            photo_required=task_lookup["photo_required"],
            employee_status="Не выполнено",
        )

        await finalize_current_task_message(context, user_id, manager_name, shift, task_index)
        await send_next_task_message(user_id, context, manager_name, shift)
        return

    if data.startswith("task_photo|"):
        _, shift, task_index = data.split("|")
        task_index = int(task_index)
        manager_name = get_selected_name(user_id)

        set_pending_photo(
            telegram_id=user_id,
            manager_name=manager_name,
            shift=shift,
            task_index=task_index
        )

        await query.answer("Отправьте фото следующим сообщением", show_alert=True)
        return

    if data == "admin_status":
        if not is_admin(user_id):
            await query.edit_message_text("Нет доступа", reply_markup=build_back_main())
            return
        await query.edit_message_text(status_today_text(), reply_markup=build_back_main())
        return

    if data == "admin_not_sent":
        if not is_admin(user_id):
            await query.edit_message_text("Нет доступа", reply_markup=build_back_main())
            return
        await query.edit_message_text(not_sent_text(), reply_markup=build_back_main())
        return

    if data == "admin_unfinished":
        if not is_admin(user_id):
            await query.edit_message_text("Нет доступа", reply_markup=build_back_main())
            return
        await query.edit_message_text(unfinished_tasks_text(), reply_markup=build_back_main())
        return

    if data == "admin_photo_tasks":
        if not is_admin(user_id):
            await query.edit_message_text("Нет доступа", reply_markup=build_back_main())
            return

        temp_media = get_admin_temp_media(user_id)
        for msg_id in temp_media:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
            except Exception:
                pass
        clear_admin_temp_media(user_id)

        await query.edit_message_text(photo_tasks_text(), reply_markup=build_back_main())

        photo_items = get_photo_task_statuses()
        sent_any_photo = False

        for item in photo_items:
            if item["photo_file_id"]:
                sent_any_photo = True
                try:
                    msg = await context.bot.send_photo(
                        chat_id=user_id,
                        photo=item["photo_file_id"],
                        caption=(
                            f"👤 {item['name']} | {item['shift']}\n"
                            f"📌 {item['task_name']}"
                        )
                    )
                    save_admin_temp_media(user_id, msg.message_id)
                except Exception as e:
                    print(f"Ошибка отправки фото управляющему: {e}")

        if not sent_any_photo:
            try:
                msg = await context.bot.send_message(
                    chat_id=user_id,
                    text="Сегодня фото пока не отправляли."
                )
                save_admin_temp_media(user_id, msg.message_id)
            except Exception as e:
                print(f"Ошибка отправки сообщения управляющему: {e}")
        return

    if data == "admin_stats_manager":
        if not is_admin(user_id):
            await query.edit_message_text("Нет доступа", reply_markup=build_back_main())
            return
        await query.edit_message_text("Выберите менеджера:", reply_markup=build_stats_manager_keyboard())
        return

    if data.startswith("stats_pick_manager|"):
        if not is_admin(user_id):
            await query.edit_message_text("Нет доступа", reply_markup=build_back_main())
            return

        manager_name = data.split("|", 1)[1]
        context.user_data["stats_manager_name"] = manager_name
        today = now_dt().date()

        await query.edit_message_text(
            f"📅 Выберите дату начала\nМенеджер: {manager_name}",
            reply_markup=build_calendar_keyboard(today.year, today.month, "start")
        )
        return

    if data.startswith("cal_nav|"):
        _, mode, year, month, direction = data.split("|")
        year = int(year)
        month = int(month)
        year, month = shift_month(year, month, direction)

        title = "📅 Выберите дату начала" if mode == "start" else "📅 Выберите дату конца"
        manager_name = context.user_data.get("stats_manager_name", "")
        await query.edit_message_text(
            f"{title}\nМенеджер: {manager_name}",
            reply_markup=build_calendar_keyboard(year, month, mode)
        )
        return

    if data.startswith("cal_pick|"):
        _, mode, picked = data.split("|")

        if mode == "start":
            context.user_data["stats_date_from"] = picked
            picked_date = datetime.strptime(picked, "%Y-%m-%d").date()

            await query.edit_message_text(
                f"📅 Выберите дату конца\nМенеджер: {context.user_data.get('stats_manager_name', '')}\nНачало: {picked}",
                reply_markup=build_calendar_keyboard(picked_date.year, picked_date.month, "end")
            )
            return

        if mode == "end":
            manager_name = context.user_data.get("stats_manager_name")
            date_from = context.user_data.get("stats_date_from")
            date_to = picked

            if not manager_name or not date_from:
                await query.edit_message_text("Ошибка выбора периода.", reply_markup=build_back_main())
                return

            if date_to < date_from:
                await query.edit_message_text(
                    "Дата конца не может быть раньше даты начала.\nВыберите дату конца заново.",
                    reply_markup=build_calendar_keyboard(
                        datetime.strptime(date_from, "%Y-%m-%d").year,
                        datetime.strptime(date_from, "%Y-%m-%d").month,
                        "end"
                    )
                )
                return

            stats = get_manager_period_stats(manager_name, date_from, date_to)
            await query.edit_message_text(
                manager_stats_text(stats),
                reply_markup=build_back_main()
            )
            return


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    if text.startswith("/"):
        return

    if is_name_waiting(context):
        if len(text) < 2:
            await update.message.reply_text("Имя слишком короткое. Напишите нормальное имя.")
            return

        add_person(text)
        save_selected_name(user_id, text)
        context.user_data["awaiting_new_name"] = False

        await update.message.reply_text(
            f"✅ Новое имя добавлено: {text}",
            reply_markup=build_main_menu(user_id)
        )
        return

    pending = get_pending_photo(user_id)
    if pending:
        await update.message.reply_text("Сейчас бот ждёт фото по задаче, а не текст.")
        return

    await update.message.reply_text("Используйте кнопки в меню.", reply_markup=build_main_menu(user_id))


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pending = get_pending_photo(user_id)

    if not pending:
        await update.message.reply_text("Сейчас бот не ожидает фото.")
        return

    shift = pending["shift"]
    task_index = pending["task_index"]
    manager_name = pending["manager_name"]
    task_lookup = next(t for t in sorted_tasks_for_shift(shift) if t["original_index"] == task_index)

    photo = update.message.photo[-1]
    file_id = photo.file_id

    save_submission(
        telegram_id=user_id,
        manager_name=manager_name,
        shift=shift,
        task_index=task_index,
        task_name=task_lookup["name"],
        deadline=task_lookup["deadline"],
        photo_required=True,
        employee_status="Выполнено",
        photo_file_id=file_id,
    )

    clear_pending_photo(user_id)

    await finalize_current_task_message(context, user_id, manager_name, shift, task_index)
    await update.message.reply_text("✅ Фото принято")
    await send_next_task_message(user_id, context, manager_name, shift)


async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    current = now_hm()

    for shift in TASKS.keys():
        active_people = get_active_people_for_shift(shift)
        tasks_sorted = sorted_tasks_for_shift(shift)

        for pos, task in enumerate(tasks_sorted):
            reminder_time = minus_minutes(task["deadline"], 5)

            if current == reminder_time:
                for person in active_people:
                    manager_name = person["manager_name"]
                    telegram_id = person["telegram_id"]

                    if was_notification_sent("manager_task_reminder", shift, task["original_index"], manager_name):
                        continue

                    submitted = get_submitted_task_indexes(manager_name, shift)
                    if task["original_index"] not in submitted:
                        try:
                            await context.bot.send_message(
                                chat_id=telegram_id,
                                text=(
                                    f"⏰ Напоминание\n\n"
                                    f"👤 {manager_name}\n"
                                    f"🕐 {shift}\n"
                                    f"📌 {task['name']}\n"
                                    f"До дедлайна осталось 5 минут.\n"
                                    f"Дедлайн: {task['deadline']}"
                                )
                            )
                        except Exception as e:
                            print(f"Ошибка напоминания менеджеру {manager_name}: {e}")

                    mark_notification_sent("manager_task_reminder", shift, task["original_index"], manager_name)

            if current == task["deadline"] and not was_notification_sent("admin_task_deadline", shift, task["original_index"], None):
                missed_people = []

                for person in active_people:
                    manager_name = person["manager_name"]
                    submitted = get_submitted_task_indexes(manager_name, shift)
                    if task["original_index"] not in submitted:
                        missed_people.append(manager_name)

                if missed_people:
                    text_lines = [
                        "❗ Не отправили задачу",
                        "",
                        f"🕐 {shift}",
                        f"📌 {task['name']}",
                        f"⏰ Дедлайн: {task['deadline']}",
                        ""
                    ]
                    for name in missed_people:
                        text_lines.append(f"— {name}")
                    text = "\n".join(text_lines)
                else:
                    text = (
                        f"✅ Все отправили вовремя\n\n"
                        f"🕐 {shift}\n"
                        f"📌 {task['name']}\n"
                        f"⏰ Дедлайн: {task['deadline']}"
                    )

                for admin_id in ADMINS:
                    try:
                        await context.bot.send_message(chat_id=admin_id, text=text)
                    except Exception as e:
                        print(f"Ошибка уведомления админу {admin_id}: {e}")

                mark_notification_sent("admin_task_deadline", shift, task["original_index"], None)


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resetname", reset_name))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    if app.job_queue is not None:
        app.job_queue.run_repeating(reminder_job, interval=60, first=10)

    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
