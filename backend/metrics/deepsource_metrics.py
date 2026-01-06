"""
DeepSource Metrics Normalization

Bu modül, DeepSource GraphQL API çıktısını standart MetricResult formatına normalize eder.

DeepSource GraphQL API Format:
{
    "data": {
        "repository": {
            "issues": {
                "edges": [
                    {
                        "node": {
                            "issue": {
                                "severity": "CRITICAL" | "MAJOR" | "MINOR" | "INFO",
                                ...
                            }
                        }
                    }
                ]
            }
        }
    }
}

Severity Mapping:
- CRITICAL -> critical
- MAJOR -> high
- MINOR -> medium
- INFO -> low
"""

from .base_metric import BaseMetric
from .result_model import MetricResult

class DeepSourceMetrics(BaseMetric):
    """
    DeepSource çıktılarını standart metrik formatına normalize eder
    
    DeepSource GraphQL API'den gelen repository issues'larını alır ve
    standart MetricResult formatına dönüştürür.
    """
    
    def calculate(self, raw_data: dict) -> MetricResult:
        """
        DeepSource GraphQL API çıktısını standart MetricResult formatına çevirir
        
        DeepSource GraphQL API formatı:
        {
            "data": {
                "repository": {
                    "issues": {
                        "totalCount": 7,
                        "edges": [
                            {
                                "node": {
                                    "issue": {
                                        "shortcode": "PYL-R0201",
                                        "title": "...",
                                        "severity": "MAJOR" | "MINOR" | "CRITICAL" | "INFO",
                                        "category": "PERFORMANCE" | "SECURITY" | "ANTI_PATTERN" | ...
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        Args:
            raw_data: DeepSource GraphQL API'den gelen ham JSON çıktısı
        
        Returns:
            MetricResult: Normalize edilmiş metrik sonucu
        """
        # ============================================
        # GraphQL RESPONSE'DAN ISSUES'LARI ÇIKAR
        # ============================================
        issues = []
        if "data" in raw_data and "repository" in raw_data["data"]:
            repo_data = raw_data["data"]["repository"]
            if "issues" in repo_data and "edges" in repo_data["issues"]:
                # GraphQL edges yapısından issue'ları çıkar
                for edge in repo_data["issues"]["edges"]:
                    if "node" in edge and "issue" in edge["node"]:
                        issues.append(edge["node"]["issue"])
        
        # ============================================
        # SEVERITY MAPPING
        # ============================================
        # DeepSource severity formatı: "CRITICAL", "MAJOR", "MINOR", "INFO"
        # Standart formata çevir: critical, high, medium, low
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for issue in issues:
            # DeepSource severity formatı: "CRITICAL", "MAJOR", "MINOR", "INFO"
            severity = issue.get("severity", "").upper()
            
            # DeepSource severity -> Standart format mapping
            if severity == "CRITICAL":
                counts["critical"] += 1
            elif severity == "MAJOR":
                counts["high"] += 1
            elif severity == "MINOR":
                counts["medium"] += 1
            elif severity == "INFO":
                counts["low"] += 1
            else:
                # Bilinmeyen severity'leri medium olarak say (varsayılan)
                counts["medium"] += 1
        
        # ============================================
        # SCAN DURATION
        # ============================================
        # DeepSource GraphQL API'sinde scan duration bilgisi yok
        # 0.0 olarak bırakıyoruz
        scan_duration = 0.0
        
        # ============================================
        # NORMALIZE EDİLMİŞ SONUCU DÖNDÜR
        # ============================================
        return MetricResult(
            tool_name="DeepSource",
            critical=counts["critical"],
            high=counts["high"],
            medium=counts["medium"],
            low=counts["low"],
            total_issues=len(issues),
            scan_duration=scan_duration
        )

