"""
SmartTestAI Feature Metrics Engine - Flask REST API

Bu modül, AI kod analiz araçlarını (Snyk Code, DeepSource) karşılaştırmak için
bir REST API sağlar. Her araç için tarama endpoint'leri ve metrik normalizasyonu içerir.

Proje Yapısı:
- backend/app.py: Ana Flask uygulaması (bu dosya)
- backend/metric_runner.py: Snyk Code tarama runner'ı
- backend/deepsource_runner.py: DeepSource tarama runner'ı
- backend/metrics/: Metrik hesaplama modülleri
- backend/tests/: Test script'leri
- results/: Tarama sonuçları (JSON formatında)

Ana Özellikler:
- Snyk Code taraması ve metrik normalizasyonu
- DeepSource taraması ve metrik normalizasyonu
- Standart metrik formatı (critical, high, medium, low)
- JSON formatında sonuç kaydetme
- RESTful API endpoint'leri

Kullanım:
    cd backend
    python app.py
    
API adresi: http://localhost:5001
"""

from flask import Flask, jsonify, send_file, request, send_from_directory
from flask_cors import CORS
import os
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from snyk_runner import run_and_return, REPORT_DIR
from metric_runner import run_code_scan_and_save
from deepsource_runner import run_deepsource_scan_and_save

# Web UI dosyalarının bulunduğu klasör
WEB_UI_DIR = Path(__file__).parent.parent / "src"

# Flask uygulamasını başlat
app = Flask(__name__, static_folder=str(WEB_UI_DIR), static_url_path='')
CORS(app)  # CORS desteği ekle (web UI için)

# Mevcut test projeleri listesi
# Bu projeler test_projects/ klasöründe bulunmalıdır
AVAILABLE_PROJECTS = [
    "flask_demo",
    "vulnerable_sql_injection",
    "vulnerable_command_injection",
    "vulnerable_xss",
    "vulnerable_hardcoded_creds"
]

# Yüklenen dosyalar için geçici proje klasörü
UPLOAD_DIR = "../test_projects/uploaded"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

@app.route("/scan", methods=["POST"])
def scan():
    """
    Container taraması endpoint'i (eski endpoint - geriye dönük uyumluluk için)
    
    Not: Bu endpoint container taraması için kullanılıyordu.
    Yeni kod analizi için /scan/code veya /scan/deepsource kullanın.
    
    Returns:
        JSON response with scan summary and report file path
    """
    summary, file_path = run_and_return()
    if not summary:
        return jsonify({"error": "scan failed"}), 500

    return jsonify({
        "message": "scan completed",
        "summary": summary,
        "report_file": file_path
    })


