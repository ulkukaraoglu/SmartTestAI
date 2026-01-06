"""
Benchmark Runner - Karşılaştırmalı Test Senaryoları Çalıştırıcı

Bu script, tüm test senaryolarını hem Snyk Code hem DeepSource ile tarar,
ground truth verisi ile karşılaştırır ve detaylı analiz raporu oluşturur.
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# API base URL
API_BASE_URL = "http://localhost:5001"

# Test projeleri
TEST_PROJECTS = [
    "flask_demo",
    "vulnerable_sql_injection",
    "vulnerable_command_injection",
    "vulnerable_xss",
    "vulnerable_hardcoded_creds"
]

# Ground truth dosyası
GROUND_TRUTH_FILE = "../test_projects/ground_truth.json"


def load_ground_truth() -> Dict[str, List[Dict]]:
    """Ground truth verisini yükler"""
    try:
        with open(GROUND_TRUTH_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"UYARI: Ground truth dosyası bulunamadı: {GROUND_TRUTH_FILE}")
        return {}


def run_scan(tool: str, project: str) -> Dict[str, Any]:
    """
    Belirtilen araç ile proje taraması yapar
    
    Args:
        tool: "snyk" veya "deepsource"
        project: Proje adı
    
    Returns:
        Tarama sonuçları
    """
    endpoint = f"{API_BASE_URL}/scan/{tool}"
    if tool == "snyk":
        endpoint = f"{API_BASE_URL}/scan/code"
    
    try:
        start_time = time.time()
        response = requests.post(
            endpoint,
            json={"project": project},
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 dakika timeout
        )
        scan_duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            result['scan_duration'] = scan_duration
            result['success'] = True
            return result
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "scan_duration": scan_duration
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "scan_duration": 0.0
        }


def extract_issues_from_raw_file(file_path: str, tool: str) -> List[Dict]:
    """
    Raw sonuç dosyasından issue'ları çıkarır
    
    Args:
        file_path: Raw sonuç dosyası yolu
        tool: "snyk" veya "deepsource"
    
    Returns:
        Issue listesi
    """
    issues = []
    
    try:
        # Dosya yolunu düzelt (relative path)
        if file_path.startswith(".."):
            file_path = Path(file_path).resolve()
        else:
            file_path = Path(file_path)
        
        if not file_path.exists():
            return issues
        
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Snyk Code için
        if tool == "snyk":
            if "runs" in raw_data and len(raw_data.get("runs", [])) > 0:
                results = raw_data["runs"][0].get("results", [])
                for result in results:
                    locations = result.get("locations", [])
                    if locations:
                        location = locations[0].get("physicalLocation", {})
                        artifact_location = location.get("artifactLocation", {})
                        region = location.get("region", {})
                        
                        # Dosya adını normalize et
                        file_uri = artifact_location.get("uri", "")
                        file_name = file_uri.split("/")[-1] if "/" in file_uri else file_uri
                        
                        issues.append({
                            "file": file_name,
                            "line": region.get("startLine", -1),
                            "type": result.get("ruleId", ""),
                            "severity": result.get("level", "error"),
                            "description": result.get("message", {}).get("text", "")
                        })
        
        # DeepSource için
        elif tool == "deepsource":
            # GraphQL formatı
            if "data" in raw_data and "repository" in raw_data["data"]:
                repo_data = raw_data["data"]["repository"]
                if "issues" in repo_data and "edges" in repo_data["issues"]:
                    for edge in repo_data["issues"]["edges"]:
                        if "node" in edge and "issue" in edge["node"]:
                            issue = edge["node"]["issue"]
                            issues.append({
                                "file": "app.py",  # DeepSource API'sinde dosya bilgisi yok, varsayılan
                                "line": -1,
                                "type": issue.get("shortcode", ""),
                                "severity": issue.get("severity", ""),
                                "description": issue.get("title", "")
                            })
            # Mock format
            elif "issues" in raw_data:
                for issue in raw_data["issues"]:
                    issues.append({
                        "file": issue.get("file", "app.py"),
                        "line": issue.get("line", -1),
                        "type": issue.get("issue_code", ""),
                        "severity": issue.get("severity", "").upper(),
                        "description": issue.get("message", "")
                    })
    
    except Exception as e:
        print(f"  [UYARI] Issue çıkarma hatası: {e}")
    
    return issues


def extract_issues_from_result(result: Dict, tool: str) -> List[Dict]:
    """
    Tarama sonucundan issue'ları çıkarır
    Raw dosyayı okuyarak detaylı issue bilgilerini alır
    """
    issues = []
    
    if not result.get("success"):
        return issues
    
    # Raw dosya yolunu al
    file_path = result.get("file_path", "")
    if file_path:
        issues = extract_issues_from_raw_file(file_path, tool)
    
    return issues


def match_issue(detected: Dict, truth: Dict) -> bool:
    """
    Bir detected issue ile ground truth issue'yu eşleştirir
    
    Eşleştirme kriterleri:
    1. Dosya adı eşleşmeli
    2. Satır numarası eşleşmeli (veya ±2 satır tolerans)
    3. Issue tipi benzer olmalı (opsiyonel)
    """
    detected_file = detected.get("file", "").lower()
    detected_line = detected.get("line", -1)
    detected_type = detected.get("type", "").upper()
    
    truth_file = truth.get("file", "").lower()
    truth_line = truth.get("line", -1)
    truth_type = truth.get("type", "").upper()
    
    # Dosya adı eşleşmeli
    if detected_file and truth_file:
        # Sadece dosya adını karşılaştır (path'ten bağımsız)
        detected_name = detected_file.split("/")[-1].split("\\")[-1]
        truth_name = truth_file.split("/")[-1].split("\\")[-1]
        if detected_name != truth_name:
            return False
    
    # Satır numarası eşleşmeli (±2 satır tolerans)
    if detected_line > 0 and truth_line > 0:
        if abs(detected_line - truth_line) <= 2:
            return True
    
    # Eğer satır numarası yoksa, issue tipine bak
    if detected_line <= 0 or truth_line <= 0:
        # Issue tipi benzerliği kontrol et
        if truth_type in detected_type or detected_type in truth_type:
            return True
    
    return False


def calculate_metrics(detected_issues: List[Dict], ground_truth: List[Dict]) -> Dict[str, float]:
    """
    Precision, Recall, F1 Score hesaplar
    
    Args:
        detected_issues: Bulunan issue'lar
        ground_truth: Gerçek issue'lar
    
    Returns:
        Metrikler (precision, recall, f1_score, true_positives, false_positives, false_negatives)
    """
    if not ground_truth:
        # Ground truth yoksa, sadece false positive oranını hesaplayabiliriz
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "true_positives": 0,
            "false_positives": len(detected_issues),
            "false_negatives": 0
        }
    
    # Eşleştirme yap
    matched_truth_indices = set()
    matched_detected_indices = set()
    
    for i, detected in enumerate(detected_issues):
        for j, truth in enumerate(ground_truth):
            if j not in matched_truth_indices and match_issue(detected, truth):
                matched_truth_indices.add(j)
                matched_detected_indices.add(i)
                break
    
    true_positives = len(matched_truth_indices)
    false_positives = len(detected_issues) - len(matched_detected_indices)
    false_negatives = len(ground_truth) - len(matched_truth_indices)
    
    # Precision: TP / (TP + FP)
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    
    # Recall: TP / (TP + FN)
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    
    # F1 Score
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }


def run_benchmark():
    """Tüm test senaryolarını çalıştırır ve karşılaştırmalı analiz yapar"""
    print("=" * 80)
    print("BENCHMARK TEST SUITE - KARŞILAŞTIRMALI ANALİZ")
    print("=" * 80)
    print()
    
    # Ground truth yükle
    ground_truth_data = load_ground_truth()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "projects": {}
    }
    
    # Her proje için tarama yap
    for project in TEST_PROJECTS:
        print(f"\n{'='*80}")
        print(f"PROJE: {project}")
        print(f"{'='*80}")
        
        project_results = {
            "snyk": {},
            "deepsource": {}
        }
        
        # Ground truth
        ground_truth = ground_truth_data.get(project, [])
        print(f"Ground Truth Issues: {len(ground_truth)}")
        
        # Snyk Code taraması
        print(f"\n[1/2] Snyk Code taraması başlatılıyor...")
        snyk_result = run_scan("snyk", project)
        if snyk_result.get("success"):
            metrics = snyk_result.get("metrics", {})
            advanced = snyk_result.get("advanced_metrics", {})
            print(f"  [OK] Tarama tamamlandi ({snyk_result.get('scan_duration', 0):.2f}s)")
            print(f"  - Total Issues: {metrics.get('total_issues', 0)}")
            print(f"  - Critical: {metrics.get('critical', 0)}")
            print(f"  - High: {metrics.get('high', 0)}")
            print(f"  - Medium: {metrics.get('medium', 0)}")
            print(f"  - Low: {metrics.get('low', 0)}")
            
            project_results["snyk"] = {
                "success": True,
                "metrics": metrics,
                "advanced_metrics": advanced,
                "scan_duration": snyk_result.get("scan_duration", 0)
            }
        else:
            print(f"  [FAIL] Tarama basarisiz: {snyk_result.get('error', 'Unknown error')}")
            project_results["snyk"] = {
                "success": False,
                "error": snyk_result.get("error", "Unknown error")
            }
        
        # DeepSource taraması
        print(f"\n[2/2] DeepSource taraması başlatılıyor...")
        deepsource_result = run_scan("deepsource", project)
        if deepsource_result.get("success"):
            metrics = deepsource_result.get("metrics", {})
            advanced = deepsource_result.get("advanced_metrics", {})
            print(f"  [OK] Tarama tamamlandi ({deepsource_result.get('scan_duration', 0):.2f}s)")
            print(f"  - Total Issues: {metrics.get('total_issues', 0)}")
            print(f"  - Critical: {metrics.get('critical', 0)}")
            print(f"  - High: {metrics.get('high', 0)}")
            print(f"  - Medium: {metrics.get('medium', 0)}")
            print(f"  - Low: {metrics.get('low', 0)}")
            
            project_results["deepsource"] = {
                "success": True,
                "metrics": metrics,
                "advanced_metrics": advanced,
                "scan_duration": deepsource_result.get("scan_duration", 0)
            }
        else:
            print(f"  [FAIL] Tarama basarisiz: {deepsource_result.get('error', 'Unknown error')}")
            project_results["deepsource"] = {
                "success": False,
                "error": deepsource_result.get("error", "Unknown error")
            }
        
        # Issue'ları çıkar ve ground truth ile karşılaştır
        snyk_issues = []
        deepsource_issues = []
        
        if project_results["snyk"].get("success"):
            snyk_issues = extract_issues_from_result(snyk_result, "snyk")
            project_results["snyk"]["detected_issues"] = snyk_issues
            project_results["snyk"]["detected_issues_count"] = len(snyk_issues)
        
        if project_results["deepsource"].get("success"):
            deepsource_issues = extract_issues_from_result(deepsource_result, "deepsource")
            project_results["deepsource"]["detected_issues"] = deepsource_issues
            project_results["deepsource"]["detected_issues_count"] = len(deepsource_issues)
        
        # Ground truth ile karşılaştırma ve metrik hesaplama
        if ground_truth:
            print(f"\n[KARŞILAŞTIRMA VE METRIKLER]")
            gt_total = len(ground_truth)
            print(f"  Ground Truth: {gt_total} issue")
            
            # Snyk Code metrikleri
            if snyk_issues:
                snyk_metrics = calculate_metrics(snyk_issues, ground_truth)
                project_results["snyk"]["comparison_metrics"] = snyk_metrics
                print(f"\n  Snyk Code:")
                print(f"    - Bulunan Issues: {len(snyk_issues)}")
                print(f"    - True Positives: {snyk_metrics['true_positives']}")
                print(f"    - False Positives: {snyk_metrics['false_positives']}")
                print(f"    - False Negatives: {snyk_metrics['false_negatives']}")
                print(f"    - Precision: {snyk_metrics['precision']:.2%}")
                print(f"    - Recall: {snyk_metrics['recall']:.2%}")
                print(f"    - F1 Score: {snyk_metrics['f1_score']:.2%}")
            
            # DeepSource metrikleri
            if deepsource_issues:
                deepsource_metrics = calculate_metrics(deepsource_issues, ground_truth)
                project_results["deepsource"]["comparison_metrics"] = deepsource_metrics
                print(f"\n  DeepSource:")
                print(f"    - Bulunan Issues: {len(deepsource_issues)}")
                print(f"    - True Positives: {deepsource_metrics['true_positives']}")
                print(f"    - False Positives: {deepsource_metrics['false_positives']}")
                print(f"    - False Negatives: {deepsource_metrics['false_negatives']}")
                print(f"    - Precision: {deepsource_metrics['precision']:.2%}")
                print(f"    - Recall: {deepsource_metrics['recall']:.2%}")
                print(f"    - F1 Score: {deepsource_metrics['f1_score']:.2%}")
        else:
            print(f"\n[UYARI] Ground truth yok, detaylı karşılaştırma yapılamıyor")
        
        results["projects"][project] = {
            "ground_truth_count": len(ground_truth),
            **project_results
        }
    
    # Sonuçları kaydet
    results_dir = Path("../results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_file = results_dir / f"benchmark_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("BENCHMARK TAMAMLANDI")
    print(f"{'='*80}")
    print(f"Rapor kaydedildi: {report_file}")
    
    # Özet rapor
    print_summary(results)
    
    return results


def print_summary(results: Dict):
    """Özet rapor yazdırır"""
    print(f"\n{'='*80}")
    print("ÖZET RAPOR")
    print(f"{'='*80}")
    
    total_projects = len(results["projects"])
    snyk_success = sum(1 for p in results["projects"].values() if p.get("snyk", {}).get("success"))
    deepsource_success = sum(1 for p in results["projects"].values() if p.get("deepsource", {}).get("success"))
    
    print(f"\n[GENEL ISTATISTIKLER]")
    print(f"Toplam Proje: {total_projects}")
    print(f"Snyk Code Basarili: {snyk_success}/{total_projects}")
    print(f"DeepSource Basarili: {deepsource_success}/{total_projects}")
    
    # Ortalama tarama süreleri
    snyk_times = [p["snyk"]["scan_duration"] for p in results["projects"].values() 
                  if p.get("snyk", {}).get("success")]
    deepsource_times = [p["deepsource"]["scan_duration"] for p in results["projects"].values() 
                        if p.get("deepsource", {}).get("success")]
    
    if snyk_times:
        print(f"\nSnyk Code Ortalama Tarama Suresi: {sum(snyk_times)/len(snyk_times):.2f}s")
    if deepsource_times:
        print(f"DeepSource Ortalama Tarama Suresi: {sum(deepsource_times)/len(deepsource_times):.2f}s")
    
    # Genel metrikler (ground truth olan projeler için)
    snyk_precisions = []
    snyk_recalls = []
    snyk_f1_scores = []
    
    deepsource_precisions = []
    deepsource_recalls = []
    deepsource_f1_scores = []
    
    for project_name, project_data in results["projects"].items():
        if project_data.get("ground_truth_count", 0) > 0:
            # Snyk metrikleri
            snyk_metrics = project_data.get("snyk", {}).get("comparison_metrics")
            if snyk_metrics:
                snyk_precisions.append(snyk_metrics.get("precision", 0))
                snyk_recalls.append(snyk_metrics.get("recall", 0))
                snyk_f1_scores.append(snyk_metrics.get("f1_score", 0))
            
            # DeepSource metrikleri
            deepsource_metrics = project_data.get("deepsource", {}).get("comparison_metrics")
            if deepsource_metrics:
                deepsource_precisions.append(deepsource_metrics.get("precision", 0))
                deepsource_recalls.append(deepsource_metrics.get("recall", 0))
                deepsource_f1_scores.append(deepsource_metrics.get("f1_score", 0))
    
    if snyk_precisions:
        print(f"\n[SNYK CODE GENEL METRIKLER]")
        print(f"  Ortalama Precision: {sum(snyk_precisions)/len(snyk_precisions):.2%}")
        print(f"  Ortalama Recall: {sum(snyk_recalls)/len(snyk_recalls):.2%}")
        print(f"  Ortalama F1 Score: {sum(snyk_f1_scores)/len(snyk_f1_scores):.2%}")
    
    if deepsource_precisions:
        print(f"\n[DEEPSOURCE GENEL METRIKLER]")
        print(f"  Ortalama Precision: {sum(deepsource_precisions)/len(deepsource_precisions):.2%}")
        print(f"  Ortalama Recall: {sum(deepsource_recalls)/len(deepsource_recalls):.2%}")
        print(f"  Ortalama F1 Score: {sum(deepsource_f1_scores)/len(deepsource_f1_scores):.2%}")


if __name__ == "__main__":
    run_benchmark()

