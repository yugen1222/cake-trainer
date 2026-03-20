# app.py
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

from cake_simulator.generator import generate_game_state
from cake_simulator.database import (
    init_db,
    save_result,
    get_results_by_employee,
    get_last_results,
    get_top_employees,
    get_employee_summary,
)

app = Flask(__name__)
app.secret_key = "CHANGE_ME_TO_SOMETHING_RANDOM_123"

init_db()


@app.get("/")
def login():
    top_employees = get_top_employees(5)
    last_results = get_last_results(5)
    return render_template(
        "login.html",
        top_employees=top_employees,
        last_results=last_results
    )


@app.post("/start")
def start():
    name = (request.form.get("name") or "").strip()
    shift = (request.form.get("shift") or "").strip()

    if not name:
        name = "Сотрудник"
    if shift not in ["1", "2", "3"]:
        shift = "1"

    session["name"] = name
    session["shift"] = shift

    if "recent_seeds" not in session:
        session["recent_seeds"] = []

    return redirect(url_for("menu"))


@app.get("/menu")
def menu():
    if "name" not in session:
        return redirect(url_for("login"))

    summary = get_employee_summary(session["name"])
    top_employees = get_top_employees(5)
    last_results = get_last_results(5)

    return render_template(
        "menu.html",
        name=session["name"],
        shift=session["shift"],
        summary=summary,
        top_employees=top_employees,
        last_results=last_results
    )


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/game/<int:mode>")
def game(mode: int):
    if "name" not in session:
        return redirect(url_for("login"))

    if mode not in [1, 2, 3, 4]:
        mode = 1

    state = generate_game_state(
        mode=mode,
        recent_seeds=session.get("recent_seeds", [])
    )

    recent = session.get("recent_seeds", [])
    recent.append(state["seed"])
    session["recent_seeds"] = recent[-15:]

    return render_template(
        "game.html",
        user_name=session["name"],
        shift=session["shift"],
        mode=mode,
        state=state
    )


@app.get("/restart/<int:mode>")
def restart(mode: int):
    return redirect(url_for("game", mode=mode))


@app.post("/save_result")
def save_result_route():
    if "name" not in session:
        return jsonify({"ok": False, "error": "not_logged_in"}), 401

    data = request.get_json(silent=True) or {}

    try:
        mode = int(data.get("mode", 1))
        score_percent = int(data.get("score_percent", 0))
        errors_count = int(data.get("errors_count", 0))
        seed = data.get("seed")
        if seed is not None:
            seed = int(seed)
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "bad_payload"}), 400

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_result(
        employee_name=session["name"],
        shift=session["shift"],
        mode=mode,
        score_percent=score_percent,
        errors_count=errors_count,
        seed=seed,
        created_at=created_at
    )

    return jsonify({"ok": True})


@app.get("/results")
def results():
    if "name" not in session:
        return redirect(url_for("login"))

    employee_results = get_results_by_employee(session["name"])
    last_results = get_last_results(20)
    top_employees = get_top_employees(20)
    summary = get_employee_summary(session["name"])

    return render_template(
        "results.html",
        user_name=session["name"],
        shift=session["shift"],
        employee_results=employee_results,
        last_results=last_results,
        top_employees=top_employees,
        summary=summary
    )


if __name__ == "__main__":
    app.run(debug=True)