@app.route("/scan/code", methods=["POST"])
def scan_code():
    """
    Snyk Code taraması endpoint'i
    
    Bu endpoint, belirtilen test projesi için Snyk Code taraması yapar,
    sonuçları normalize eder ve results/ klasörüne kaydeder.
    
    Request body (JSON):
    {
        "project": "flask_demo" veya "nodejs-goof" (opsiyonel, default: flask_demo)
    }
    
    veya query parameter:
    ?project=flask_demo
    
    Returns:
        JSON response with:
        - message: İşlem durumu
        - project: Taranan proje adı
        - file_path: Kaydedilen sonuç dosyası yolu
        - metrics: Normalize edilmiş metrik sonuçları
    """
    try:
        # Proje adını al (body'den veya query'den)
        project = None
        
        if request.is_json and request.json:
            project = request.json.get("project")
        
        if not project:
            project = request.args.get("project", "flask_demo")
        
        # Proje geçerli mi kontrol et
        if project not in AVAILABLE_PROJECTS:
            return jsonify({
                "success": False,
                "error": f"Invalid project. Available projects: {AVAILABLE_PROJECTS}",
                "available_projects": AVAILABLE_PROJECTS,
                "project": project
            }), 400
        
        # Tarama yap
        result = run_code_scan_and_save(project)
        
        if not result.get("success", False):
            error_msg = result.get("error", "Scan failed")
            print(f"ERROR: Snyk scan failed for project {project}: {error_msg}")
            return jsonify({
                "success": False,
                "error": error_msg,
                "project": project,
                "message": "Snyk Code taraması başarısız"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "code scan completed",
            "project": result["project"],
            "file_path": result["file_path"],
            "advanced_metrics_file_path": result.get("advanced_metrics_file_path"),
            "metrics": result["metric_result"],
            "advanced_metrics": result.get("advanced_metrics", {})
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        print(f"EXCEPTION in scan_code: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {error_msg}",
            "project": project if 'project' in locals() else "unknown"
        }), 500


@app.route("/scan/code/all", methods=["POST"])
def scan_code_all():
    """
    Tüm test projeleri için Snyk Code taraması yapar
    
    AVAILABLE_PROJECTS listesindeki tüm projeleri sırayla tarar
    ve her biri için sonuçları döner.
    
    Returns:
        JSON response with:
        - message: Başarılı tarama sayısı
        - results: Her proje için tarama sonuçları listesi
    """
    results = []
    
    for project in AVAILABLE_PROJECTS:
        result = run_code_scan_and_save(project)
        results.append(result)
    
    success_count = sum(1 for r in results if r["success"])
    
    return jsonify({
        "message": f"Scanned {success_count}/{len(AVAILABLE_PROJECTS)} projects",
        "results": results
    }), 200 if success_count > 0 else 500


@app.route("/projects", methods=["GET"])
def list_projects():
    """
    Mevcut test projelerini listeler
    
    Returns:
        JSON response with:
        - available_projects: Proje adları listesi
        - projects: Her proje için detaylı bilgi (name, exists, path)
    """
    projects_info = []
    
    for project in AVAILABLE_PROJECTS:
        project_path = Path(f"../test_projects/{project}")
        exists = project_path.exists()
        
        projects_info.append({
            "name": project,
            "exists": exists,
            "path": str(project_path)
        })
    
    return jsonify({
        "available_projects": AVAILABLE_PROJECTS,
        "projects": projects_info
    })


@app.route("/scan/latest", methods=["GET"])
def latest():
    """
    En son container tarama raporunu döner (eski endpoint)
    
    Returns:
        En son rapor dosyası
    """
    files = os.listdir(REPORT_DIR)
    if not files:
        return jsonify({"error": "no reports found"}), 404

    latest = sorted(files)[-1]
    return send_file(os.path.join(REPORT_DIR, latest))


@app.route("/scan/file/<name>", methods=["GET"])
def file(name):
    """
    Belirtilen rapor dosyasını döner (eski endpoint)
    
    Args:
        name: Rapor dosyası adı
    
    Returns:
        Rapor dosyası
    """
    return send_file(os.path.join(REPORT_DIR, name))


# ============================================
# DEEPSOURCE ENDPOINT'LERİ
# ============================================

@app.route("/scan/deepsource", methods=["POST"])
def scan_deepsource():
    """
    DeepSource code taraması endpoint'i
    
    Bu endpoint, belirtilen test projesi için DeepSource taraması yapar,
    sonuçları normalize eder ve results/ klasörüne kaydeder.
    
    DeepSource GraphQL API kullanarak repository issues'larını alır
    ve standart metrik formatına dönüştürür.
    
    Request body (JSON):
    {
        "project": "flask_demo" veya "nodejs-goof" (opsiyonel, default: flask_demo)
    }
    
    veya query parameter:
    ?project=flask_demo
    
    Returns:
        JSON response with:
        - message: İşlem durumu
        - project: Taranan proje adı
        - file_path: Kaydedilen sonuç dosyası yolu
        - metrics: Normalize edilmiş metrik sonuçları
    """
    try:
        # Proje adını al (body'den veya query'den)
        project = None
        
        if request.is_json and request.json:
            project = request.json.get("project")
        
        if not project:
            project = request.args.get("project", "flask_demo")
        
        # Proje geçerli mi kontrol et
        if project not in AVAILABLE_PROJECTS:
            return jsonify({
                "success": False,
                "error": f"Invalid project. Available projects: {AVAILABLE_PROJECTS}",
                "available_projects": AVAILABLE_PROJECTS,
                "project": project
            }), 400
        
        # Tarama yap
        result = run_deepsource_scan_and_save(project)
        
        if not result.get("success", False):
            error_msg = result.get("error", "Scan failed")
            print(f"ERROR: DeepSource scan failed for project {project}: {error_msg}")
            return jsonify({
                "success": False,
                "error": error_msg,
                "project": project,
                "message": "DeepSource taraması başarısız"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "deepsource scan completed",
            "project": result["project"],
            "file_path": result["file_path"],
            "advanced_metrics_file_path": result.get("advanced_metrics_file_path"),
            "metrics": result["metric_result"],
            "advanced_metrics": result.get("advanced_metrics", {})
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        print(f"EXCEPTION in scan_deepsource: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {error_msg}",
            "project": project if 'project' in locals() else "unknown"
        }), 500


@app.route("/upload", methods=["POST"])
def upload_files():
    """
    Dosya yükleme endpoint'i
    
    Yüklenen dosyaları geçici bir proje klasörüne kaydeder ve
    bu klasörü AVAILABLE_PROJECTS listesine ekler.
    
    Request:
        multipart/form-data ile dosyalar gönderilir
    
    Returns:
        JSON response with:
        - success: bool
        - project_name: str (oluşturulan proje adı)
        - files: list (yüklenen dosya adları)
    """
    try:
        if 'files' not in request.files:
            return jsonify({
                "success": False,
                "error": "No files provided"
            }), 400
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({
                "success": False,
                "error": "No files selected"
            }), 400
        
        # Benzersiz proje adı oluştur
        project_name = f"uploaded_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        project_path = Path(UPLOAD_DIR) / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        uploaded_file_names = []
        
        # Dosyaları kaydet
        for file in files:
            if file.filename:
                # Güvenlik: Dosya adını temizle
                safe_filename = os.path.basename(file.filename)
                file_path = project_path / safe_filename
                file.save(str(file_path))
                uploaded_file_names.append(safe_filename)
        
        # Projeyi geçici olarak AVAILABLE_PROJECTS'e ekle
        if project_name not in AVAILABLE_PROJECTS:
            AVAILABLE_PROJECTS.append(project_name)
        
        return jsonify({
            "success": True,
            "project_name": project_name,
            "files": uploaded_file_names,
            "message": f"Files uploaded successfully to project: {project_name}"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/scan/deepsource/all", methods=["POST"])
def scan_deepsource_all():
    """
    Tüm test projeleri için DeepSource taraması yapar
    
    AVAILABLE_PROJECTS listesindeki tüm projeleri sırayla tarar
    ve her biri için sonuçları döner.
    
    Returns:
        JSON response with:
        - message: Başarılı tarama sayısı
        - results: Her proje için tarama sonuçları listesi
    """
    results = []
    
    for project in AVAILABLE_PROJECTS:
        result = run_deepsource_scan_and_save(project)
        results.append(result)
    
    success_count = sum(1 for r in results if r["success"])
    
    return jsonify({
        "message": f"DeepSource scanned {success_count}/{len(AVAILABLE_PROJECTS)} projects",
        "results": results
    }), 200 if success_count > 0 else 500


# Web UI Static File Serving (en sonda olmalı, API route'larından sonra)
@app.route("/")
def index():
    """Ana sayfa - Web UI'yi göster"""
    index_path = WEB_UI_DIR / "index.html"
    if index_path.exists():
        return send_from_directory(str(WEB_UI_DIR), "index.html")
    else:
        return jsonify({
            "message": "Web UI not found. Please check if src/index.html exists.",
            "api_endpoints": {
                "projects": "/projects",
                "scan_code": "/scan/code",
                "scan_deepsource": "/scan/deepsource",
                "upload": "/upload"
            }
        }), 404


@app.route("/<path:filename>")
def serve_static(filename):
    """Static dosyaları serve et (CSS, JS, vb.) - API route'ları ile çakışmayan dosyalar için"""
    # API route'ları ile çakışmayan dosyaları kontrol et
    static_extensions = ['.css', '.js', '.html', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.json']
    file_path = WEB_UI_DIR / filename
    
    if file_path.exists() and file_path.suffix in static_extensions:
        return send_from_directory(str(WEB_UI_DIR), filename)
    else:
        # Dosya bulunamadıysa 404 döndür
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    """
    Flask uygulamasını başlatır
    
    Port: 5001
    Debug mode: True (geliştirme için)
    Web UI: http://localhost:5001
    API: http://localhost:5001/api/*
    """
    print("=" * 60)
    print("SmartTestAI Backend Başlatılıyor...")
    print("=" * 60)
    print(f"Web UI: http://localhost:5001")
    print(f"API Base URL: http://localhost:5001")
    print(f"API Endpoints:")
    print(f"  - GET  /projects")
    print(f"  - POST /upload")
    print(f"  - POST /scan/code")
    print(f"  - POST /scan/deepsource")
    print("=" * 60)
    print()
    
    app.run(port=5001, debug=True)
