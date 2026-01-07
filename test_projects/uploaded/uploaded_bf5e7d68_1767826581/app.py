"""
Test Senaryosu 3: XSS (Cross-Site Scripting) Açığı
Bu proje kasıtlı olarak XSS açığı içerir.
"""
from flask import Flask, request
from flask import render_template_string

app = Flask(__name__)

@app.route("/")
def index():
    return "XSS Test App"

@app.route("/comment")
def add_comment():
    """
    XSS açığı: user input doğrudan HTML'e ekleniyor
    Ground Truth: Line 15 - XSS açığı
    """
    comment = request.args.get('text', '')
    # VULNERABLE: XSS açığı - input sanitize edilmiyor
    template = f"<h1>Your comment: {comment}</h1>"
    return render_template_string(template)

@app.route("/search")
def search():
    """
    XSS açığı: search parametresi doğrudan HTML'e ekleniyor
    Ground Truth: Line 25 - XSS açığı
    """
    query = request.args.get('q', '')
    # VULNERABLE: XSS açığı
    return f"<p>Search results for: {query}</p>"

@app.route("/profile")
def profile():
    """
    XSS açığı: username parametresi doğrudan HTML'e ekleniyor
    Ground Truth: Line 33 - XSS açığı
    """
    username = request.args.get('user', '')
    # VULNERABLE: XSS açığı
    return f"<h2>Welcome, {username}!</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

