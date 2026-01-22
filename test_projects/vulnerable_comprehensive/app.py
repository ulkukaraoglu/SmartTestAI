"""
Kapsamlı Güvenlik Açıkları Test Projesi
Bu proje kasıtlı olarak çeşitli güvenlik açıkları içerir.
Tüm güvenlik açıklarını test etmek için tasarlanmıştır.
"""
from flask import Flask, request, jsonify, send_file, render_template_string
import sqlite3
import subprocess
import os
import hashlib
import pickle
import random
import requests
import json
from urllib.parse import urlparse

app = Flask(__name__)

# ============================================
# VULNERABILITY 1: Hardcoded Credentials
# Ground Truth: Line 18-20 - Hardcoded credentials
# ============================================
DATABASE_PASSWORD = "super_secret_password_123"
API_KEY = "sk_test_FAKE_KEY_FOR_TESTING_ONLY_123456789"  # Test amaçlı fake key
SECRET_KEY = "my_secret_key_never_change_this"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ============================================
# VULNERABILITY 2: SQL Injection
# Ground Truth: Line 35, 48, 62 - SQL Injection
# ============================================
def get_db():
    conn = sqlite3.connect('test.db')
    return conn

@app.route("/")
def index():
    return """
    <h1>Comprehensive Vulnerability Test App</h1>
    <p>Bu uygulama çeşitli güvenlik açıkları içerir.</p>
    <ul>
        <li>/user/&lt;id&gt; - SQL Injection</li>
        <li>/search?q=&lt;query&gt; - SQL Injection</li>
        <li>/comment?text=&lt;text&gt; - XSS</li>
        <li>/ping?host=&lt;host&gt; - Command Injection</li>
        <li>/file?name=&lt;filename&gt; - Path Traversal</li>
        <li>/login?user=&lt;user&gt;&password=&lt;pass&gt; - Weak Hashing</li>
        <li>/deserialize?data=&lt;pickle&gt; - Insecure Deserialization</li>
        <li>/fetch?url=&lt;url&gt; - SSRF</li>
        <li>/api?key=&lt;key&gt; - Hardcoded Credentials</li>
        <li>/random - Insecure Random</li>
        <li>/debug - Information Disclosure</li>
    </ul>
    """

@app.route("/user/<user_id>")
def get_user(user_id):
    """
    SQL Injection açığı: user_id parametresi doğrudan SQL sorgusuna ekleniyor
    Ground Truth: Line 35 - SQL Injection açığı
    """
    conn = get_db()
    cursor = conn.cursor()
    # VULNERABLE: SQL Injection açığı
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return jsonify({"user": str(result) if result else "User not found"})

@app.route("/search")
def search_users():
    """
    SQL Injection açığı: search parametresi doğrudan SQL sorgusuna ekleniyor
    Ground Truth: Line 48 - SQL Injection açığı
    """
    search_term = request.args.get('q', '')
    conn = get_db()
    cursor = conn.cursor()
    # VULNERABLE: SQL Injection açığı
    query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%' OR email LIKE '%{search_term}%'"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return jsonify({"results": results})

@app.route("/user_by_email")
def get_user_by_email():
    """
    SQL Injection açığı: email parametresi doğrudan SQL sorgusuna ekleniyor
    Ground Truth: Line 62 - SQL Injection açığı
    """
    email = request.args.get('email', '')
    conn = get_db()
    cursor = conn.cursor()
    # VULNERABLE: SQL Injection açığı
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return jsonify({"user": str(result) if result else "User not found"})

# ============================================
# VULNERABILITY 3: XSS (Cross-Site Scripting)
# Ground Truth: Line 75, 87, 99 - XSS
# ============================================
@app.route("/comment")
def add_comment():
    """
    XSS açığı: user input doğrudan HTML'e ekleniyor
    Ground Truth: Line 75 - XSS açığı
    """
    comment = request.args.get('text', '')
    # VULNERABLE: XSS açığı - input sanitize edilmiyor
    template = f"""
    <html>
    <head><title>Comments</title></head>
    <body>
        <h1>Your comment:</h1>
        <p>{comment}</p>
    </body>
    </html>
    """
    return render_template_string(template)

@app.route("/search_page")
def search_page():
    """
    XSS açığı: search parametresi doğrudan HTML'e ekleniyor
    Ground Truth: Line 87 - XSS açığı
    """
    query = request.args.get('q', '')
    # VULNERABLE: XSS açığı
    return f"""
    <html>
    <body>
        <h1>Search Results</h1>
        <p>Search results for: {query}</p>
    </body>
    </html>
    """

