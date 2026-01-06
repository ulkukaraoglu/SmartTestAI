"""
Kapsamlı Test Raporu Oluşturucu

Tüm test senaryolarını çalıştırır, sonuçları analiz eder ve detaylı rapor oluşturur.
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

API_BASE_URL = "http://localhost:5001"
TEST_PROJECTS = [
    "flask_demo",
    "vulnerable_sql_injection",
    "vulnerable_command_injection",
    "vulnerable_xss",
    "vulnerable_hardcoded_creds"
]
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
    """Belirtilen araç ile proje taraması yapar"""
    endpoint = f"{API_BASE_URL}/scan/code" if tool == "snyk" else f"{API_BASE_URL}/scan/deepsource"
    
    try:
        start_time = time.time()
        response = requests.post(
            endpoint,
            json={"project": project},
            headers={"Content-Type": "application/json"},
            timeout=300
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
    """Raw sonuç dosyasından issue'ları çıkarır"""
    issues = []
    
    try:
        if file_path.startswith(".."):
            file_path = Path(file_path).resolve()
        else:
            file_path = Path(file_path)
        
        if not file_path.exists():
            return issues
        
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        if tool == "snyk":
            if "runs" in raw_data and len(raw_data.get("runs", [])) > 0:
                results = raw_data["runs"][0].get("results", [])
                for result in results:
                    locations = result.get("locations", [])
                    if locations:
                        location = locations[0].get("physicalLocation", {})
                        artifact_location = location.get("artifactLocation", {})
                        region = location.get("region", {})
                        
                        file_uri = artifact_location.get("uri", "")
                        file_name = file_uri.split("/")[-1] if "/" in file_uri else file_uri
                        
                        issues.append({
                            "file": file_name,
                            "line": region.get("startLine", -1),
                            "type": result.get("ruleId", ""),
                            "severity": result.get("level", "error"),
                            "description": result.get("message", {}).get("text", "")
                        })
        
        elif tool == "deepsource":
            if "data" in raw_data and "repository" in raw_data["data"]:
                repo_data = raw_data["data"]["repository"]
                if "issues" in repo_data and "edges" in repo_data["issues"]:
                    for edge in repo_data["issues"]["edges"]:
                        if "node" in edge and "issue" in edge["node"]:
                            issue = edge["node"]["issue"]
                            issues.append({
                                "file": "app.py",
                                "line": -1,
                                "type": issue.get("shortcode", ""),
                                "severity": issue.get("severity", ""),
                                "description": issue.get("title", "")
                            })
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


def match_issue(detected: Dict, truth: Dict) -> bool:
    """Issue eşleştirme"""
    detected_file = detected.get("file", "").lower()
    detected_line = detected.get("line", -1)
    
    truth_file = truth.get("file", "").lower()
    truth_line = truth.get("line", -1)
    
    if detected_file and truth_file:
        detected_name = detected_file.split("/")[-1].split("\\")[-1]
        truth_name = truth_file.split("/")[-1].split("\\")[-1]
        if detected_name != truth_name:
            return False
    
    if detected_line > 0 and truth_line > 0:
        if abs(detected_line - truth_line) <= 2:
            return True
    
    return False


def calculate_metrics(detected_issues: List[Dict], ground_truth: List[Dict]) -> Dict[str, float]:
    """Precision, Recall, F1 Score hesaplar"""
    if not ground_truth:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "true_positives": 0,
            "false_positives": len(detected_issues),
            "false_negatives": 0
        }
    
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
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }


