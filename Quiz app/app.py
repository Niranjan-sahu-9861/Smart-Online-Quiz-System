from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3, random, time
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register_page")
def register_page():
    return render_template("register.html")


app = Flask(__name__)
app.secret_key = "quiz_secret"
@app.route("/submit_quiz/<int:quiz_id>", methods=["POST"])
def submit_quiz(quiz_id):
    conn = get_db()
    c = conn.cursor()

    # get all questions of this quiz
    c.execute("SELECT id, correct, weight FROM questions WHERE quiz_id=?", (quiz_id,))
    questions = c.fetchall()

    score = 0
    total = 0

    for q in questions:
        q_id, correct, weight = q
        total += weight

        user_ans = request.form.get(f"q{q_id}")

        if user_ans is not None and int(user_ans) == correct:
            score += weight

    # save attempt
    c.execute("INSERT INTO attempts(username, quiz_id, score, time_taken) VALUES(?,?,?,?)",
              (session["user"], quiz_id, score, 0))
    conn.commit()
    conn.close()

    return f"<h2>Your Score: {score} / {total}</h2><a href='/dashboard'>Go Back</a>"


# -------- DATABASE SETUP ----------
def get_db():
    conn = sqlite3.connect("database.db")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS quizzes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        time_limit INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER,
        text TEXT,
        opt1 TEXT, opt2 TEXT, opt3 TEXT, opt4 TEXT,
        correct INTEGER,
        weight INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS attempts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        quiz_id INTEGER,
        score INTEGER,
        time_taken REAL
    )
    """)

    conn.commit()

    # --- Seed a sample quiz if none exist (so "View Quizzes" never empty) ---
    c.execute("SELECT COUNT(*) FROM quizzes")
    count = c.fetchone()[0]
    if count == 0:
        c.execute("INSERT INTO quizzes(title, time_limit) VALUES(?,?)",
                  ("Sample Python Quiz", 60))
        quiz_id = c.lastrowid
        # Add couple of sample questions
        c.execute("""INSERT INTO questions(quiz_id, text, opt1, opt2, opt3, opt4, correct, weight)
                     VALUES(?,?,?,?,?,?,?,?)""",
                  (quiz_id, "What is the keyword to define a function in Python?", "func", "define", "def", "fn", 2, 1))
        c.execute("""INSERT INTO questions(quiz_id, text, opt1, opt2, opt3, opt4, correct, weight)
                     VALUES(?,?,?,?,?,?,?,?)""",
                  (quiz_id, "Which data type is immutable?", "list", "dict", "set", "tuple", 3, 1))
        conn.commit()

    # Seed default admin if not present
    c.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", ("admin","123","admin"))
        conn.commit()

    conn.close()

init_db()

# -------- ROUTES ----------
@app.route("/")
def root():
    # Landing page: single big button
    return redirect(url_for("landing"))

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/do_login", methods=["POST"])
def do_login():
    username = request.form["username"].strip()
    password = request.form["password"].strip()

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session["user"] = username
        session["role"] = user[3]
        flash("Logged in successfully!", "success")
        return redirect("/dashboard")
    else:
        flash("Invalid credentials!", "danger")
        return redirect("/login")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"].strip()
    password = request.form["password"].strip()
    role = request.form.get("role","student")

    # Server-side validation (restrictions)
    if len(username) < 4:
        flash("Username must be at least 4 characters.", "danger")
        return redirect("/login")
    if len(password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                   (username,password,role))
        conn.commit()
        flash("Registered Successfully! Please login.", "success")
    except Exception as e:
        flash("Username already exists!", "danger")
    conn.close()
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", role=session.get("role"))

@app.route("/quizzes")
def quizzes():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, title, time_limit FROM quizzes")
    all_quizzes = c.fetchall()
    conn.close()
    return render_template("quiz_list.html", quizzes=all_quizzes)

@app.route("/take/<int:quiz_id>")
def take_quiz(quiz_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE quiz_id=?", (quiz_id,))
    questions = c.fetchall()
    conn.close()
    random.shuffle(questions)
    return render_template("take_quiz.html", questions=questions, quiz_id=quiz_id)

# --- Admin: create quiz & add question ---
@app.route("/create_quiz", methods=["GET","POST"])
def create_quiz():
    if session.get("role") != "admin":
        flash("Only admin can create quizzes.", "danger")
        return redirect("/dashboard")
    if request.method == "POST":
        title = request.form["title"].strip()
        try:
            time_limit = int(request.form["time_limit"])
        except:
            time_limit = 60
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO quizzes(title,time_limit) VALUES(?,?)", (title,time_limit))
        conn.commit()
        quiz_id = c.lastrowid
        conn.close()
        flash("Quiz created! Add questions now.", "success")
        return redirect(url_for("add_question", quiz_id=quiz_id))
    return render_template("create_quiz.html")

@app.route("/add_question/<int:quiz_id>", methods=["GET","POST"])
def add_question(quiz_id):
    if session.get("role") != "admin":
        flash("Only admin can add questions.", "danger")
        return redirect("/dashboard")
    if request.method == "POST":
        text = request.form["text"].strip()
        opt1 = request.form["opt1"].strip()
        opt2 = request.form["opt2"].strip()
        opt3 = request.form["opt3"].strip()
        opt4 = request.form["opt4"].strip()
        try:
            correct = int(request.form["correct"])
        except:
            correct = 1
        try:
            weight = int(request.form.get("weight",1))
        except:
            weight = 1
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO questions(quiz_id, text, opt1, opt2, opt3, opt4, correct, weight)
                     VALUES(?,?,?,?,?,?,?,?)""", (quiz_id, text, opt1, opt2, opt3, opt4, correct-1, weight))
        conn.commit()
        conn.close()
        flash("Question added.", "success")
        return redirect(url_for("add_question", quiz_id=quiz_id))
    return render_template("add_question.html", quiz_id=quiz_id)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect("/landing")

if __name__ == "__main__":
    app.run(debug=True)