@app.route("/profile")
def profile():
    """
    XSS açığı: username parametresi doğrudan HTML'e ekleniyor
    Ground Truth: Line 99 - XSS açığı
    """
    username = request.args.get('user', '')
    # VULNERABLE: XSS açığı
    return f"""
    <html>
    <body>
        <h2>Welcome, {username}!</h2>
        <p>Your profile information</p>
    </body>
    </html>
    """

# ============================================
# VULNERABILITY 4: Command Injection
# Ground Truth: Line 112, 125 - Command Injection
# ============================================
@app.route("/ping")
def ping_host():
    """
    Command Injection açığı: host parametresi doğrudan shell komutuna ekleniyor
    Ground Truth: Line 112 - Command Injection açığı
    """
    host = request.args.get('host', 'localhost')
    # VULNERABLE: Command Injection açığı
    result = subprocess.run(f"ping -c 4 {host}", shell=True, capture_output=True, text=True)
    return f"<pre>{result.stdout}</pre>"

@app.route("/execute")
def execute_command():
    """
    Command Injection açığı: command parametresi doğrudan shell komutuna ekleniyor
    Ground Truth: Line 125 - Command Injection açığı
    """
    command = request.args.get('cmd', '')
    # VULNERABLE: Command Injection açığı
    result = os.system(command)
    return f"Command executed with exit code: {result}"

# ============================================
# VULNERABILITY 5: Path Traversal
# Ground Truth: Line 138, 150 - Path Traversal
# ============================================
@app.route("/file")
def read_file():
    """
    Path Traversal açığı: filename parametresi doğrudan dosya okuma işleminde kullanılıyor
    Ground Truth: Line 138 - Path Traversal açığı
    """
    filename = request.args.get('name', '')
    # VULNERABLE: Path Traversal açığı
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/download")
def download_file():
    """
    Path Traversal açığı: filename parametresi doğrudan dosya indirme işleminde kullanılıyor
    Ground Truth: Line 150 - Path Traversal açığı
    """
    filename = request.args.get('file', '')
    # VULNERABLE: Path Traversal açığı
    return send_file(filename)

# ============================================
# VULNERABILITY 6: Weak Hashing & Hardcoded Credentials
# Ground Truth: Line 163, 175, 188 - Weak Hashing, Hardcoded Credentials
# ============================================
@app.route("/login")
def login():
    """
    Weak password hashing: MD5 kullanımı ve hardcoded credentials
    Ground Truth: Line 163 - Weak hashing algorithm açığı
    """
    username = request.args.get('user', '')
    password = request.args.get('password', '')
    # VULNERABLE: MD5 zayıf bir hash algoritması
    hashed = hashlib.md5(password.encode()).hexdigest()
    # VULNERABLE: Hardcoded credentials
    stored_hash = hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()
    
    if username == ADMIN_USERNAME and hashed == stored_hash:
        return "Login successful"
    return "Login failed"

@app.route("/api")
def api_endpoint():
    """
    Hardcoded API key kullanımı
    Ground Truth: Line 175 - Hardcoded API key açığı
    """
    api_key = request.headers.get('X-API-Key', '') or request.args.get('key', '')
    # VULNERABLE: Hardcoded API key
    if api_key == API_KEY:
        return jsonify({"status": "API access granted", "data": "sensitive_data_here"})
    return jsonify({"status": "API access denied"})

@app.route("/database_connect")
def database_connect():
    """
    Hardcoded database password kullanımı
    Ground Truth: Line 188 - Hardcoded credentials açığı
    """
    # VULNERABLE: Hardcoded database password
    connection_string = f"postgresql://user:{DATABASE_PASSWORD}@localhost/db"
    return jsonify({"connection": connection_string, "status": "connected"})

# ============================================
# VULNERABILITY 7: Insecure Deserialization
# Ground Truth: Line 201 - Insecure Deserialization
# ============================================
@app.route("/deserialize")
def deserialize_data():
    """
    Insecure Deserialization açığı: pickle kullanımı
    Ground Truth: Line 201 - Insecure Deserialization açığı
    """
    data = request.args.get('data', '')
    # VULNERABLE: Insecure Deserialization - pickle güvenli değil
    try:
        decoded = data.encode('latin1')
        obj = pickle.loads(decoded)
        return jsonify({"deserialized": str(obj)})
    except Exception as e:
        return jsonify({"error": str(e)})

