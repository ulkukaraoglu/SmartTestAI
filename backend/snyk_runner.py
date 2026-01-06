"""
Snyk Container Runner Modülü

Bu modül, Snyk Container taraması için kullanılır (eski endpoint - geriye dönük uyumluluk).

Not: Bu modül container taraması için kullanılıyordu. Yeni kod analizi için
metric_runner.py (Snyk Code) veya deepsource_runner.py (DeepSource) kullanın.
"""

import os
from pathlib import Path
from datetime import datetime

# Container tarama raporlarının kaydedileceği klasör
REPORT_DIR = "../reports"

def run_and_return():
    """
    Container taraması yapar ve sonuç döner (eski endpoint için)
    
    Not: Bu fonksiyon container taraması için kullanılıyordu ancak artık
    kod analizine odaklanıldığı için basit bir stub implementasyonudur.
    
    Returns:
        tuple: (summary dict, report_file_path str)
    """
    # Reports klasörünü oluştur
    reports_path = Path(REPORT_DIR)
    reports_path.mkdir(parents=True, exist_ok=True)
    
    # Basit bir summary döndür (container taraması artık aktif değil)
    summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "note": "Container scanning is deprecated. Use /scan/code or /scan/deepsource for code analysis."
    }
    
    # Basit bir report dosyası yolu oluştur
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_file = f"snyk-container-report-{timestamp}.json"
    report_path = reports_path / report_file
    
    # Boş bir report dosyası oluştur
    import json
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    return summary, str(report_path)

