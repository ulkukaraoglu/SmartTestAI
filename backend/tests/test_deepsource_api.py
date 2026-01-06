#!/usr/bin/env python3
"""
DeepSource API Test Script

Bu script, DeepSource GraphQL API'sini test eder ve
repository issues'larını alır.

Kullanım:
    cd backend/tests
    python test_deepsource_api.py
    
    veya backend/ klasöründen:
    python -m tests.test_deepsource_api
"""

import requests
import json

# DeepSource API yapılandırması
TOKEN = "dsp_144b578a44fdc5553b0fe6ff5a52b00c8752"
API_URL = "https://api.deepsource.io/graphql/"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Test 0: Introspection - Repository type'ını öğren
print("=== Test 0: Introspection ===")
query0 = {
    "query": """
    query {
        __type(name: "Query") {
            fields {
                name
                args {
                    name
                    type {
                        name
                        kind
                    }
                }
            }
        }
    }
    """
}
r0 = requests.post(API_URL, headers=headers, json=query0)
print(f"Status: {r0.status_code}")
if r0.status_code == 200:
    print(f"Response: {json.dumps(r0.json(), indent=2)[:1000]}...")
print()

# Test 1: Repository bilgilerini al (doğru format)
print("=== Test 1: Repository Info ===")
query1 = {
    "query": """
    query {
        repository(login: "elif1624", name: "kalite", vcsProvider: GITHUB) {
            name
            defaultBranch
            isActivated
        }
    }
    """
}
r1 = requests.post(API_URL, headers=headers, json=query1)
print(f"Status: {r1.status_code}")
print(f"Response: {json.dumps(r1.json(), indent=2)}")
print()

# Test 2a: Issue type'ını öğren
print("=== Test 2a: Issue Type Introspection ===")
query2a = {
    "query": """
    query {
        __type(name: "RepositoryIssue") {
            fields {
                name
                type {
                    name
                    kind
                }
            }
        }
    }
    """
}
r2a = requests.post(API_URL, headers=headers, json=query2a)
print(f"Status: {r2a.status_code}")
if r2a.status_code == 200:
    print(f"Response: {json.dumps(r2a.json(), indent=2)}")
print()

# Test 2b: Issues listesi
print("=== Test 2b: Issues List ===")
query2b = {
    "query": """
    query {
        repository(login: "elif1624", name: "kalite", vcsProvider: GITHUB) {
            issues(first: 10) {
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
    """
}
r2b = requests.post(API_URL, headers=headers, json=query2b)
print(f"Status: {r2b.status_code}")
print(f"Response: {json.dumps(r2b.json(), indent=2)}")
print()

# Test 3: Repository'yi bul ve issues'ları al
print("=== Test 3: Repository Issues ===")
query3 = {
    "query": """
    query {
        repository(login: "elif1624", name: "kalite", vcsProvider: GITHUB) {
            name
            issues {
                totalCount
            }
        }
    }
    """
}
r3 = requests.post(API_URL, headers=headers, json=query3)
print(f"Status: {r3.status_code}")
print(f"Response: {json.dumps(r3.json(), indent=2)}")

