"""
Snyk Code Runner Modülü

Bu modül, Snyk Code CLI kullanarak kod analizi yapar ve sonuçları
standart metrik formatına normalize eder.

Snyk Organization:
- Organization Name: SmartTestAI-demo
- Organization ID: 31b7aa9b-c8a6-443a-8858-4576d54abd64

Proje Yapısı İçindeki Yeri:
- backend/metric_runner.py: Bu dosya
- backend/metrics/snyk_metrics.py: Snyk metrik normalizasyonu
- results/: Tarama sonuçları kaydedilir

Ana Fonksiyonlar:
- run_snyk_code_scan(): Snyk CLI ile tarama yapar (organizasyon bilgisi ile)
- save_scan_result(): Sonuçları JSON formatında kaydeder
- run_code_scan_and_save(): Tam tarama ve kaydetme işlemi

Kullanım:
    cd backend
    python metric_runner.py
    veya
    from metric_runner import run_code_scan_and_save
    result = run_code_scan_and_save("flask_demo")
"""

import json
import subprocess
import os
import shutil
from datetime import datetime
from pathlib import Path
from metrics.snyk_metrics import SnykMetrics
from metrics.advanced_metrics import AdvancedMetricsCalculator

# Ground truth dosyasının yolu
GROUND_TRUTH_FILE = "../test_projects/ground_truth.json"

def load_ground_truth(project_name: str) -> list:
    """
    Ground truth verilerini yükler
    
    Args:
        project_name: Proje adı
    
    Returns:
        list: Ground truth issue'ları listesi (proje için varsa)
    """
    try:
        if not Path(GROUND_TRUTH_FILE).exists():
            return []
        
        with open(GROUND_TRUTH_FILE, "r", encoding="utf-8") as f:
            ground_truth_data = json.load(f)
        
        # Proje adına göre ground truth verilerini döndür
        return ground_truth_data.get(project_name, [])
    except Exception as e:
        print(f"WARNING: Ground truth yüklenemedi: {e}")
        return []

# Snyk Organization Bilgileri
SNYK_ORG_NAME = "SmartTestAI-demo"
SNYK_ORG_ID = "31b7aa9b-c8a6-443a-8858-4576d54abd64"

