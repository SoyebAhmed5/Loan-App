from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "loans.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS application (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT,
                         income INTEGER,
                         credit_score INTEGER,
                         loan_amount INTEGER,
                         status TEXT,
                         reason TEXT
                    )""")
    print("Database initialized")
    
    
def evaluate_application(income, credit_score, loan_amount):
    """Apply static rules to approve/reject loan."""
    if income >= 35000 and credit_score >= 650 and loan_amount <= 5 * income:
        return "Approved", "Meets all conditions"
    else:
        reasons = []
        if income < 35000:
            reasons.append("Income too low (< 35000)")
        if credit_score < 650:
            reasons.append("Credit score too low (< 650)")
        if loan_amount > 5 * income:
            reasons.append("Loan amount exceeds 5x income")
        return "Rejected", "; ".join(reasons)
    
    
@app.route("/")
def home():
    return redirect(url_for("list_applications"))


@app.route("/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        name = request.form["name"]
        income = int(request.form["income"])
        credit_score = int(request.form["credit_score"])
        loan_amount = int(request.form["loan_amount"])
        
        status, reason = evaluate_application(income, credit_score, loan_amount)
        
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                         "INSERT INTO application (name, income, credit_score, loan_amount, status, reason)VALUES (?, ?, ?, ?, ?, ?)",
                         (name, income, credit_score, loan_amount, status, reason),
                        )
        return redirect(url_for("list_applications"))
    return render_template("add.html")


@app.route("/applications")
def list_applications():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT * FROM application")
        apps = cursor.fetchall()
    return render_template("list.html", apps=apps)


@app.route("/edit/<int:app_id>", methods=["GET", "POST"])
def edit_application(app_id):
    with sqlite3.connect(DB_NAME) as conn:
        if request.method == "POST":
            name = request.form["name"]
            income = int(request.form["income"])
            credit_score = int(request.form["credit_score"])
            loan_amount = int(request.form["loan_amount"])
            
            status, reason = evaluate_application(income, credit_score, loan_amount)
            
            # with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "UPDATE application SET name=?, income=?, credit_score=?, loan_amount=?, status=?, reason=? WHERE id=?",
                            (name, income, credit_score, loan_amount, status, reason, app_id),
                            )
            return redirect(url_for("list_applications"))
        
        cursor = conn.execute("SELECT * FROM application WHERE id=?", (app_id,))
        app_data = cursor.fetchone()  
    return render_template("edit.html", app=app_data)

@app.route("/delete/<int:app_id>")
def delete_application(app_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM application WHERE id=?", (app_id,))
    return redirect(url_for("list_applications"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
