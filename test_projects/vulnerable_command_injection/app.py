"""
Test Senaryosu 2: Command Injection Açığı
Bu proje kasıtlı olarak command injection açığı içerir.
"""
from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "Command Injection Test App"

@app.route("/ping")
def ping_host():
    """
    Command Injection açığı: host parametresi doğrudan shell komutuna ekleniyor
    Ground Truth: Line 18 - Command Injection açığı
    """
    host = request.args.get('host', 'localhost')
    # VULNERABLE: Command Injection açığı
    result = subprocess.run(f"ping -c 4 {host}", shell=True, capture_output=True, text=True)
    return result.stdout

@app.route("/execute")
def execute_command():
    """
    Command Injection açığı: command parametresi doğrudan shell komutuna ekleniyor
    Ground Truth: Line 28 - Command Injection açığı
    """
    command = request.args.get('cmd', '')
    # VULNERABLE: Command Injection açığı
    result = os.system(command)
    return f"Command executed with exit code: {result}"

@app.route("/file")
def read_file():
    """
    Path Traversal açığı: filename parametresi doğrudan dosya okuma işleminde kullanılıyor
    Ground Truth: Line 37 - Path Traversal açığı
    """
    filename = request.args.get('name', '')
    # VULNERABLE: Path Traversal açığı
    with open(filename, 'r') as f:
        content = f.read()
    return content

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

