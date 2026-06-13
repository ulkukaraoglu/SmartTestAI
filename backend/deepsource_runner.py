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
import hashlib
import time
import requests
from datetime import datetime
from pathlib import Path
from metrics.deepsource_metrics import DeepSourceMetrics
from metrics.advanced_metrics import AdvancedMetricsCalculator
import github_runner

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
                node = edge.get("node", {})
                if "issue" not in node:
                    continue
                issue = node["issue"]
                # Her issue'nun gerçek dosya/satır konumlarını (occurrences) çıkar.
                # Böylece ground truth ile dosya+satır bazında eşleştirme yapılabilir.
                occ_edges = node.get("occurrences", {}).get("edges", [])
                if occ_edges:
                    for occ_edge in occ_edges:
                        occ = occ_edge.get("node", {})
                        file_path = occ.get("path", "")
                        file_name = file_path.split("/")[-1] if file_path else "unknown"
                        issues.append({
                            "file": file_name,
                            "line": occ.get("beginLine", -1),
                            "type": issue.get("shortcode", ""),
                            "severity": issue.get("severity", ""),
                            "description": issue.get("title", "")
                        })
                else:
                    # Occurrences gelmediyse (eski/temel sorgu), en azından issue'yu kaydet
                    issues.append({
                        "file": "unknown",
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

def _tag_scan_mode(data: dict, mode: str) -> dict:
    """
    Tarama sonucuna, sonucun kaynağını belirten bir mod etiketi ekler.

    Mod değerleri:
    - "cli":        DeepSource CLI ile yüklenen kod yerelde tarandı (gerçek/doğru)
    - "repository": Gerçek GraphQL API; sonuçlar yapılandırılmış repo geneline aittir
                    (yüklenen dosyalara özel DEĞİL)
    - "mock":       DeepSource bağlı değil; demo/sahte veri döndürülüyor

    Args:
        data: Tarama ham çıktısı
        mode: Mod etiketi

    Returns:
        dict: Etiketlenmiş ham çıktı
    """
    if isinstance(data, dict):
        data["_deepsource_scan_mode"] = mode
    return data


def _unavailable_output(reason: str) -> dict:
    """
    DeepSource gerçek veri döndüremediğinde "kullanılamıyor" çıktısı üretir.

    Mock/sahte veri YERİNE kullanılır. Boş ama geçerli bir GraphQL yapısı döner
    (issue sayısı 0), ayrıca neden ve mod etiketlerini taşır. Böylece arayüz
    sahte sayı göstermez; bunun yerine açık bir "kullanılamıyor" durumu gösterir.

    reason değerleri:
    - "uploaded":        Yüklenen dosya bağlı repoda değil (DeepSource tarayamaz)
    - "no_token":        DEEPSOURCE_API_TOKEN ayarlı değil
    - "no_github_token": Geçici commit için GITHUB_TOKEN/repo bilgisi yok (Yol B)
    - "push_failed":     Dosyalar repoya gönderilemedi/silinemedi (GitHub hatası)
    - "run_timeout":     DeepSource analizi zaman aşımına uğradı (commit beklenirken)
    - "run_error":       DeepSource analizi başarısız/iptal oldu
    - "api_error":       API/GraphQL hatası
    - "network_error":   Ağ hatası

    Args:
        reason: Kullanılamama nedeni

    Returns:
        dict: Etiketli boş çıktı
    """
    return {
        "_deepsource_scan_mode": "unavailable",
        "_deepsource_reason": reason,
        "data": {
            "repository": {
                "name": DEEPSOURCE_REPO_NAME,
                "issues": {"totalCount": 0, "edges": []}
            }
        }
    }

# ============================================
# DEEPSOURCE YAPILANDIRMASI
# ============================================

# DeepSource API token (environment variable'dan alınır)
# Token almak için: https://deepsource.io/settings/api-tokens
DEEPSOURCE_API_TOKEN = os.getenv("DEEPSOURCE_API_TOKEN", "")

# DeepSource GraphQL API endpoint
# Not: Güncel resmi domain api.deepsource.com'dur (eski api.deepsource.io yerine).
DEEPSOURCE_API_URL = os.getenv("DEEPSOURCE_API_URL", "https://api.deepsource.com/graphql/")

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

def _fetch_deepsource_issues_for_path(headers: dict, repo_path: str) -> dict:
    """
    Bağlı repodaki tüm issue'ları (occurrences ile) sayfalayarak çeker ve
    yalnızca `repo_path` klasörü altındaki occurrence'lara sahip olanları döndürür.

    DeepSource'un `issues(path:)` filtresi tek bir DOSYA yolu beklediğinden
    (klasör verince boş döner), klasör bazlı filtrelemeyi burada kendimiz yapıyoruz.
    Böylece "test_projects/<proje>/" altındaki gerçek issue'ları güvenle alırız.

    Args:
        headers: Authorization header'ları
        repo_path: Repo içindeki klasör yolu (ör. "test_projects/flask_demo/")

    Returns:
        dict: GraphQL response benzeri yapı (yalnızca eşleşen edges ile)

    Raises:
        RuntimeError: API/GraphQL hatasında
    """
    norm = repo_path.strip("/")  # "test_projects/flask_demo"
    query_str = """
    query($after: String) {
        repository(login: "%s", name: "%s", vcsProvider: %s) {
            name
            issues(first: 100, after: $after) {
                totalCount
                pageInfo { hasNextPage endCursor }
                edges {
                    node {
                        issue { shortcode title severity category }
                        occurrences(first: 100) {
                            edges { node { path beginLine endLine } }
                        }
                    }
                }
            }
        }
    }
    """ % (DEEPSOURCE_REPO_OWNER, DEEPSOURCE_REPO_NAME, DEEPSOURCE_VCS_PROVIDER)

    filtered_edges = []
    repo_name = DEEPSOURCE_REPO_NAME
    after = None
    max_pages = 50  # güvenlik sınırı (5000 issue'ya kadar)

    for _ in range(max_pages):
        response = requests.post(
            DEEPSOURCE_API_URL,
            headers=headers,
            json={"query": query_str, "variables": {"after": after}},
            timeout=300
        )
        if response.status_code != 200:
            raise RuntimeError(f"DeepSource API error: {response.status_code} - {response.text}")

        data = response.json()
        if "errors" in data:
            raise RuntimeError(f"DeepSource GraphQL error: {data['errors']}")

        repo = (data.get("data") or {}).get("repository") or {}
        repo_name = repo.get("name", repo_name)
        issues = repo.get("issues", {}) or {}

        for edge in issues.get("edges", []):
            node = edge.get("node", {})
            occ_edges = node.get("occurrences", {}).get("edges", [])
            # Bu issue'nun, hedef klasör altındaki occurrence'larını seç
            matched = []
            for oe in occ_edges:
                path = (oe.get("node", {}).get("path", "") or "").strip("/")
                if path == norm or path.startswith(norm + "/"):
                    matched.append(oe)
            if matched:
                filtered_edges.append({
                    "node": {
                        "issue": node.get("issue", {}),
                        "occurrences": {"edges": matched}
                    }
                })

        page_info = issues.get("pageInfo", {})
        if page_info.get("hasNextPage"):
            after = page_info.get("endCursor")
        else:
            break

    return {
        "data": {
            "repository": {
                "name": repo_name,
                "issues": {
                    "totalCount": len(filtered_edges),
                    "edges": filtered_edges
                }
            }
        }
    }


# ============================================
# YOL B: Yüklenen kodu repoya geçici koyup tarama
# ============================================
# Akış: içerik hash'i ile önbelleğe bak -> yoksa dosyaları repoya geçici commit'le ->
# DeepSource analizini (commit'e göre) bekle -> sonuçları çek -> geçici dosyaları sil.

# Yüklenen taramaların önbellek dosyası (aynı içerik tekrar yüklenirse tekrar uğraşma)
UPLOAD_CACHE_FILE = "../results/uploaded_ds_cache.json"

# DeepSource analizini beklerken kullanılan zaman aşımı ve sorgu aralığı (saniye)
RUN_POLL_TIMEOUT = int(os.getenv("DEEPSOURCE_RUN_TIMEOUT", "600"))   # toplam bekleme bütçesi
RUN_POLL_INTERVAL = int(os.getenv("DEEPSOURCE_RUN_INTERVAL", "10"))  # yoklamalar arası bekleme
RUN_POLL_REQUEST_TIMEOUT = int(os.getenv("DEEPSOURCE_RUN_REQUEST_TIMEOUT", "45"))  # istek başına timeout
RUN_POLL_INITIAL_DELAY = int(os.getenv("DEEPSOURCE_RUN_INITIAL_DELAY", "20"))  # ilk yoklamadan önce bekle


def _hash_upload_dir(local_dir: str) -> str:
    """
    Yüklenen klasörün içeriğine göre kararlı bir SHA-256 hash üretir.

    Dosya adı + içerik birlikte hashlenir; böylece aynı dosyalar tekrar
    yüklendiğinde aynı hash elde edilir (önbellek ve "var mı yok mu" kontrolü için).
    """
    digest = hashlib.sha256()
    base = Path(local_dir)
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(base).as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _load_upload_cache() -> dict:
    """Yüklenen tarama önbelleğini yükler (yoksa boş döner)."""
    try:
        p = Path(UPLOAD_CACHE_FILE)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"WARNING: Yukleme onbellegi okunamadi: {e}")
    return {}


def _save_upload_cache(content_hash: str, raw_result: dict) -> None:
    """Bir içerik hash'i için tarama sonucunu önbelleğe yazar."""
    try:
        cache = _load_upload_cache()
        cache[content_hash] = raw_result
        p = Path(UPLOAD_CACHE_FILE)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
    except Exception as e:
        print(f"WARNING: Yukleme onbellegi yazilamadi: {e}")


def _wait_for_deepsource_run(headers: dict, commit_oid: str) -> str:
    """
    Belirli bir commit için DeepSource analiz çalışmasının (run) bitmesini bekler.

    DeepSource `run(commitOid:)` sorgusu ile durumu yoklar. Push edilen commit
    için analiz tetiklenene ve sonuçlanana kadar (zaman aşımına kadar) bekler.

    Args:
        headers: DeepSource Authorization header'ları
        commit_oid: Beklenen commit SHA'sı

    Returns:
        str: Terminal durum ("SUCCESS"/"FAILURE"/"SKIPPED"/"TIMEOUT"/"CANCEL")
             veya zaman aşımında "TIMEOUT".
    """
    # NOT: Kök `run(commitOid:)` sorgusu bu ağda güvenilmez (istek takılıp okuma
    # zaman aşımına düşüyor). Bunun yerine, sağlıklı çalışan `repository` sorgusunun
    # `analysisRuns` listesini kullanıp commit'imize ait run'ı buluyoruz.
    query = """
    query {
        repository(name: "%s", login: "%s", vcsProvider: %s) {
            analysisRuns(first: 20) {
                edges {
                    node {
                        commitOid
                        status
                    }
                }
            }
        }
    }
    """ % (DEEPSOURCE_REPO_NAME, DEEPSOURCE_REPO_OWNER, DEEPSOURCE_VCS_PROVIDER)

    done_states = {"SUCCESS", "FAILURE", "SKIPPED"}
    bad_states = {"TIMEOUT", "CANCEL"}
    deadline = time.time() + RUN_POLL_TIMEOUT
    short = commit_oid[:8]

    # DeepSource'un push'u alıp analiz çalışmasını (run) oluşturması zaman alır;
    # ilk yoklamadan önce kısa bir süre bekleyerek boşa istek atmayı azaltırız.
    if RUN_POLL_INITIAL_DELAY > 0:
        time.sleep(RUN_POLL_INITIAL_DELAY)

    while time.time() < deadline:
        try:
            response = requests.post(
                DEEPSOURCE_API_URL,
                headers=headers,
                json={"query": query},
                timeout=RUN_POLL_REQUEST_TIMEOUT,
            )
            if response.status_code == 200:
                data = response.json()
                repo = (data.get("data") or {}).get("repository") or {}
                edges = (repo.get("analysisRuns") or {}).get("edges", [])
                status = None
                for edge in edges:
                    node = edge.get("node") or {}
                    node_oid = node.get("commitOid") or ""
                    # Commit eşleştir (tam veya prefix; kısa/uzun SHA farkına dayanıklı)
                    if node_oid == commit_oid or node_oid.startswith(commit_oid) or commit_oid.startswith(node_oid):
                        status = node.get("status")
                        break
                if status in done_states:
                    print(f"INFO: DeepSource analizi tamamlandi (commit {short}): {status}")
                    return status
                if status in bad_states:
                    print(f"WARNING: DeepSource analizi hatali bitti (commit {short}): {status}")
                    return status
                # Run henüz yok / PENDING / READY -> beklemeye devam
                print(f"INFO: DeepSource analizi bekleniyor (commit {short}, durum={status})")
            else:
                print(f"WARNING: analysisRuns sorgusu {response.status_code}: {response.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(f"WARNING: run durumu sorgulanamadi, tekrar denenecek: {e}")
        time.sleep(RUN_POLL_INTERVAL)

    print(f"WARNING: DeepSource run zaman asimi (commit {short})")
    return "TIMEOUT"


def _scan_uploaded_via_repo(target_path: str) -> dict:
    """
    Yüklenen dosyalar için Yol B akışını yürütür.

    1. İçerik hash'ine göre önbelleğe bakar (varsa sonucu döndürür).
    2. Dosyaları repoda `uploads_tmp/<hash>/` altına geçici commit'ler.
    3. O commit için DeepSource analizinin bitmesini bekler.
    4. O klasöre ait issue'ları çeker (path-filtreli).
    5. Geçici dosyaları repodan siler (boyut artmasın).
    6. Sonucu önbelleğe yazar ve etiketleyerek döndürür.

    Args:
        target_path: Yüklenen dosyaların bulunduğu yerel klasör

    Returns:
        dict: Etiketlenmiş GraphQL benzeri çıktı veya _unavailable_output(...)
    """
    # DeepSource API token'ı olmadan analiz durumu/sonuçları çekilemez
    if not DEEPSOURCE_API_TOKEN:
        return _unavailable_output("no_token")

    content_hash = _hash_upload_dir(target_path)

    # 1) Önbellek: aynı içerik daha önce tarandıysa tekrar repoya dokunma
    cached = _load_upload_cache().get(content_hash)
    if cached:
        print(f"INFO: Yuklenen icerik onbellekte bulundu (hash {content_hash[:8]}). Repoya gerek yok.")
        return _tag_scan_mode(json.loads(json.dumps(cached)), "repository_cached")

    # 2) Geçici commit için GitHub yapılandırması gerekli
    if not github_runner.is_configured():
        print("WARNING: GITHUB_TOKEN/repo bilgisi yok. Yuklenen kod repoya gonderilemez. Sonuc: kullanilamiyor.")
        return _unavailable_output("no_github_token")

    headers = {
        "Authorization": f"Bearer {DEEPSOURCE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    subdir = content_hash[:16]
    repo_path = f"{github_runner.TMP_ROOT}/{subdir}/"
    push_info = None

    try:
        # 2) Dosyaları repoya geçici olarak gönder
        print(f"INFO: Yuklenen dosyalar repoya gonderiliyor: {repo_path}")
        push_info = github_runner.push_temp_files(target_path, subdir)
        commit_sha = push_info["commit_sha"]

        # 3) DeepSource analizinin bitmesini bekle
        print(f"INFO: DeepSource analizi bekleniyor (commit {commit_sha[:8]})...")
        status = _wait_for_deepsource_run(headers, commit_sha)
        if status == "TIMEOUT":
            return _unavailable_output("run_timeout")
        if status == "CANCEL":
            return _unavailable_output("run_error")

        # 4) Bu klasöre ait gerçek issue'ları çek (path-filtreli)
        result = _fetch_deepsource_issues_for_path(headers, repo_path)

        # 6) Önbelleğe yaz ve etiketle
        _save_upload_cache(content_hash, result)
        return _tag_scan_mode(result, "repository_temp")

    except github_runner.GitHubError as e:
        print(f"WARNING: GitHub gecici commit hatasi: {e}")
        return _unavailable_output("push_failed")
    except requests.exceptions.RequestException as e:
        print(f"WARNING: DeepSource API hatasi (uploaded): {e}")
        return _unavailable_output("network_error")
    except Exception as e:
        print(f"WARNING: Yuklenen tarama beklenmeyen hata: {e}")
        return _unavailable_output("api_error")
    finally:
        # 5) Geçici dosyaları her durumda temizle (repo boyutu artmasin)
        if push_info:
            try:
                print(f"INFO: Gecici dosyalar repodan siliniyor: {repo_path}")
                github_runner.delete_temp_path(push_info["paths"], subdir)
            except Exception as e:
                print(f"WARNING: Gecici dosyalar silinemedi ({repo_path}): {e}")


def run_deepsource_scan(target_path: str, repo_path: str = None, uploaded: bool = False) -> dict:
    """
    DeepSource taraması yapar ve JSON çıktısı döner.
    
    DeepSource repository-based çalışır, bu yüzden local path yerine
    GitHub repository bilgisi kullanılır. Üç yöntem denemesi yapılır:
    
    1. CLI yöntemi: DeepSource CLI kuruluysa kullanılır
    2. GraphQL API: DeepSource GraphQL API ile repository issues alınır
       (repo_path verilirse, sadece o klasördeki issue'lar dosya/satır
       bilgisiyle birlikte çekilir -> ground truth ile eşleştirilebilir)
    3. Mock modu: repo_path yoksa (ör. yüklenen dosya repoda değil) veya
       API çağrısı başarısız olursa mock veri döner
    
    Args:
        target_path: Taranacak proje yolu (CLI için kullanılır)
        repo_path: Bağlı repo içindeki klasör yolu (ör. "test_projects/flask_demo/").
                   None ise gerçek API atlanır (kod repoda olmadığından).
        uploaded: True ise (web'den yüklenen proje) Yol B akışı çalışır:
                  dosyalar repoya geçici commit'lenir, analiz beklenir,
                  sonuç çekilir ve dosyalar tekrar silinir.
    
    Returns:
        dict: DeepSource'un JSON çıktısı (GraphQL response formatı)
    
    Raises:
        RuntimeError: API hatası veya timeout durumunda
    """
    # ============================================
    # YÖNTEM 0: Yüklenen proje -> Yol B (repoya geçici commit + analiz + temizlik)
    # ============================================
    if uploaded:
        return _scan_uploaded_via_repo(target_path)

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
            # CLI yerelde yüklenen kodu taradı -> sonuç doğru/yüklenen koda özel
            return _tag_scan_mode(json.loads(result.stdout), "cli")
        elif result.stdout:
            # Bazı durumlarda hata olsa bile stdout'ta JSON olabilir
            try:
                return _tag_scan_mode(json.loads(result.stdout), "cli")
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
    # DeepSource repository-based çalışır, bu yüzden GitHub repository bilgisi kullanılır.
    # repo_path verildiyse (sabit test_projects), o klasöre özel gerçek veri çekilir.
    # repo_path None ise (yüklenen dosya repoda değil) gerçek API atlanır -> mock.
    if DEEPSOURCE_API_TOKEN and repo_path:
        try:
            # API isteği için header'ları hazırla
            headers = {
                "Authorization": f"Bearer {DEEPSOURCE_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # Tüm issue'ları çekip occurrence yoluna göre repo_path altına filtrele.
            # (DeepSource'un issues(path:) filtresi dosya bekler, klasör için güvenilir değil.)
            result = _fetch_deepsource_issues_for_path(headers, repo_path)
            
            # Başarılı - boş sonuç da geçerli (bu klasörde issue yok demektir)
            # NOT: Sonuçlar yalnızca bu proje klasörüne aittir (path ile filtrelendi)
            return _tag_scan_mode(result, "repository")
        
        except requests.exceptions.RequestException as e:
            error_msg = f"DeepSource API request failed: {str(e)}"
            print(f"WARNING: {error_msg}")
            # Ağ hatası - mock YOK, kullanılamıyor olarak işaretle
            return _unavailable_output("network_error")
        except Exception as e:
            error_msg = f"DeepSource API unexpected error: {str(e)}"
            print(f"WARNING: {error_msg}")
            # Beklenmeyen/GraphQL hatası - mock YOK, kullanılamıyor
            return _unavailable_output("api_error")
    
    # ============================================
    # YÖNTEM 3: Gerçek veri alınamadı -> KULLANILAMIYOR (mock YOK)
    # ============================================
    # Buraya gelmenin iki nedeni olabilir; ayrı ayrı logla ki sebep net olsun.
    if not repo_path:
        # Yüklenen dosya bağlı repoda olmadığından gerçek API kullanılamaz (tasarım gereği)
        print("INFO: Yuklenen proje bagli repoda olmadigi icin DeepSource gercek tarama yapamaz. Sonuc: kullanilamiyor.")
        return _unavailable_output("uploaded")
    elif not DEEPSOURCE_API_TOKEN:
        # Sabit test projesi ama token yok
        print("WARNING: DEEPSOURCE_API_TOKEN ayarli degil. Gercek DeepSource verisi icin token gerekli. Sonuc: kullanilamiyor.")
        return _unavailable_output("no_token")
    else:
        print("WARNING: DeepSource gercek tarama yapilamadi. Sonuc: kullanilamiyor.")
        return _unavailable_output("api_error")


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
    import time
    try:
        # Proje yolunu oluştur (uploaded klasörü de kontrol et)
        target_path = f"../test_projects/{project_name}"
        is_uploaded = False
        if not Path(target_path).exists():
            # Uploaded klasöründe olabilir
            target_path = f"../test_projects/uploaded/{project_name}"
            is_uploaded = True
        
        # Bağlı repo içindeki klasör yolunu belirle.
        # Sabit test_projects bağlı repoda olduğundan gerçek (path-filtreli) veri çekilebilir.
        # Yüklenen projeler repoda olmadığından Yol B (geçici commit) ile taranır.
        repo_path = None if is_uploaded else f"test_projects/{project_name}/"
        
        # Proje var mı kontrol et
        if not Path(target_path).exists():
            return {
                "success": False,
                "project": project_name,
                "error": f"Project '{project_name}' not found in test_projects/"
            }
        
        # Tarama süresini ölç (gerçek süre)
        scan_start_time = time.time()
        
        # Tarama yap:
        # - Sabit projeler: repo_path ile gerçek/projeye özel veri çekilir.
        # - Yüklenen projeler: uploaded=True ile Yol B (repoya geçici commit + analiz) çalışır.
        raw_output = run_deepsource_scan(target_path, repo_path=repo_path, uploaded=is_uploaded)
        
        # Tarama modunu/nedenini çıkar (ham çıktıyı kirletmemek için pop et)
        # "cli"/"repository" -> gerçek veri, "unavailable" -> gerçek veri alınamadı (mock YOK)
        scan_mode = raw_output.pop("_deepsource_scan_mode", "unavailable") if isinstance(raw_output, dict) else "unavailable"
        reason = raw_output.pop("_deepsource_reason", None) if isinstance(raw_output, dict) else None
        
        # Gerçek tarama süresini hesapla
        actual_scan_duration = time.time() - scan_start_time
        
        # DeepSource gerçek veri döndüremediyse: sahte sonuç gösterme, "kullanılamıyor" döndür
        if scan_mode == "unavailable":
            return {
                "success": True,
                "project": project_name,
                "available": False,
                "scan_mode": "unavailable",
                "reason": reason or "api_error",
                "file_path": None,
                "advanced_metrics_file_path": None,
                "metric_result": {
                    "tool_name": "DeepSource",
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "total_issues": 0,
                    "scan_duration": actual_scan_duration
                },
                "advanced_metrics": {}
            }
        
        # Sonucu kaydet
        saved_path = save_scan_result(raw_output, "deepsource", project_name)
        
        # Temel metrikleri hesapla
        metric = DeepSourceMetrics()
        metric_result = metric.calculate(raw_output)
        
        # Gerçek tarama süresini metric_result'a ekle (eğer 0 ise)
        if metric_result.scan_duration == 0.0:
            metric_result.scan_duration = actual_scan_duration
        
        # Issue'ları çıkar (advanced metrics için)
        detected_issues = extract_issues_from_deepsource_result(raw_output)
        
        # Ground truth verilerini yükle
        ground_truth = load_ground_truth(project_name)
        if ground_truth:
            print(f"Ground truth yüklendi: {len(ground_truth)} issue bulundu")
        else:
            print(f"Ground truth bulunamadı veya boş: {project_name}")
        
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
        
        # Gelişmiş metrikleri hesapla (hata olursa boş dict döndür)
        advanced_metrics_dict = {}
        advanced_file_path = None
        try:
            calculator = AdvancedMetricsCalculator()
            advanced_result = calculator.calculate_all_advanced_metrics(
                raw_data=raw_output,
                detected_issues=detected_issues,
                ground_truth=ground_truth,  # Ground truth verilerini kullan
                scan_duration=metric_result.scan_duration  # Gerçek süre kullanılıyor
            )
            
            # Advanced metrics sonucunu kaydet
            advanced_file_path = save_advanced_metrics_result(
                "deepsource",
                project_name,
                metric_result,
                advanced_result,
                ground_truth=ground_truth
            )
            
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
        except Exception as e:
            print(f"WARNING: Advanced metrics hesaplanamadı: {e}")
            import traceback
            traceback.print_exc()
            # Boş dict döndür, temel metrikler başarılı olsa bile
            advanced_metrics_dict = {}
        
        return {
            "success": True,
            "project": project_name,
            "available": True,
            "file_path": saved_path,
            "advanced_metrics_file_path": advanced_file_path,
            "metric_result": metric_dict,
            "advanced_metrics": advanced_metrics_dict,
            "scan_mode": scan_mode
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

