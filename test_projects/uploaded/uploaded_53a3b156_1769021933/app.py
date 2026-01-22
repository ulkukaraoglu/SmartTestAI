"""
Test Senaryosu 1: SQL Injection Açığı
Bu proje kasıtlı olarak SQL injection açığı içerir.
"""
from flask import Flask, request
import sqlite3

app = Flask(__name__)

# Veritabanı bağlantısı
def get_db():
    conn = sqlite3.connect('users.db')
    return conn

@app.route("/")
def index():
    return "SQL Injection Test App"

@app.route("/user/<user_id>")
def get_user(user_id):
    """
    SQL Injection açığı: user_id parametresi doğrudan SQL sorgusuna ekleniyor
    Ground Truth: Line 20 - SQL Injection açığı
    """
    conn = get_db()
    cursor = conn.cursor()
    # VULNERABLE: SQL Injection açığı
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return str(result) if result else "User not found"

@app.route("/search")
def search_users():
    """
    SQL Injection açığı: search parametresi doğrudan SQL sorgusuna ekleniyor
    Ground Truth: Line 33 - SQL Injection açığı
    """
    search_term = request.args.get('q', '')
    conn = get_db()
    cursor = conn.cursor()
    # VULNERABLE: SQL Injection açığı
    query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return str(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

