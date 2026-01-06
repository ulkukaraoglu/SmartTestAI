"""
DeepSource Runner Modülü

Bu modül, DeepSource GraphQL API kullanarak kod analizi yapar ve sonuçları
standart metrik formatına normalize eder.

Proje Yapısı İçindeki Yeri:
- backend/deepsource_runner.py: Bu dosya
- backend/metrics/deepsource_metrics.py: DeepSource metrik normalizasyonu
- results/: Tarama sonuçları kaydedilir

DeepSource repository-based çalışır, yani local path yerine GitHub repository
bilgisi kullanılır.

Ana Fonksiyonlar:
- run_deepsource_scan(): DeepSource API ile tarama yapar
- save_scan_result(): Sonuçları JSON formatında kaydeder
- run_deepsource_scan_and_save(): Tam tarama ve kaydetme işlemi

Kullanım:
    cd backend
    python deepsource_runner.py
    veya
    from deepsource_runner import run_deepsource_scan_and_save
    result = run_deepsource_scan_and_save("flask_demo")

Environment Variables:
    DEEPSOURCE_API_TOKEN: DeepSource API token (gerekli)
    DEEPSOURCE_API_URL: API endpoint (default: https://api.deepsource.io/graphql/)
    DEEPSOURCE_REPO_OWNER: GitHub repository owner (default: zeliha-orhan)
    DEEPSOURCE_REPO_NAME: Repository name (default: SmartTestAI)
    DEEPSOURCE_VCS_PROVIDER: VCS provider (default: GITHUB)
"""

import json
import subprocess
import os
import requests
from datetime import datetime
from pathlib import Path
from metrics.deepsource_metrics import DeepSourceMetrics
from metrics.advanced_metrics import AdvancedMetricsCalculator

# Sonuç dosyalarının kaydedileceği klasör
RESULTS_DIR = "../results"


def extract_issues_from_deepsource_result(raw_data: dict) -> list:
    """
    DeepSource GraphQL formatından veya mock formatından issue'ları çıkarır
    
    Args:
        raw_data: DeepSource'tan gelen ham JSON çıktısı (GraphQL veya mock format)
    
    Returns:
        list: Issue listesi (dict formatında)
    """
    issues = []
    
    # GraphQL formatı (gerçek API)
    if "data" in raw_data and "repository" in raw_data["data"]:
        repo_data = raw_data["data"]["repository"]
        if "issues" in repo_data and "edges" in repo_data["issues"]:
            for edge in repo_data["issues"]["edges"]:
                if "node" in edge and "issue" in edge["node"]:
                    issue = edge["node"]["issue"]
                    issues.append({
                        "file": "unknown",  # DeepSource API'sinde dosya bilgisi yok
                        "line": -1,
                        "type": issue.get("shortcode", ""),
                        "severity": issue.get("severity", ""),
                        "description": issue.get("title", "")
                    })
    
    # Mock format (test için)
    elif "issues" in raw_data:
        for issue in raw_data["issues"]:
            issues.append({
                "file": issue.get("file", "unknown"),
                "line": issue.get("line", -1),
                "type": issue.get("issue_code", ""),
                "severity": issue.get("severity", "").upper(),  # MAJOR, MINOR, etc.
                "description": issue.get("message", "")
            })
    
    return issues

def save_advanced_metrics_result(
    tool_name: str,
    project_name: str,
    basic_result,
    advanced_result,
    ground_truth: list = None
) -> str:
    """
    Gelişmiş metrik sonuçlarını results/ klasörüne kaydeder
    
    Args:
        tool_name: Araç adı ("deepsource")
        project_name: Proje adı
        basic_result: Temel metrik sonucu (MetricResult)
        advanced_result: Gelişmiş metrik sonucu (AdvancedMetricResult)
        ground_truth: Ground truth listesi (opsiyonel)
    
    Returns:
        str: Kaydedilen dosyanın yolu
    """
    results_path = Path(RESULTS_DIR)
    results_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{tool_name}_advanced_metrics_{project_name}_{timestamp}.json"
    file_path = results_path / filename
    
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
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2, ensure_ascii=False)
    
    return str(file_path)

