"""
GitHub Runner Modülü (Yol B yardımcı modülü)

Bu modül, yüklenen dosyaların DeepSource tarafından gerçekten taranabilmesi için
bağlı GitHub reposuna GEÇİCİ olarak commit'lenmesini ve analiz sonrasında
silinmesini sağlar (repo boyutu artmasın diye).

Neden gerekli?
- DeepSource yalnızca bağlı repodaki kodu analiz eder. Web arayüzünden yüklenen
  dosyalar repoda olmadığı için doğrudan taranamaz.
- Çözüm: dosyaları repoda `uploads_tmp/<id>/` altına koyup analizi bekleyip,
  sonuçları aldıktan sonra aynı dosyaları tekrar silmek.

GitHub Git Data API (blobs/trees/commits/refs) kullanılır; böylece birden fazla
dosya tek bir commit'te işlenebilir ve temizlik tek commit ile yapılabilir.

Environment Variables:
    GITHUB_TOKEN:          contents:write izinli GitHub Personal Access Token (gerekli)
    GITHUB_REPO_OWNER:     Repo sahibi (yoksa DEEPSOURCE_REPO_OWNER'a düşer)
    GITHUB_REPO_NAME:      Repo adı (yoksa DEEPSOURCE_REPO_NAME'e düşer)
    GITHUB_DEFAULT_BRANCH: Hedef branch (default: main)
    GITHUB_API_URL:        API kök adresi (default: https://api.github.com)
"""

import base64
import os

import requests

# ============================================
# YAPILANDIRMA
# ============================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")

# Repo bilgisi: GITHUB_* yoksa DeepSource repo değişkenlerine düş (aynı repo)
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER") or os.getenv("DEEPSOURCE_REPO_OWNER", "")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME") or os.getenv("DEEPSOURCE_REPO_NAME", "SmartTestAI")
GITHUB_DEFAULT_BRANCH = os.getenv("GITHUB_DEFAULT_BRANCH", "main")

# Yüklenen dosyaların repoda geçici olarak konacağı kök klasör
TMP_ROOT = "uploads_tmp"

# Tek bir geçici commit için güvenlik sınırları
MAX_FILES = 50
MAX_FILE_BYTES = 1_000_000  # dosya başına ~1 MB
MAX_TOTAL_BYTES = 5_000_000  # toplam ~5 MB


class GitHubError(RuntimeError):
    """GitHub API ile ilgili hatalar için özel istisna."""


def is_configured() -> bool:
    """Geçici commit akışının çalışabilmesi için token ve repo bilgisi var mı?"""
    return bool(GITHUB_TOKEN and GITHUB_REPO_OWNER and GITHUB_REPO_NAME)


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _repo_url(suffix: str) -> str:
    return f"{GITHUB_API_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}{suffix}"


def _request(method: str, url: str, **kwargs) -> dict:
    """GitHub API isteği yapar; hata durumunda GitHubError fırlatır."""
    resp = requests.request(method, url, headers=_headers(), timeout=60, **kwargs)
    if resp.status_code >= 300:
        raise GitHubError(f"GitHub API {method} {url} -> {resp.status_code}: {resp.text}")
    if resp.text:
        return resp.json()
    return {}


def _get_branch_head(branch: str) -> tuple:
    """Branch'in son commit sha'sı ve tree sha'sını döndürür: (commit_sha, tree_sha)."""
    ref = _request("GET", _repo_url(f"/git/ref/heads/{branch}"))
    commit_sha = ref["object"]["sha"]
    commit = _request("GET", _repo_url(f"/git/commits/{commit_sha}"))
    tree_sha = commit["tree"]["sha"]
    return commit_sha, tree_sha


def _collect_files(local_dir: str) -> list:
    """
    Yerel klasördeki dosyaları (alt klasörler dahil) okur ve
    (göreli_yol, bytes) listesi döndürür. Boyut/sayı sınırlarını uygular.
    """
    from pathlib import Path

    base = Path(local_dir)
    files = []
    total = 0
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(base).as_posix()
        data = path.read_bytes()
        if len(data) > MAX_FILE_BYTES:
            raise GitHubError(f"File too large for temp scan: {rel} ({len(data)} bytes)")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise GitHubError("Uploaded files exceed total size limit for temp scan")
        files.append((rel, data))
        if len(files) > MAX_FILES:
            raise GitHubError(f"Too many files for temp scan (max {MAX_FILES})")
    if not files:
        raise GitHubError("No files to push for temp scan")
    return files


