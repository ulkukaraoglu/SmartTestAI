"""
Örnek Test Uygulaması - Web Arayüzünden Yüklemek İçin

Bu dosyayı web arayüzünden yükleyerek gelişmiş metrikleri test edebilirsiniz.
Bu uygulama kasıtlı olarak güvenlik açıkları içerir.
"""

from flask import Flask, request, render_template_string
import sqlite3
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)

# Hardcoded credentials (Ground Truth: Line 8-9)
# Note: These are loaded from .env file for security
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
API_KEY = os.getenv("API_KEY", "sk_live_1234567890abcdef")

@app.route("/")
def index():
    return "Test Uygulaması - Güvenlik Açıkları Testi"

@app.route("/user/<user_id>")
def get_user(user_id):
    """
    SQL Injection açığı: user_id parametresi doğrudan SQL sorgusuna ekleniyor
    Ground Truth: Line 20 - SQL Injection açığı (high severity)
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # VULNERABLE: SQL Injection açığı
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return str(result) if result else "User not found"

@app.route("/search")
def search():
    """
    XSS açığı: search parametresi doğrudan HTML'e ekleniyor
    Ground Truth: Line 35 - XSS açığı (medium severity)
    """
    search_term = request.args.get('q', '')
    html = f"<h1>Arama Sonuçları</h1><p>Aradığınız: {search_term}</p>"
    return html

@app.route("/ping")
def ping():
    """
    Command Injection açığı: host parametresi doğrudan shell komutuna ekleniyor
    Ground Truth: Line 47 - Command Injection açığı (critical severity)
    """
    host = request.args.get('host', 'localhost')
    # VULNERABLE: Command Injection açığı
    result = subprocess.run(f"ping -c 4 {host}", shell=True, capture_output=True, text=True)
    return result.stdout

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