def _get_mock_deepsource_output(target_path: str) -> dict:
    """
    Test için mock DeepSource çıktısı döner.
    
    Gerçek DeepSource API'sine erişim olmadığında veya test için kullanılır.
    Gerçek API formatını simüle eder.
    
    Args:
        target_path: Taranacak proje yolu (kullanılmıyor, mock için)
    
    Returns:
        dict: Mock DeepSource çıktısı
    """
    # Mock format - DeepSource'un gerçek formatına göre güncellenmeli
    return {
        "issues": [
            {
                "severity": "high",
                "issue_code": "DS-PY-001",
                "message": "Mock DeepSource issue - High severity",
                "file": "app.py",
                "line": 10
            },
            {
                "severity": "medium",
                "issue_code": "DS-PY-002",
                "message": "Mock DeepSource issue - Medium severity",
                "file": "app.py",
                "line": 20
            }
        ],
        "scan_duration": 5.2,
        "total_issues": 2
    }

# ============================================
# DEEPSOURCE YAPILANDIRMASI
# ============================================

# DeepSource API token (environment variable'dan alınır)
# Token almak için: https://deepsource.io/settings/api-tokens
DEEPSOURCE_API_TOKEN = os.getenv("DEEPSOURCE_API_TOKEN", "")

# DeepSource GraphQL API endpoint
DEEPSOURCE_API_URL = os.getenv("DEEPSOURCE_API_URL", "https://api.deepsource.io/graphql/")

# DeepSource CLI yolu (eğer CLI kuruluysa)
DEEPSOURCE_CLI_PATH = os.getenv("DEEPSOURCE_CLI_PATH", "deepsource")

# Repository bilgileri (environment variable'dan veya default)
# DeepSource repository-based çalışır, bu yüzden GitHub repository bilgisi gerekli
DEEPSOURCE_REPO_OWNER = os.getenv("DEEPSOURCE_REPO_OWNER", "zeliha-orhan")
DEEPSOURCE_REPO_NAME = os.getenv("DEEPSOURCE_REPO_NAME", "SmartTestAI")
DEEPSOURCE_VCS_PROVIDER = os.getenv("DEEPSOURCE_VCS_PROVIDER", "GITHUB")  # GITHUB, GITLAB, BITBUCKET

# Debug: Environment variable'ları kontrol et
if not DEEPSOURCE_API_TOKEN:
    print("WARNING: DEEPSOURCE_API_TOKEN environment variable bulunamadi!")
else:
    print(f"INFO: DeepSource API token bulundu (ilk 10 karakter: {DEEPSOURCE_API_TOKEN[:10]}...)")
print(f"INFO: Repository: {DEEPSOURCE_REPO_OWNER}/{DEEPSOURCE_REPO_NAME}")

