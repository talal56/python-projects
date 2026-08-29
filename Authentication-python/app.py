from flask import Flask, request, render_template
import pyodbc
import re

app = Flask(__name__)

SERVER = r"localhost\NOVA"
DATABASE = "loginSys"


def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username NVARCHAR(100) NOT NULL,
            email NVARCHAR(150) NOT NULL UNIQUE,
            password NVARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=~`\[\]/;']", password):
        return False
    return True


@app.route("/", methods=["GET"])
def home():
    return render_template("register.html", message=None)


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("pass")
    confirm_password = request.form.get("confirm")

    if not username or not email or not password:
        return render_template("register.html", message="All fields are required.")

    if password != confirm_password:
        return render_template("register.html", message="Passwords do not match.")

    if not is_valid_password(password):
        return render_template(
            "register.html",
            message="Password must be at least 8 characters, contain 1 uppercase letter and 1 special character."
        )

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return render_template("register.html", message="An account with that email already exists.")

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    # After successful signup, send them to the login page
    return render_template("login.html", message="Account created! Please log in.")




@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html", message=None)


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("pass")

    if not email or not password:
        return render_template("login.html", message="Both fields are required.")

    conn = get_connection()
    cursor = conn.cursor()
    try:
     
        cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if user is None:
        return render_template("login.html", message="No account found with that email.")

    stored_username, stored_password = user

    # Compare the submitted password to the one stored in the database
    if password != stored_password:
        return render_template("login.html", message="Incorrect password.")

    # Success — in a real app you'd set up a session here
    return f"<h2>Welcome back, {stored_username}!</h2><a href='/'>Go to homepage</a>"


if __name__ == "__main__":
    init_db()
    app.run(debug=True)