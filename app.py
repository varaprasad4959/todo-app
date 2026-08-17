from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "todo.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def home():
    conn = get_db()

    if request.method == "POST":
        title = request.form["title"].strip()

        if title:
            conn.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (title,)
            )
            conn.commit()

        conn.close()
        return redirect(url_for("home"))

    tasks = conn.execute(
        "SELECT * FROM tasks ORDER BY id DESC"
    ).fetchall()

    total = len(tasks)
    completed = sum(task["completed"] for task in tasks)
    pending = total - completed

    conn.close()

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending
    )


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    conn = get_db()

    task = conn.execute(
        "SELECT completed FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task:
        new_status = 0 if task["completed"] else 1

        conn.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (new_status, task_id)
        )
        conn.commit()

    conn.close()
    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    title = request.form.get("title", "").strip()

    if title:
        conn = get_db()

        conn.execute(
            "UPDATE tasks SET title = ? WHERE id = ?",
            (title, task_id)
        )

        conn.commit()
        conn.close()

    return redirect(url_for("home"))


@app.route("/clear-completed")
def clear_completed():
    conn = get_db()

    conn.execute(
        "DELETE FROM tasks WHERE completed = 1"
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


init_db()


if __name__ == "__main__":
    app.run(debug=True)