def run_deepsource_scan(target_path: str) -> dict:
    """
    DeepSource taraması yapar ve JSON çıktısı döner.
    
    DeepSource repository-based çalışır, bu yüzden local path yerine
    GitHub repository bilgisi kullanılır. Üç yöntem denemesi yapılır:
    
    1. CLI yöntemi: DeepSource CLI kuruluysa kullanılır
    2. GraphQL API: DeepSource GraphQL API ile repository issues alınır
    3. Mock modu: Test için mock veri döner
    
    Args:
        target_path: Taranacak proje yolu (CLI için kullanılır, API için kullanılmaz)
    
    Returns:
        dict: DeepSource'un JSON çıktısı (GraphQL response formatı)
    
    Raises:
        RuntimeError: API hatası veya timeout durumunda
    """
    # ============================================
    # YÖNTEM 1: DeepSource CLI kullanımı
    # ============================================
    # Eğer DeepSource CLI kuruluysa, local path üzerinde analiz yapar
    try:
        result = subprocess.run(
            [DEEPSOURCE_CLI_PATH, "analyze", target_path, "--format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300  # 5 dakika timeout
        )
        
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        elif result.stdout:
            # Bazı durumlarda hata olsa bile stdout'ta JSON olabilir
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                raise RuntimeError(f"DeepSource CLI error: {result.stderr}")
        else:
            raise RuntimeError(f"DeepSource CLI failed: {result.stderr}")
    
    except FileNotFoundError:
        # CLI bulunamadı, API kullanmayı dene
        pass
    except subprocess.TimeoutExpired:
        raise RuntimeError("DeepSource scan timeout (exceeded 5 minutes)")
    
    # ============================================
    # YÖNTEM 2: DeepSource GraphQL API kullanımı
    # ============================================
    # DeepSource repository-based çalışır, bu yüzden GitHub repository bilgisi kullanılır
    if DEEPSOURCE_API_TOKEN:
        try:
            # API isteği için header'ları hazırla
            headers = {
                "Authorization": f"Bearer {DEEPSOURCE_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # GraphQL query: Repository issues'ları al
            # first: 100 - İlk 100 issue'yu al (pagination için daha fazla gerekebilir)
            query = {
                "query": """
                query {
                    repository(login: "%s", name: "%s", vcsProvider: %s) {
                        name
                        issues(first: 100) {
                            totalCount
                            edges {
                                node {
                                    issue {
                                        shortcode
                                        title
                                        severity
                                        category
                                    }
                                }
                            }
                        }
                    }
                }
                """ % (DEEPSOURCE_REPO_OWNER, DEEPSOURCE_REPO_NAME, DEEPSOURCE_VCS_PROVIDER)
            }
            
            # GraphQL API'ye POST isteği gönder
            response = requests.post(
                DEEPSOURCE_API_URL,
                headers=headers,
                json=query,
                timeout=300  # 5 dakika timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # GraphQL hata kontrolü
                if "errors" in result:
                    error_msg = f"DeepSource GraphQL error: {result['errors']}"
                    print(f"WARNING: {error_msg}")
                    # Hata olsa bile mock moda geçmek yerine boş sonuç döndür
                    return {
                        "data": {
                            "repository": {
                                "name": DEEPSOURCE_REPO_NAME,
                                "issues": {
                                    "totalCount": 0,
                                    "edges": []
                                }
                            }
                        }
                    }
                # Başarılı - boş sonuç da geçerli (repository'de issue yok)
                return result
            else:
                error_msg = f"DeepSource API error: {response.status_code} - {response.text}"
                print(f"WARNING: {error_msg}")
                # API hatası - mock moda geç
                return _get_mock_deepsource_output(target_path)
        
        except requests.exceptions.RequestException as e:
            error_msg = f"DeepSource API request failed: {str(e)}"
            print(f"WARNING: {error_msg}")
            # Network hatası - mock moda geç
            return _get_mock_deepsource_output(target_path)
        except Exception as e:
            error_msg = f"DeepSource API unexpected error: {str(e)}"
            print(f"WARNING: {error_msg}")
            # Beklenmeyen hata - mock moda geç
            return _get_mock_deepsource_output(target_path)
    
    # ============================================
    # YÖNTEM 3: Mock/Test verisi
    # ============================================
    # API token yoksa veya tüm yöntemler başarısız olduysa mock moda geç
    print("WARNING: DeepSource API token bulunamadi veya API cagrisi basarisiz. Test modu kullaniliyor...")
    return _get_mock_deepsource_output(target_path)


def save_scan_result(raw_output: dict, tool_name: str, project_name: str) -> str:
    """
    Tarama sonucunu results/ klasörüne kaydeder.
    
    Args:
        raw_output: DeepSource'ten gelen ham JSON çıktısı
        tool_name: Kullanılan araç adı (örn: "deepsource")
        project_name: Test projesi adı
    
    Returns:
        Kaydedilen dosyanın yolu
    """
    # results klasörünü oluştur
    results_path = Path(RESULTS_DIR)
    results_path.mkdir(parents=True, exist_ok=True)
    
    # Dosya adını oluştur: tool_project_timestamp.json
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{tool_name}_{project_name}_{timestamp}.json"
    file_path = results_path / filename
    
    # JSON'u kaydet
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(raw_output, f, indent=2, ensure_ascii=False)
    
    print(f"Tarama sonucu kaydedildi: {file_path}")
    return str(file_path)


def run_deepsource_scan_and_save(project_name: str) -> dict:
    """
    Belirli bir proje için DeepSource taraması yapar ve sonucu kaydeder.
    API'den çağrılabilir fonksiyon.
    
    Args:
        project_name: Test projesi adı
    
    Returns:
        {
            "success": bool,
            "project": str,
            "file_path": str,
            "metric_result": MetricResult (dict olarak),
            "error": str (varsa)
        }
    """
    try:
        # Proje yolunu oluştur
        target_path = f"../test_projects/{project_name}"
        
        # Proje var mı kontrol et
        if not Path(target_path).exists():
            return {
                "success": False,
                "project": project_name,
                "error": f"Project '{project_name}' not found in test_projects/"
            }
        
        # Tarama yap
        raw_output = run_deepsource_scan(target_path)
        
        # Sonucu kaydet
        saved_path = save_scan_result(raw_output, "deepsource", project_name)
        
        # Temel metrikleri hesapla
        metric = DeepSourceMetrics()
        metric_result = metric.calculate(raw_output)
        
        # Issue'ları çıkar (advanced metrics için)
        detected_issues = extract_issues_from_deepsource_result(raw_output)
        
        # Gelişmiş metrikleri hesapla
        calculator = AdvancedMetricsCalculator()
        advanced_result = calculator.calculate_all_advanced_metrics(
            raw_data=raw_output,
            detected_issues=detected_issues,
            ground_truth=None,  # Ground truth opsiyonel
            scan_duration=metric_result.scan_duration
        )
        
        # Advanced metrics sonucunu kaydet
        advanced_file_path = save_advanced_metrics_result(
            "deepsource",
            project_name,
            metric_result,
            advanced_result,
            ground_truth=None
        )
        
        # MetricResult'ı dict'e çevir
        metric_dict = {
            "tool_name": metric_result.tool_name,
            "critical": metric_result.critical,
            "high": metric_result.high,
            "medium": metric_result.medium,
            "low": metric_result.low,
            "total_issues": metric_result.total_issues,
            "scan_duration": metric_result.scan_duration
        }
        
        # Advanced metrics'i dict'e çevir
        advanced_metrics_dict = {
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
        }
        
        return {
            "success": True,
            "project": project_name,
            "file_path": saved_path,
            "advanced_metrics_file_path": advanced_file_path,
            "metric_result": metric_dict,
            "advanced_metrics": advanced_metrics_dict
        }
        
    except Exception as e:
        return {
            "success": False,
            "project": project_name,
            "error": str(e)
        }


def main():
    """
    Test için main fonksiyonu
    
    flask_demo projesi için DeepSource taraması yapar,
    sonuçları kaydeder ve normalize edilmiş metrikleri gösterir.
    """
    target_path = "../test_projects/flask_demo"
    project_name = Path(target_path).name
    
    # DeepSource taraması yap
    raw_output = run_deepsource_scan(target_path)
    
    # Sonucu kaydet
    saved_path = save_scan_result(raw_output, "deepsource", project_name)
    
    # Metrik hesapla ve normalize et
    metric = DeepSourceMetrics()
    result = metric.calculate(raw_output)

    # Sonuçları yazdır
    print("\n=== SMARTTESTAI METRIC OUTPUT (DEEPSOURCE) ===")
    print(result)
    print("================================")

if __name__ == "__main__":
    main()