# ============================================
# VULNERABILITY 8: SSRF (Server-Side Request Forgery)
# Ground Truth: Line 214 - SSRF
# ============================================
@app.route("/fetch")
def fetch_url():
    """
    SSRF açığı: URL parametresi doğrudan HTTP isteğinde kullanılıyor
    Ground Truth: Line 214 - SSRF açığı
    """
    url = request.args.get('url', '')
    # VULNERABLE: SSRF açığı - URL doğrulanmıyor
    try:
        response = requests.get(url, timeout=5)
        return jsonify({
            "url": url,
            "status_code": response.status_code,
            "content": response.text[:500]
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# ============================================
# VULNERABILITY 9: Insecure Random
# Ground Truth: Line 228 - Insecure Random
# ============================================
@app.route("/random")
def generate_random():
    """
    Insecure Random açığı: random modülü kriptografik olarak güvenli değil
    Ground Truth: Line 228 - Insecure Random açığı
    """
    # VULNERABLE: random modülü kriptografik olarak güvenli değil
    token = ''.join([str(random.randint(0, 9)) for _ in range(32)])
    session_id = random.randint(1000, 9999)
    return jsonify({
        "token": token,
        "session_id": session_id,
        "warning": "Using insecure random for sensitive data"
    })

# ============================================
# VULNERABILITY 10: Information Disclosure
# Ground Truth: Line 242, 254 - Information Disclosure
# ============================================
@app.route("/debug")
def debug_info():
    """
    Information Disclosure açığı: Debug bilgileri production'da açık
    Ground Truth: Line 242 - Information Disclosure açığı
    """
    # VULNERABLE: Debug mode production'da açık
    debug_info = {
        "app_name": "Comprehensive Vulnerability Test",
        "version": "1.0.0",
        "debug_mode": True,
        "database_password": DATABASE_PASSWORD,  # VULNERABLE: Sensitive info exposed
        "api_key": API_KEY,  # VULNERABLE: Sensitive info exposed
        "environment": "production",
        "stack_trace": "Full stack trace here..."
    }
    return jsonify(debug_info)

@app.route("/error")
def error_handler():
    """
    Information Disclosure açığı: Hata mesajları çok detaylı
    Ground Truth: Line 254 - Information Disclosure açığı
    """
    try:
        # Simulated error
        result = 1 / 0
    except Exception as e:
        # VULNERABLE: Full exception details exposed
        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "traceback": str(e.__traceback__),
            "file_path": __file__,
            "line_number": 260
        })

# ============================================
# VULNERABILITY 11: Insecure Direct Object Reference
# Ground Truth: Line 268 - IDOR
# ============================================
@app.route("/user_data/<user_id>")
def get_user_data(user_id):
    """
    Insecure Direct Object Reference açığı: Authorization kontrolü yok
    Ground Truth: Line 268 - IDOR açığı
    """
    # VULNERABLE: Authorization kontrolü yok
    conn = get_db()
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return jsonify({
        "user_id": user_id,
        "data": result,
        "message": "No authorization check performed"
    })

# ============================================
# VULNERABILITY 12: CORS Misconfiguration
# Ground Truth: Line 283 - CORS Misconfiguration
# ============================================
@app.route("/api/cors")
def cors_endpoint():
    """
    CORS Misconfiguration açığı: Tüm origin'lere izin veriliyor
    Ground Truth: Line 283 - CORS Misconfiguration açığı
    """
    from flask_cors import cross_origin
    # VULNERABLE: CORS tüm origin'lere açık
    response = jsonify({"data": "sensitive_data", "status": "ok"})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

# ============================================
# VULNERABILITY 13: Weak Cryptography
# Ground Truth: Line 297 - Weak Cryptography
# ============================================
@app.route("/encrypt")
def encrypt_data():
    """
    Weak Cryptography açığı: XOR şifreleme kullanımı
    Ground Truth: Line 297 - Weak Cryptography açığı
    """
    data = request.args.get('data', '')
    key = "weak_key_123"  # VULNERABLE: Weak encryption key
    
    # VULNERABLE: XOR şifreleme güvenli değil
    encrypted = ''.join([chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data)])
    return jsonify({
        "encrypted": encrypted,
        "method": "XOR",
        "warning": "Weak encryption method used"
    })

if __name__ == "__main__":
    # VULNERABLE: Debug mode production'da açık
    app.run(host="0.0.0.0", port=5000, debug=True)

