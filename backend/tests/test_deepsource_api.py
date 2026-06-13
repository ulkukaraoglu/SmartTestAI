#!/usr/bin/env python3
"""
DeepSource API Test Script

Bu script, DeepSource GraphQL API'sine bağlanıp repository bilgisini ve
issue listesini çeker. Hızlı bir bağlantı/doğrulama (smoke test) aracıdır.

Güvenlik: API token ve repo bilgileri ASLA koda gömülmez; environment
variable'lardan okunur (deepsource_runner.py ile aynı değişkenler).

Kullanım:
    # Önce gerekli değişkenleri ayarla (PowerShell örneği):
    #   $env:DEEPSOURCE_API_TOKEN="<token>"
    #   $env:DEEPSOURCE_REPO_OWNER="<owner>"
    #   $env:DEEPSOURCE_REPO_NAME="SmartTestAI"
    #   $env:DEEPSOURCE_VCS_PROVIDER="GITHUB"

    cd backend/tests
    python test_deepsource_api.py

    veya backend/ klasöründen:
    python -m tests.test_deepsource_api
"""

import json
import os
import sys

import requests

# ============================================
# YAPILANDIRMA (environment variable'lardan)
# ============================================
TOKEN = os.getenv("DEEPSOURCE_API_TOKEN", "")
API_URL = os.getenv("DEEPSOURCE_API_URL", "https://api.deepsource.com/graphql/")
REPO_OWNER = os.getenv("DEEPSOURCE_REPO_OWNER", "")
REPO_NAME = os.getenv("DEEPSOURCE_REPO_NAME", "SmartTestAI")
VCS_PROVIDER = os.getenv("DEEPSOURCE_VCS_PROVIDER", "GITHUB")

if not TOKEN:
    print("HATA: DEEPSOURCE_API_TOKEN ayarli degil. Once token'i environment'a ekleyin.")
    sys.exit(1)
if not REPO_OWNER:
    print("HATA: DEEPSOURCE_REPO_OWNER ayarli degil. Repo sahibini environment'a ekleyin.")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

print(f"Endpoint : {API_URL}")
print(f"Repo     : {REPO_OWNER}/{REPO_NAME} ({VCS_PROVIDER})")
print(f"Token    : {TOKEN[:8]}... (gizlendi)")
print()


def run_query(query: str) -> dict:
    """GraphQL sorgusu gönderir ve JSON yanıtını döndürür."""
    resp = requests.post(API_URL, headers=headers, json={"query": query}, timeout=60)
    print(f"Status: {resp.status_code}")
    try:
        return resp.json()
    except ValueError:
        print(f"Gecersiz yanit: {resp.text[:500]}")
        return {}


# ============================================
# Test 1: Repository bilgisi
# ============================================
print("=== Test 1: Repository Info ===")
data1 = run_query(
    """
    query {
        repository(login: "%s", name: "%s", vcsProvider: %s) {
            name
            defaultBranch
            isActivated
            latestCommitOid
        }
    }
    """ % (REPO_OWNER, REPO_NAME, VCS_PROVIDER)
)
print(json.dumps(data1, indent=2, ensure_ascii=False))
print()

# ============================================
# Test 2: Issue listesi (ilk 10)
# ============================================
print("=== Test 2: Issues List ===")
data2 = run_query(
    """
    query {
        repository(login: "%s", name: "%s", vcsProvider: %s) {
            issues(first: 10) {
                totalCount
                edges {
                    node {
                        issue { shortcode title severity category }
                    }
                }
            }
        }
    }
    """ % (REPO_OWNER, REPO_NAME, VCS_PROVIDER)
)
print(json.dumps(data2, indent=2, ensure_ascii=False))
print()

# ============================================
# Test 3: Son analiz çalışmaları (Yol B polling ile aynı sorgu)
# ============================================
print("=== Test 3: Analysis Runs ===")
data3 = run_query(
    """
    query {
        repository(login: "%s", name: "%s", vcsProvider: %s) {
            analysisRuns(first: 5) {
                edges {
                    node { commitOid status }
                }
            }
        }
    }
    """ % (REPO_OWNER, REPO_NAME, VCS_PROVIDER)
)
print(json.dumps(data3, indent=2, ensure_ascii=False))
