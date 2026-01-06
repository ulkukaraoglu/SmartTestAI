#!/usr/bin/env python3
"""
Gelişmiş Metrik Test Script'i

Bu script, Snyk Code ve DeepSource için gelişmiş metrikleri hesaplar
ve sonuçları results/ klasörüne kaydeder.

Test Senaryoları:
1. Snyk Code: vulnerable_demo projesi için ground truth ile precision/recall hesaplar
2. DeepSource: Repository-based tarama için temel metrikleri hesaplar

Kullanım:
    cd backend/tests
    python test_advanced_metrics.py
    
    veya backend/ klasöründen:
    python -m tests.test_advanced_metrics

Çıktı:
    - Console'da metrik sonuçları gösterilir
    - results/ klasörüne JSON formatında kaydedilir
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Backend klasörünü Python path'ine ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics.advanced_metrics import AdvancedMetricsCalculator, AdvancedMetricResult
from metrics.snyk_metrics import SnykMetrics
from metrics.deepsource_metrics import DeepSourceMetrics

# Sonuç dosyalarının kaydedileceği klasör (proje root'una göre)
RESULTS_DIR = "../../results"

def create_ground_truth_vulnerable_demo():
    """
    vulnerable_demo projesi için ground truth (gerçek hata listesi)
    Bu projede kasıtlı olarak eklenen güvenlik açıkları
    """
    return [
        {
            "file": "app.py",
            "line": 18,
            "type": "SQL_INJECTION",
            "severity": "high",
            "description": "SQL Injection vulnerability in login function"
        },
        {
            "file": "app.py",
            "line": 32,
            "type": "COMMAND_INJECTION",
            "severity": "high",
            "description": "Command Injection vulnerability in ping function"
        },
        {
            "file": "app.py",
            "line": 40,
            "type": "PATH_TRAVERSAL",
            "severity": "high",
            "description": "Path Traversal vulnerability in read_file function"
        },
        {
            "file": "app.py",
            "line": 44,
            "type": "HARDCODED_SECRET",
            "severity": "medium",
            "description": "Hardcoded secret key"
        },
        {
            "file": "app.py",
            "line": 49,
            "type": "INSECURE_DESERIALIZATION",
            "severity": "high",
            "description": "Insecure deserialization using pickle"
        },
        {
            "file": "app.py",
            "line": 60,
            "type": "XSS",
            "severity": "high",
            "description": "Cross-Site Scripting vulnerability"
        }
    ]

def extract_issues_from_snyk_result(raw_data: dict) -> list:
    """Snyk SARIF formatından issue'ları çıkarır"""
    issues = []
    if "runs" in raw_data and len(raw_data.get("runs", [])) > 0:
        results = raw_data["runs"][0].get("results", [])
        for result in results:
            locations = result.get("locations", [])
            if locations:
                location = locations[0].get("physicalLocation", {})
                artifact_location = location.get("artifactLocation", {})
                region = location.get("region", {})
                
                issues.append({
                    "file": artifact_location.get("uri", ""),
                    "line": region.get("startLine", -1),
                    "type": result.get("ruleId", ""),
                    "severity": result.get("level", "error"),
                    "description": result.get("message", {}).get("text", "")
                })
    return issues

def extract_issues_from_deepsource_result(raw_data: dict) -> list:
    """DeepSource GraphQL formatından issue'ları çıkarır"""
    issues = []
    if "data" in raw_data and "repository" in raw_data["data"]:
        repo_data = raw_data["data"]["repository"]
        if "issues" in repo_data and "edges" in repo_data["issues"]:
            for edge in repo_data["issues"]["edges"]:
                if "node" in edge and "issue" in edge["node"]:
                    issue = edge["node"]["issue"]
                    # DeepSource'te dosya ve satır bilgisi yok, sadece issue bilgisi var
                    issues.append({
                        "file": "unknown",  # DeepSource API'sinde dosya bilgisi yok
                        "line": -1,
                        "type": issue.get("shortcode", ""),
                        "severity": issue.get("severity", ""),
                        "description": issue.get("title", "")
                    })
    return issues

