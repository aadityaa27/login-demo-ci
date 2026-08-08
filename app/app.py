from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "demo-secret-key-change-in-real-app"

# Simple in-memory "user database" for demo purposes
USERS = {
    "admin": "password123",
    "aditya": "qatester1",
}

MAX_ATTEMPTS = 3


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Username and password are required."
        elif username in USERS and USERS[username] == password:
            session["user"] = username
            session["attempts"] = 0
            return redirect(url_for("dashboard"))
        else:
            session["attempts"] = session.get("attempts", 0) + 1
            remaining = MAX_ATTEMPTS - session["attempts"]
            if remaining <= 0:
                error = "Account locked after too many failed attempts."
            else:
                error = f"Invalid username or password. {remaining} attempt(s) left."

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["user"])


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