def push_temp_files(local_dir: str, repo_subdir: str, branch: str = None) -> dict:
    """
    Yerel klasördeki dosyaları repoda `uploads_tmp/<repo_subdir>/` altına tek
    commit ile ekler.

    Args:
        local_dir: Yüklenen dosyaların bulunduğu yerel klasör
        repo_subdir: uploads_tmp altındaki benzersiz alt klasör adı (ör. hash)
        branch: Hedef branch (default: GITHUB_DEFAULT_BRANCH)

    Returns:
        dict: {"commit_sha": str, "repo_path": str, "paths": [repo içi tam yollar]}
    """
    if not is_configured():
        raise GitHubError("GitHub is not configured (GITHUB_TOKEN/owner/name missing)")

    branch = branch or GITHUB_DEFAULT_BRANCH
    repo_path = f"{TMP_ROOT}/{repo_subdir}".strip("/")

    files = _collect_files(local_dir)

    base_commit_sha, base_tree_sha = _get_branch_head(branch)

    # Her dosya için blob oluştur ve tree girdisi hazırla
    tree_entries = []
    pushed_paths = []
    for rel, data in files:
        blob = _request(
            "POST",
            _repo_url("/git/blobs"),
            json={"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"},
        )
        full_path = f"{repo_path}/{rel}"
        tree_entries.append({"path": full_path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        pushed_paths.append(full_path)

    new_tree = _request(
        "POST",
        _repo_url("/git/trees"),
        json={"base_tree": base_tree_sha, "tree": tree_entries},
    )

    new_commit = _request(
        "POST",
        _repo_url("/git/commits"),
        json={
            # NOT: "[skip ci]" KULLANMA — DeepSource bu etiketli commit'leri
            # analiz etmez. Bu commit'in analiz edilmesini İSTİYORUZ.
            "message": f"chore(temp): add temp scan files {repo_subdir}",
            "tree": new_tree["sha"],
            "parents": [base_commit_sha],
        },
    )

    _request(
        "PATCH",
        _repo_url(f"/git/refs/heads/{branch}"),
        json={"sha": new_commit["sha"], "force": False},
    )

    return {"commit_sha": new_commit["sha"], "repo_path": repo_path, "paths": pushed_paths}


def delete_temp_path(paths: list, repo_subdir: str, branch: str = None) -> str:
    """
    push_temp_files ile eklenen dosyaları tek commit ile siler (repo şişmesin).

    Args:
        paths: Silinecek repo içi tam dosya yolları (push sonucu dönen 'paths')
        repo_subdir: Commit mesajı için kullanılan alt klasör adı
        branch: Hedef branch

    Returns:
        str: Temizlik commit sha'sı
    """
    if not is_configured():
        raise GitHubError("GitHub is not configured")
    if not paths:
        return ""

    branch = branch or GITHUB_DEFAULT_BRANCH
    base_commit_sha, base_tree_sha = _get_branch_head(branch)

    # sha: None -> Git Data API'de o yoldaki dosyayı siler
    tree_entries = [
        {"path": p, "mode": "100644", "type": "blob", "sha": None} for p in paths
    ]

    new_tree = _request(
        "POST",
        _repo_url("/git/trees"),
        json={"base_tree": base_tree_sha, "tree": tree_entries},
    )

    new_commit = _request(
        "POST",
        _repo_url("/git/commits"),
        json={
            "message": f"chore(temp): remove temp scan files {repo_subdir} [skip ci]",
            "tree": new_tree["sha"],
            "parents": [base_commit_sha],
        },
    )

    _request(
        "PATCH",
        _repo_url(f"/git/refs/heads/{branch}"),
        json={"sha": new_commit["sha"], "force": False},
    )

    return new_commit["sha"]
