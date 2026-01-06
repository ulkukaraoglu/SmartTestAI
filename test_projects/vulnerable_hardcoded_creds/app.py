"""
Test Senaryosu 4: Hardcoded Credentials ve Güvenlik Açıkları
Bu proje kasıtlı olarak hardcoded credentials ve diğer güvenlik açıkları içerir.
"""
from flask import Flask, request
import hashlib

app = Flask(__name__)

# VULNERABLE: Hardcoded credentials
# Ground Truth: Line 8-9 - Hardcoded credentials açığı
DATABASE_PASSWORD = "admin123"
API_KEY = "sk_live_1234567890abcdef"

@app.route("/")
def index():
    return "Hardcoded Credentials Test App"

@app.route("/login")
def login():
    """
    Weak password hashing: MD5 kullanımı
    Ground Truth: Line 20 - Weak hashing algorithm açığı
    """
    password = request.args.get('password', '')
    # VULNERABLE: MD5 zayıf bir hash algoritması
    hashed = hashlib.md5(password.encode()).hexdigest()
    stored_hash = hashlib.md5("admin123".encode()).hexdigest()
    
    if hashed == stored_hash:
        return "Login successful"
    return "Login failed"

@app.route("/api")
def api_endpoint():
    """
    Hardcoded API key kullanımı
    Ground Truth: Line 33 - Hardcoded API key açığı
    """
    api_key = request.headers.get('X-API-Key', '')
    # VULNERABLE: Hardcoded API key
    if api_key == API_KEY:
        return "API access granted"
    return "API access denied"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # VULNERABLE: Debug mode production'da açık