def test_snyk_advanced_metrics():
    """Snyk için gelişmiş metrikleri test et"""
    print("=" * 60)
    print("SNYK CODE - GELISMIS METRIK TESTI")
    print("=" * 60)
    
    # Son Snyk sonuç dosyasını bul
    snyk_files = list(Path("../../results").glob("snyk_code_*.json"))
    if not snyk_files:
        print("HATA: Snyk sonuc dosyasi bulunamadi!")
        return
    
    latest_snyk = max(snyk_files, key=lambda x: x.stat().st_mtime)
    print(f"\nDosya: {latest_snyk.name}")
    
    # Sonuç dosyasını oku
    with open(latest_snyk, "r", encoding="utf-8") as f:
        snyk_raw_data = json.load(f)
    
    # Issue'ları çıkar
    detected_issues = extract_issues_from_snyk_result(snyk_raw_data)
    print(f"Bulunan Issues: {len(detected_issues)}")
    
    # Ground truth (vulnerable_demo için)
    if "vulnerable_demo" in latest_snyk.name:
        ground_truth = create_ground_truth_vulnerable_demo()
        print(f"Ground Truth: {len(ground_truth)} bilinen hata")
    else:
        ground_truth = None
        print("UYARI: Ground Truth yok (flask_demo temiz proje)")
    
    # Temel metrikleri hesapla
    snyk_metric = SnykMetrics()
    basic_result = snyk_metric.calculate(snyk_raw_data)
    print(f"\nTEMEL METRIKLER:")
    print(f"  Critical: {basic_result.critical}")
    print(f"  High: {basic_result.high}")
    print(f"  Medium: {basic_result.medium}")
    print(f"  Low: {basic_result.low}")
    print(f"  Total: {basic_result.total_issues}")
    
    # Gelişmiş metrikleri hesapla
    calculator = AdvancedMetricsCalculator()
    advanced_result = calculator.calculate_all_advanced_metrics(
        raw_data=snyk_raw_data,
        detected_issues=detected_issues,
        ground_truth=ground_truth,
        scan_duration=basic_result.scan_duration
    )
    
    print(f"\nGELISMIS METRIKLER:")
    if ground_truth:
        print(f"  Precision: {advanced_result.precision:.2%}")
        print(f"  Recall: {advanced_result.recall:.2%}")
        print(f"  F1 Score: {advanced_result.f1_score:.2%}")
        print(f"  False Positive Rate: {advanced_result.false_positive_rate:.2%}")
        print(f"  True Positives: {advanced_result.true_positives}")
        print(f"  False Positives: {advanced_result.false_positives}")
        print(f"  False Negatives: {advanced_result.false_negatives}")
    else:
        print("  UYARI: Ground Truth olmadan precision/recall hesaplanamaz")
    
    print(f"  Code Coverage: {advanced_result.code_coverage:.2f}%")
    print(f"  Files Analyzed: {advanced_result.files_analyzed}")
    print(f"  Average Scan Time: {advanced_result.average_scan_time:.2f}s")
    print(f"  CPU Usage: {advanced_result.cpu_usage_percent:.2f}%")
    print(f"  Memory Usage: {advanced_result.memory_usage_mb:.2f} MB")
    
    # Sonuçları kaydet
    save_advanced_metrics_result("snyk", latest_snyk.stem, basic_result, advanced_result, ground_truth)
    
    print("\n" + "=" * 60)