def run_comprehensive_tests():
    """Tüm test senaryolarını çalıştırır ve kapsamlı rapor oluşturur"""
    print("=" * 80)
    print("KAPSAMLI TEST RAPORU - TÜM SENARYOLAR")
    print("=" * 80)
    print(f"Başlangıç Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    ground_truth_data = load_ground_truth()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_summary": {
            "total_projects": len(TEST_PROJECTS),
            "tools_tested": ["Snyk Code", "DeepSource"]
        },
        "projects": {}
    }
    
    # Her proje için test
    for project_idx, project in enumerate(TEST_PROJECTS, 1):
        print(f"\n{'='*80}")
        print(f"[{project_idx}/{len(TEST_PROJECTS)}] PROJE: {project}")
        print(f"{'='*80}")
        
        project_results = {
            "ground_truth_count": len(ground_truth_data.get(project, [])),
            "snyk": {},
            "deepsource": {}
        }
        
        ground_truth = ground_truth_data.get(project, [])
        print(f"Ground Truth Issues: {len(ground_truth)}")
        
        # Snyk Code taraması
        print(f"\n[1/2] Snyk Code taraması...")
        snyk_result = run_scan("snyk", project)
        
        if snyk_result.get("success"):
            metrics = snyk_result.get("metrics", {})
            advanced = snyk_result.get("advanced_metrics", {})
            scan_duration = snyk_result.get("scan_duration", 0)
            
            # Issue'ları çıkar
            file_path = snyk_result.get("file_path", "")
            detected_issues = extract_issues_from_raw_file(file_path, "snyk") if file_path else []
            
            # Metrikleri hesapla
            comparison_metrics = calculate_metrics(detected_issues, ground_truth)
            
            project_results["snyk"] = {
                "success": True,
                "scan_duration": scan_duration,
                "metrics": metrics,
                "advanced_metrics": advanced,
                "detected_issues_count": len(detected_issues),
                "comparison_metrics": comparison_metrics
            }
            
            print(f"  [OK] Süre: {scan_duration:.2f}s")
            print(f"  - Issues: {metrics.get('total_issues', 0)}")
            print(f"  - Precision: {comparison_metrics['precision']:.2%}")
            print(f"  - Recall: {comparison_metrics['recall']:.2%}")
            print(f"  - F1 Score: {comparison_metrics['f1_score']:.2%}")
        else:
            project_results["snyk"] = {
                "success": False,
                "error": snyk_result.get("error", "Unknown error")
            }
            print(f"  [FAIL] {snyk_result.get('error', 'Unknown error')}")
        
        # DeepSource taraması
        print(f"\n[2/2] DeepSource taraması...")
        deepsource_result = run_scan("deepsource", project)
        
        if deepsource_result.get("success"):
            metrics = deepsource_result.get("metrics", {})
            advanced = deepsource_result.get("advanced_metrics", {})
            scan_duration = deepsource_result.get("scan_duration", 0)
            
            # Issue'ları çıkar
            file_path = deepsource_result.get("file_path", "")
            detected_issues = extract_issues_from_raw_file(file_path, "deepsource") if file_path else []
            
            # Metrikleri hesapla
            comparison_metrics = calculate_metrics(detected_issues, ground_truth)
            
            project_results["deepsource"] = {
                "success": True,
                "scan_duration": scan_duration,
                "metrics": metrics,
                "advanced_metrics": advanced,
                "detected_issues_count": len(detected_issues),
                "comparison_metrics": comparison_metrics
            }
            
            print(f"  [OK] Süre: {scan_duration:.2f}s")
            print(f"  - Issues: {metrics.get('total_issues', 0)}")
            print(f"  - Precision: {comparison_metrics['precision']:.2%}")
            print(f"  - Recall: {comparison_metrics['recall']:.2%}")
            print(f"  - F1 Score: {comparison_metrics['f1_score']:.2%}")
        else:
            project_results["deepsource"] = {
                "success": False,
                "error": deepsource_result.get("error", "Unknown error")
            }
            print(f"  [FAIL] {deepsource_result.get('error', 'Unknown error')}")
        
        results["projects"][project] = project_results
    
    # Sonuçları kaydet
    results_dir = Path("../results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_file = results_dir / f"comprehensive_test_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("TEST RAPORU TAMAMLANDI")
    print(f"{'='*80}")
    print(f"Rapor kaydedildi: {report_file}")
    
    # Özet rapor oluştur
    generate_summary_report(results, report_file)
    
    return results


def generate_summary_report(results: Dict, json_file: Path):
    """Özet rapor oluşturur"""
    report_file = json_file.parent / f"summary_report_{json_file.stem.split('_')[-1]}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("KAPSAMLI TEST RAPORU - ÖZET\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Rapor Tarihi: {results['timestamp']}\n")
        f.write(f"Test Edilen Projeler: {results['test_summary']['total_projects']}\n")
        f.write(f"Test Edilen Araçlar: {', '.join(results['test_summary']['tools_tested'])}\n\n")
        
        # Genel istatistikler
        f.write("=" * 80 + "\n")
        f.write("GENEL İSTATİSTİKLER\n")
        f.write("=" * 80 + "\n\n")
        
        snyk_success = sum(1 for p in results["projects"].values() if p.get("snyk", {}).get("success"))
        deepsource_success = sum(1 for p in results["projects"].values() if p.get("deepsource", {}).get("success"))
        
        f.write(f"Snyk Code Başarı Oranı: {snyk_success}/{results['test_summary']['total_projects']} ({snyk_success/results['test_summary']['total_projects']*100:.1f}%)\n")
        f.write(f"DeepSource Başarı Oranı: {deepsource_success}/{results['test_summary']['total_projects']} ({deepsource_success/results['test_summary']['total_projects']*100:.1f}%)\n\n")
        
        # Performans metrikleri
        f.write("=" * 80 + "\n")
        f.write("PERFORMANS METRİKLERİ\n")
        f.write("=" * 80 + "\n\n")
        
        snyk_times = [p["snyk"]["scan_duration"] for p in results["projects"].values() 
                      if p.get("snyk", {}).get("success")]
        deepsource_times = [p["deepsource"]["scan_duration"] for p in results["projects"].values() 
                            if p.get("deepsource", {}).get("success")]
        
        if snyk_times:
            f.write(f"Snyk Code:\n")
            f.write(f"  - Ortalama Süre: {sum(snyk_times)/len(snyk_times):.2f}s\n")
            f.write(f"  - En Hızlı: {min(snyk_times):.2f}s\n")
            f.write(f"  - En Yavaş: {max(snyk_times):.2f}s\n\n")
        
        if deepsource_times:
            f.write(f"DeepSource:\n")
            f.write(f"  - Ortalama Süre: {sum(deepsource_times)/len(deepsource_times):.2f}s\n")
            f.write(f"  - En Hızlı: {min(deepsource_times):.2f}s\n")
            f.write(f"  - En Yavaş: {max(deepsource_times):.2f}s\n\n")
        
        if snyk_times and deepsource_times:
            speed_ratio = sum(snyk_times)/len(snyk_times) / sum(deepsource_times)/len(deepsource_times)
            f.write(f"DeepSource, Snyk Code'dan {speed_ratio:.1f}x daha hızlı\n\n")
        
        # Doğruluk metrikleri
        f.write("=" * 80 + "\n")
        f.write("DOĞRULUK METRİKLERİ (Ground Truth Olan Projeler)\n")
        f.write("=" * 80 + "\n\n")
        
        projects_with_gt = {k: v for k, v in results["projects"].items() if v.get("ground_truth_count", 0) > 0}
        
        if projects_with_gt:
            snyk_precisions = []
            snyk_recalls = []
            snyk_f1_scores = []
            snyk_tps = []
            snyk_fps = []
            snyk_fns = []
            
            deepsource_precisions = []
            deepsource_recalls = []
            deepsource_f1_scores = []
            deepsource_tps = []
            deepsource_fps = []
            deepsource_fns = []
            
            for project_name, project_data in projects_with_gt.items():
                f.write(f"Proje: {project_name}\n")
                f.write(f"  Ground Truth: {project_data['ground_truth_count']} issue\n")
                
                snyk_metrics = project_data.get("snyk", {}).get("comparison_metrics")
                if snyk_metrics:
                    snyk_precisions.append(snyk_metrics["precision"])
                    snyk_recalls.append(snyk_metrics["recall"])
                    snyk_f1_scores.append(snyk_metrics["f1_score"])
                    snyk_tps.append(snyk_metrics["true_positives"])
                    snyk_fps.append(snyk_metrics["false_positives"])
                    snyk_fns.append(snyk_metrics["false_negatives"])
                    
                    f.write(f"  Snyk Code:\n")
                    f.write(f"    - Precision: {snyk_metrics['precision']:.2%}\n")
                    f.write(f"    - Recall: {snyk_metrics['recall']:.2%}\n")
                    f.write(f"    - F1 Score: {snyk_metrics['f1_score']:.2%}\n")
                    f.write(f"    - TP: {snyk_metrics['true_positives']}, FP: {snyk_metrics['false_positives']}, FN: {snyk_metrics['false_negatives']}\n")
                
                deepsource_metrics = project_data.get("deepsource", {}).get("comparison_metrics")
                if deepsource_metrics:
                    deepsource_precisions.append(deepsource_metrics["precision"])
                    deepsource_recalls.append(deepsource_metrics["recall"])
                    deepsource_f1_scores.append(deepsource_metrics["f1_score"])
                    deepsource_tps.append(deepsource_metrics["true_positives"])
                    deepsource_fps.append(deepsource_metrics["false_positives"])
                    deepsource_fns.append(deepsource_metrics["false_negatives"])
                    
                    f.write(f"  DeepSource:\n")
                    f.write(f"    - Precision: {deepsource_metrics['precision']:.2%}\n")
                    f.write(f"    - Recall: {deepsource_metrics['recall']:.2%}\n")
                    f.write(f"    - F1 Score: {deepsource_metrics['f1_score']:.2%}\n")
                    f.write(f"    - TP: {deepsource_metrics['true_positives']}, FP: {deepsource_metrics['false_positives']}, FN: {deepsource_metrics['false_negatives']}\n")
                
                f.write("\n")
            
            # Genel özet
            f.write("=" * 80 + "\n")
            f.write("GENEL ÖZET - DOĞRULUK METRİKLERİ\n")
            f.write("=" * 80 + "\n\n")
            
            if snyk_precisions:
                f.write(f"Snyk Code:\n")
                f.write(f"  - Ortalama Precision: {sum(snyk_precisions)/len(snyk_precisions):.2%}\n")
                f.write(f"  - Ortalama Recall: {sum(snyk_recalls)/len(snyk_recalls):.2%}\n")
                f.write(f"  - Ortalama F1 Score: {sum(snyk_f1_scores)/len(snyk_f1_scores):.2%}\n")
                f.write(f"  - Toplam TP: {sum(snyk_tps)}, FP: {sum(snyk_fps)}, FN: {sum(snyk_fns)}\n\n")
            
            if deepsource_precisions:
                f.write(f"DeepSource:\n")
                f.write(f"  - Ortalama Precision: {sum(deepsource_precisions)/len(deepsource_precisions):.2%}\n")
                f.write(f"  - Ortalama Recall: {sum(deepsource_recalls)/len(deepsource_recalls):.2%}\n")
                f.write(f"  - Ortalama F1 Score: {sum(deepsource_f1_scores)/len(deepsource_f1_scores):.2%}\n")
                f.write(f"  - Toplam TP: {sum(deepsource_tps)}, FP: {sum(deepsource_fps)}, FN: {sum(deepsource_fns)}\n\n")
            
            # Karşılaştırma
            if snyk_precisions and deepsource_precisions:
                f.write("KARŞILAŞTIRMA:\n")
                if sum(snyk_precisions)/len(snyk_precisions) > sum(deepsource_precisions)/len(deepsource_precisions):
                    f.write(f"  Precision: Snyk Code daha iyi ({sum(snyk_precisions)/len(snyk_precisions):.2%} vs {sum(deepsource_precisions)/len(deepsource_precisions):.2%})\n")
                else:
                    f.write(f"  Precision: DeepSource daha iyi ({sum(deepsource_precisions)/len(deepsource_precisions):.2%} vs {sum(snyk_precisions)/len(snyk_precisions):.2%})\n")
                
                if sum(snyk_recalls)/len(snyk_recalls) > sum(deepsource_recalls)/len(deepsource_recalls):
                    f.write(f"  Recall: Snyk Code daha iyi ({sum(snyk_recalls)/len(snyk_recalls):.2%} vs {sum(deepsource_recalls)/len(deepsource_recalls):.2%})\n")
                else:
                    f.write(f"  Recall: DeepSource daha iyi ({sum(deepsource_recalls)/len(deepsource_recalls):.2%} vs {sum(snyk_recalls)/len(snyk_recalls):.2%})\n")
                
                if sum(snyk_f1_scores)/len(snyk_f1_scores) > sum(deepsource_f1_scores)/len(deepsource_f1_scores):
                    f.write(f"  F1 Score: Snyk Code daha iyi ({sum(snyk_f1_scores)/len(snyk_f1_scores):.2%} vs {sum(deepsource_f1_scores)/len(deepsource_f1_scores):.2%})\n")
                else:
                    f.write(f"  F1 Score: DeepSource daha iyi ({sum(deepsource_f1_scores)/len(deepsource_f1_scores):.2%} vs {sum(snyk_f1_scores)/len(snyk_f1_scores):.2%})\n")
    
    print(f"Özet rapor kaydedildi: {report_file}")


if __name__ == "__main__":
    run_comprehensive_tests()