def find_snyk_cli():
    """
    Snyk CLI'nin yolunu otomatik olarak bulur.
    Birden fazla yolu kontrol eder.
    
    Returns:
        str: Snyk CLI'nin tam yolu veya None
    """
    # Windows için olası yollar
    possible_paths = [
        # npm global install yolu (kullanıcı bazlı)
        os.path.expanduser(r"~\AppData\Roaming\npm\snyk.cmd"),
        # npm global install yolu (system-wide)
        r"C:\Program Files\nodejs\npm-global\node_modules\.bin\snyk.cmd",
        # Node.js global bin
        r"C:\Program Files\nodejs\snyk.cmd",
        # PATH'de arıyoruz
        shutil.which("snyk"),
        shutil.which("snyk.cmd"),
    ]
    
    # Kullanıcı adını alarak dinamik yol oluştur
    username = os.getenv("USERNAME") or os.getenv("USER") or os.path.expanduser("~").split(os.sep)[-1]
    if username:
        user_path = rf"C:\Users\{username}\AppData\Roaming\npm\snyk.cmd"
        if user_path not in possible_paths:
            possible_paths.insert(0, user_path)
    
    # Her yolu kontrol et
    for path in possible_paths:
        if path and Path(path).exists():
            return path
    
    # PATH'de "snyk" komutunu dene
    try:
        result = subprocess.run(["snyk", "--version"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              timeout=5)
        if result.returncode == 0:
            return "snyk"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    try:
        result = subprocess.run(["snyk.cmd", "--version"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              timeout=5)
        if result.returncode == 0:
            return "snyk.cmd"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    return None

# Snyk CLI yolunu otomatik bul
SNYK_PATH = find_snyk_cli()

if not SNYK_PATH:
    print("WARNING: Snyk CLI bulunamadı. Lütfen Snyk CLI'yi kurun: npm install -g snyk")
    print("Alternatif olarak backend/metric_runner.py dosyasında SNYK_PATH değerini manuel olarak ayarlayabilirsiniz.")

# Sonuç dosyalarının kaydedileceği klasör
RESULTS_DIR = "../results"

def extract_issues_from_snyk_result(raw_data: dict) -> list:
    """
    Snyk SARIF formatından issue'ları çıkarır
    
    Args:
        raw_data: Snyk'ten gelen ham JSON çıktısı
    
    Returns:
        list: Issue listesi (dict formatında)
    """
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
        tool_name: Araç adı ("snyk_code")
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

def run_snyk_code_scan(target_path: str) -> dict:
    """
    Snyk Code CLI kullanarak kod analizi yapar
    
    Args:
        target_path: Taranacak proje klasörünün yolu
    
    Returns:
        dict: Snyk'ten gelen JSON formatındaki ham sonuç
        (SARIF formatı veya eski vulnerabilities formatı)
    
    Raises:
        RuntimeError: Snyk CLI hatası veya tarama başarısız olduğunda
    """
    # Snyk CLI komutunu oluştur
    # --json flag'i ile JSON formatında çıktı al
    # --org parametresi ile organizasyon belirtilir
    cmd = [
        SNYK_PATH, 
        "code", 
        "test", 
        target_path, 
        "--json",
        "--org", SNYK_ORG_ID  # Organization ID kullan
    ]
    
    # Snyk CLI kontrolü
    if not SNYK_PATH:
        raise RuntimeError(
            "Snyk CLI bulunamadı. Lütfen Snyk CLI'yi kurun:\n"
            "  npm install -g snyk\n"
            "ve ardından authenticate edin:\n"
            "  snyk auth\n"
            "Alternatif olarak backend/metric_runner.py dosyasında SNYK_PATH değerini manuel olarak ayarlayabilirsiniz."
        )
    
    if SNYK_PATH and SNYK_PATH not in ["snyk", "snyk.cmd"] and not Path(SNYK_PATH).exists():
        raise RuntimeError(
            f"Snyk CLI dosyası bulunamadı: {SNYK_PATH}\n"
            "Lütfen Snyk CLI'nin kurulu olduğundan ve yolun doğru olduğundan emin olun.\n"
            "backend/metric_runner.py dosyasında SNYK_PATH değerini kontrol edin."
        )
    
    try:
        # Snyk CLI komutunu çalıştır
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=600  # 10 dakika timeout
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"Snyk CLI bulunamadı. Yol: {SNYK_PATH}\n"
            "Lütfen Snyk CLI'yi kurun: npm install -g snyk\n"
            "ve ardından authenticate edin: snyk auth"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Snyk taraması zaman aşımına uğradı (10 dakikadan fazla sürdü)")
    except Exception as e:
        raise RuntimeError(f"Snyk CLI çalıştırma hatası: {str(e)}")

    # Hata kontrolü
    if result.returncode != 0:
        error_msg = result.stderr or "Unknown error"
        # Eğer stdout'ta JSON varsa, onu kullanmayı dene (bazı durumlarda hata olsa bile sonuç döner)
        if result.stdout:
            try:
                output = json.loads(result.stdout)
                # Eğer valid JSON ise ve runs içeriyorsa, hataya rağmen döndür
                if "runs" in output or "vulnerabilities" in output:
                    return output
            except json.JSONDecodeError:
                pass
        
        raise RuntimeError(f"Snyk CLI hatası (return code: {result.returncode}): {error_msg}")

    # JSON çıktısını parse et
    if not result.stdout or not result.stdout.strip():
        raise RuntimeError("Snyk CLI hiçbir çıktı döndürmedi")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Snyk çıktısı JSON formatında değil: {str(e)}\nÇıktı: {result.stdout[:500]}")

def save_scan_result(raw_output: dict, tool_name: str, project_name: str) -> str:
    """
    Tarama sonucunu results/ klasörüne kaydeder.
    
    Args:
        raw_output: Snyk'ten gelen ham JSON çıktısı
        tool_name: Kullanılan araç adı (örn: "snyk_code")
        project_name: Test projesi adı (örn: "nodejs-goof", "flask_demo")
    
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

def run_code_scan_and_save(project_name: str) -> dict:
    """
    Belirli bir proje için code taraması yapar ve sonucu kaydeder.
    API'den çağrılabilir fonksiyon.
    
    Args:
        project_name: Test projesi adı ("flask_demo" veya "nodejs-goof")
    
    Returns:
        {
            "success": bool,
            "project": str,
            "file_path": str,
            "metric_result": MetricResult (dict olarak),
            "error": str (varsa)
        }
    """
    import time
    try:
        # Proje yolunu oluştur (uploaded klasörü de kontrol et)
        target_path = f"../test_projects/{project_name}"
        if not Path(target_path).exists():
            # Uploaded klasöründe olabilir
            target_path = f"../test_projects/uploaded/{project_name}"
        
        # Proje var mı kontrol et
        if not Path(target_path).exists():
            return {
                "success": False,
                "project": project_name,
                "error": f"Project '{project_name}' not found in test_projects/"
            }
        
        # Tarama süresini ölç (gerçek süre)
        scan_start_time = time.time()
        
        # Tarama yap
        raw_output = run_snyk_code_scan(target_path)
        
        # Gerçek tarama süresini hesapla
        actual_scan_duration = time.time() - scan_start_time
        
        # Sonucu kaydet
        saved_path = save_scan_result(raw_output, "snyk_code", project_name)
        
        # Temel metrikleri hesapla
        metric = SnykMetrics()
        metric_result = metric.calculate(raw_output)
        
        # Gerçek tarama süresini metric_result'a ekle (eğer 0 ise)
        if metric_result.scan_duration == 0.0:
            metric_result.scan_duration = actual_scan_duration
        
        # Issue'ları çıkar (advanced metrics için)
        detected_issues = extract_issues_from_snyk_result(raw_output)
        
        # Ground truth verilerini yükle
        ground_truth = load_ground_truth(project_name)
        if ground_truth:
            print(f"Ground truth yüklendi: {len(ground_truth)} issue bulundu")
        else:
            print(f"Ground truth bulunamadı veya boş: {project_name}")
        
        # Gelişmiş metrikleri hesapla (gerçek tarama süresi ile)
        calculator = AdvancedMetricsCalculator()
        advanced_result = calculator.calculate_all_advanced_metrics(
            raw_data=raw_output,
            detected_issues=detected_issues,
            ground_truth=ground_truth,  # Ground truth verilerini kullan
            scan_duration=metric_result.scan_duration  # Gerçek süre kullanılıyor
        )
        
        # Advanced metrics sonucunu kaydet
        advanced_file_path = save_advanced_metrics_result(
            "snyk_code",
            project_name,
            metric_result,
            advanced_result,
            ground_truth=ground_truth
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
    target_path = "../test_projects/flask_demo"
    project_name = Path(target_path).name
    
    raw_output = run_snyk_code_scan(target_path)
    
    # Sonucu kaydet
    saved_path = save_scan_result(raw_output, "snyk_code", project_name)
    
    # Metrik hesapla
    metric = SnykMetrics()
    result = metric.calculate(raw_output)

    print("\n=== SMARTTESTAI METRIC OUTPUT ===")
    print(result)
    print("================================")

if __name__ == "__main__":
    main()
