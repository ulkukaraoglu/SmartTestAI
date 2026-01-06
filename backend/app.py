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

from flask import Flask, jsonify, send_file, request
import os
from pathlib import Path
from snyk_runner import run_and_return, REPORT_DIR
from metric_runner import run_code_scan_and_save
from deepsource_runner import run_deepsource_scan_and_save

# Flask uygulamasını başlat
app = Flask(__name__)

# Mevcut test projeleri listesi
# Bu projeler test_projects/ klasöründe bulunmalıdır
AVAILABLE_PROJECTS = [
    "flask_demo",
    "vulnerable_sql_injection",
    "vulnerable_command_injection",
    "vulnerable_xss",
    "vulnerable_hardcoded_creds"
]

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
    # Proje adını al (body'den veya query'den)
    project = None
    
    if request.is_json and request.json:
        project = request.json.get("project")
    
    if not project:
        project = request.args.get("project", "flask_demo")
    
    # Proje geçerli mi kontrol et
    if project not in AVAILABLE_PROJECTS:
        return jsonify({
            "error": f"Invalid project. Available projects: {AVAILABLE_PROJECTS}",
            "available_projects": AVAILABLE_PROJECTS
        }), 400
    
    # Tarama yap
    result = run_code_scan_and_save(project)
    
    if not result["success"]:
        return jsonify({
            "error": result.get("error", "Scan failed"),
            "project": project
        }), 500
    
    return jsonify({
        "message": "code scan completed",
        "project": result["project"],
        "file_path": result["file_path"],
        "advanced_metrics_file_path": result.get("advanced_metrics_file_path"),
        "metrics": result["metric_result"],
        "advanced_metrics": result.get("advanced_metrics", {})
    }), 200


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
    # Proje adını al (body'den veya query'den)
    project = None
    
    if request.is_json and request.json:
        project = request.json.get("project")
    
    if not project:
        project = request.args.get("project", "flask_demo")
    
    # Proje geçerli mi kontrol et
    if project not in AVAILABLE_PROJECTS:
        return jsonify({
            "error": f"Invalid project. Available projects: {AVAILABLE_PROJECTS}",
            "available_projects": AVAILABLE_PROJECTS
        }), 400
    
    # Tarama yap
    result = run_deepsource_scan_and_save(project)
    
    if not result["success"]:
        return jsonify({
            "error": result.get("error", "Scan failed"),
            "project": project
        }), 500
    
    return jsonify({
        "message": "deepsource scan completed",
        "project": result["project"],
        "file_path": result["file_path"],
        "advanced_metrics_file_path": result.get("advanced_metrics_file_path"),
        "metrics": result["metric_result"],
        "advanced_metrics": result.get("advanced_metrics", {})
    }), 200


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


if __name__ == "__main__":
    """
    Flask uygulamasını başlatır
    
    Port: 5001
    Debug mode: True (geliştirme için)
    """
    app.run(port=5001, debug=True)
