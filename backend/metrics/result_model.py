"""
Metric Result Model

Bu modül, tüm AI kod analiz araçları için standart metrik sonuç formatını tanımlar.
Her araç, kendi çıktısını bu formata normalize eder, böylece araçlar arası
karşılaştırma yapılabilir.

Kullanım:
    result = MetricResult(
        tool_name="Snyk Code",
        critical=5,
        high=10,
        medium=20,
        low=5,
        total_issues=40,
        scan_duration=12.5
    )
"""

from dataclasses import dataclass

@dataclass
class MetricResult:
    """
    Standart metrik sonuç modeli
    
    Tüm AI kod analiz araçları, çıktılarını bu formata normalize eder.
    Bu sayede farklı araçların sonuçları karşılaştırılabilir.
    
    Attributes:
        tool_name: Araç adı (örn: "Snyk Code", "DeepSource")
        critical: Critical seviyesindeki issue sayısı
        high: High seviyesindeki issue sayısı
        medium: Medium seviyesindeki issue sayısı
        low: Low seviyesindeki issue sayısı
        total_issues: Toplam issue sayısı
        scan_duration: Tarama süresi (saniye)
    """
    tool_name: str
    critical: int
    high: int
    medium: int
    low: int
    total_issues: int
    scan_duration: float