def test_deepsource_advanced_metrics():
    """DeepSource için gelişmiş metrikleri test et"""
    print("=" * 60)
    print("DEEPSOURCE - GELISMIS METRIK TESTI")
    print("=" * 60)
    
    # Son DeepSource sonuç dosyasını bul (advanced_metrics olmayan)
    deepsource_files = [
        f for f in Path("../../results").glob("deepsource_*.json")
        if "advanced_metrics" not in f.name
    ]
    if not deepsource_files:
        print("HATA: DeepSource sonuc dosyasi bulunamadi!")
        return
    
    latest_deepsource = max(deepsource_files, key=lambda x: x.stat().st_mtime)
    print(f"\nDosya: {latest_deepsource.name}")
    
    # Sonuç dosyasını oku
    with open(latest_deepsource, "r", encoding="utf-8") as f:
        deepsource_raw_data = json.load(f)
    
    # Issue'ları çıkar
    detected_issues = extract_issues_from_deepsource_result(deepsource_raw_data)
    print(f"Bulunan Issues: {len(detected_issues)}")
    
    # Ground truth (DeepSource repository-based çalıştığı için genel ground truth)
    ground_truth = None  # DeepSource tüm repository'yi taradığı için spesifik ground truth yok
    print("UYARI: Ground Truth yok (repository-based tarama)")
    
    # Temel metrikleri hesapla
    deepsource_metric = DeepSourceMetrics()
    basic_result = deepsource_metric.calculate(deepsource_raw_data)
    print(f"\nTEMEL METRIKLER:")
    print(f"  Critical: {basic_result.critical}")
    print(f"  High: {basic_result.high}")
    print(f"  Medium: {basic_result.medium}")
    print(f"  Low: {basic_result.low}")
    print(f"  Total: {basic_result.total_issues}")
    
    # Gelişmiş metrikleri hesapla
    calculator = AdvancedMetricsCalculator()
    advanced_result = calculator.calculate_all_advanced_metrics(
        raw_data=deepsource_raw_data,
        detected_issues=detected_issues,
        ground_truth=ground_truth,
        scan_duration=basic_result.scan_duration
    )
    
    print(f"\nGELISMIS METRIKLER:")
    if ground_truth:
        print(f"  Precision: {advanced_result.precision:.2%}")
        print(f"  Recall: {advanced_result.recall:.2%}")
        print(f"  F1 Score: {advanced_result.f1_score:.2%}")
        print(f"  False Positive Rate: {advanced_result.false_positive_rate:.2%}")
    else:
        print("  UYARI: Ground Truth olmadan precision/recall hesaplanamaz")
    
    print(f"  Code Coverage: {advanced_result.code_coverage:.2f}%")
    print(f"  Files Analyzed: {advanced_result.files_analyzed}")
    print(f"  Average Scan Time: {advanced_result.average_scan_time:.2f}s")
    print(f"  CPU Usage: {advanced_result.cpu_usage_percent:.2f}%")
    print(f"  Memory Usage: {advanced_result.memory_usage_mb:.2f} MB")
    
    # Sonuçları kaydet
    save_advanced_metrics_result("deepsource", latest_deepsource.stem, basic_result, advanced_result, ground_truth)
    
    print("\n" + "=" * 60)

def save_advanced_metrics_result(
    tool_name: str,
    project_name: str,
    basic_result,
    advanced_result: AdvancedMetricResult,
    ground_truth: list = None
):
    """
    Gelişmiş metrik sonuçlarını results/ klasörüne kaydeder
    
    Args:
        tool_name: Araç adı ("snyk" veya "deepsource")
        project_name: Proje adı
        basic_result: Temel metrik sonucu (MetricResult)
        advanced_result: Gelişmiş metrik sonucu (AdvancedMetricResult)
        ground_truth: Ground truth listesi (opsiyonel)
    """
    results_path = Path(RESULTS_DIR)
    results_path.mkdir(parents=True, exist_ok=True)
    
    # Dosya adını oluştur
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{tool_name}_advanced_metrics_{project_name}_{timestamp}.json"
    file_path = results_path / filename
    
    # Sonuçları dict'e çevir
    result_dict = {
        "tool_name": tool_name,
        "project": project_name,
        "timestamp": timestamp,
        "basic_metrics": {
            "tool_name": basic_result.tool_name,
            "critical": basic_result.critical,
            "high": basic_result.high,
            "medium": basic_result.medium,
            "low": basic_result.low,
            "total_issues": basic_result.total_issues,
            "scan_duration": basic_result.scan_duration
        },
        "advanced_metrics": {
            "defect_detection_accuracy": {
                "precision": advanced_result.precision,
                "recall": advanced_result.recall,
                "f1_score": advanced_result.f1_score,
                "true_positives": advanced_result.true_positives,
                "false_positives": advanced_result.false_positives,
                "false_negatives": advanced_result.false_negatives,
                "true_negatives": advanced_result.true_negatives
            },
            "code_coverage": {
                "code_coverage_percent": advanced_result.code_coverage,
                "files_analyzed": advanced_result.files_analyzed,
                "lines_analyzed": advanced_result.lines_analyzed
            },
            "false_positive_rate": advanced_result.false_positive_rate,
            "operational_efficiency": {
                "average_scan_time": advanced_result.average_scan_time,
                "cpu_usage_percent": advanced_result.cpu_usage_percent,
                "memory_usage_mb": advanced_result.memory_usage_mb
            },
            "code_quality_score": advanced_result.code_quality_score
        },
        "ground_truth_count": len(ground_truth) if ground_truth else 0
    }
    
    # JSON'u kaydet
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\nSonuc kaydedildi: {file_path}")

if __name__ == "__main__":
    print("\nGELISMIS METRIK TEST SUITI\n")
    
    # Snyk testi
    test_snyk_advanced_metrics()
    
    print("\n")
    
    # DeepSource testi
    test_deepsource_advanced_metrics()
    
    print("\nTest tamamlandi!")

