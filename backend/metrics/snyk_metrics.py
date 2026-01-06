"""
Snyk Code Metrics Normalization

Bu modül, Snyk Code'un çıktısını standart MetricResult formatına normalize eder.

Snyk Code iki farklı format kullanabilir:
1. SARIF format (yeni): runs[0].results[] yapısında
2. Eski format: vulnerabilities[] yapısında

Her iki format da desteklenir ve otomatik olarak algılanır.

Severity Mapping:
- Priority Score >= 900 -> critical
- Priority Score >= 700 -> high
- Priority Score >= 500 -> medium
- Priority Score < 500 -> low
- Level "error" -> high
- Level "warning" -> medium
- Diğer -> low
"""

from .base_metric import BaseMetric
from .result_model import MetricResult
import time

class SnykMetrics(BaseMetric):
    """
    Snyk Code çıktılarını standart metrik formatına normalize eder
    """
    
    def calculate(self, raw_data: dict) -> MetricResult:
        """
        Snyk Code'un ham çıktısını standart MetricResult formatına çevirir
        
        Snyk Code iki farklı format kullanabilir:
        1. SARIF format (yeni): runs[0].results[] yapısında
        2. Eski format: vulnerabilities[] yapısında
        
        Her iki format da otomatik olarak algılanır ve işlenir.
        
        Args:
            raw_data: Snyk Code'dan gelen ham JSON çıktısı
        
        Returns:
            MetricResult: Normalize edilmiş metrik sonucu
        """
        # ============================================
        # SARIF FORMAT DESTEĞİ (Yeni format)
        # ============================================
        # Snyk Code'un yeni SARIF formatı: runs[0].results[]
        if "runs" in raw_data and len(raw_data.get("runs", [])) > 0:
            # SARIF formatından results listesini al
            results = raw_data["runs"][0].get("results", [])
            
            # Severity sayacıları
            counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            
            # Her result için severity belirleme
            for result in results:
                level = result.get("level", "error").lower()
                priority_score = result.get("properties", {}).get("priorityScore", 0)
                
                # Priority score varsa, ona göre severity belirle
                # Snyk Code priority score: 0-1000 arası
                if priority_score > 0:
                    if priority_score >= 900:
                        counts["critical"] += 1
                    elif priority_score >= 700:
                        counts["high"] += 1
                    elif priority_score >= 500:
                        counts["medium"] += 1
                    else:
                        counts["low"] += 1
                else:
                    # Priority score yoksa, level'a göre belirle
                    if level == "error":
                        counts["high"] += 1
                    elif level == "warning":
                        counts["medium"] += 1
                    else:
                        counts["low"] += 1
            
            # Scan duration SARIF formatında genelde yok
            # automationDetails içinde olabilir ama genelde 0.0 olarak bırakıyoruz
            scan_duration = 0.0
            if "runs" in raw_data and len(raw_data["runs"]) > 0:
                automation_details = raw_data["runs"][0].get("automationDetails", {})
                # Duration bilgisi genelde automationDetails'te yok
            
            # Normalize edilmiş sonucu döndür
            return MetricResult(
                tool_name="Snyk Code",
                critical=counts["critical"],
                high=counts["high"],
                medium=counts["medium"],
                low=counts["low"],
                total_issues=len(results),
                scan_duration=scan_duration
            )
        
        # ============================================
        # ESKİ FORMAT DESTEĞİ (Geriye dönük uyumluluk)
        # ============================================
        # Snyk Code'un eski formatı: vulnerabilities[]
        vulns = raw_data.get("vulnerabilities", [])

        # Severity sayacıları
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        # Her vulnerability için severity say
        for v in vulns:
            sev = v.get("severity")
            if sev in counts:
                counts[sev] += 1

        # Normalize edilmiş sonucu döndür
        return MetricResult(
            tool_name="Snyk Code",
            critical=counts["critical"],
            high=counts["high"],
            medium=counts["medium"],
            low=counts["low"],
            total_issues=len(vulns),
            scan_duration=raw_data.get("scanDuration", 0.0)
        )
