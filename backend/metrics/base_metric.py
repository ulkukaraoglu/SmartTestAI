"""
Base Metric Abstract Class

Bu modül, tüm AI kod analiz araçları için ortak bir interface sağlar.
Her araç, kendi çıktı formatını standart MetricResult formatına
dönüştürmek için BaseMetric'ten türetilmelidir.

Kullanım:
    class MyToolMetrics(BaseMetric):
        def calculate(self, raw_data: dict) -> MetricResult:
            # Araç özel normalizasyon mantığı
            return MetricResult(...)
"""

from abc import ABC, abstractmethod
from .result_model import MetricResult

class BaseMetric(ABC):
    """
    Tüm metrik hesaplama sınıfları için abstract base class
    
    Her AI kod analiz aracı, kendi çıktı formatını standart MetricResult
    formatına dönüştürmek için bu sınıftan türetilmelidir.
    """
    
    @abstractmethod
    def calculate(self, raw_data: dict) -> MetricResult:
        """
        AI test aracının ham çıktısını standart metrik formatına çevirir
        
        Bu metod, her araç için implement edilmelidir. Araç özel formatını
        (SARIF, GraphQL, JSON, vb.) standart MetricResult formatına dönüştürür.
        
        Args:
            raw_data: Araçtan gelen ham JSON çıktısı
        
        Returns:
            MetricResult: Standart metrik sonucu (critical, high, medium, low, total_issues)
        
        Raises:
            NotImplementedError: Alt sınıf bu metodu implement etmediyse
        """
        pass
    
    def calculate_advanced_metrics(
        self, 
        raw_data: dict, 
        detected_issues: list, 
        ground_truth: list = None, 
        scan_duration: float = 0.0
    ) -> dict:
        """
        Gelişmiş metrikleri hesaplar (opsiyonel)
        
        Precision, Recall, F1 Score, Code Coverage, False Positive Rate gibi
        gelişmiş metrikleri hesaplar. Ground truth gerekli metrikler için
        opsiyonel parametre olarak alınır.
        
        Args:
            raw_data: Araçtan gelen ham veri
            detected_issues: Bulunan issue'lar listesi
            ground_truth: Gerçek issue'lar listesi (precision/recall için gerekli)
            scan_duration: Tarama süresi (saniye)
        
        Returns:
            dict: Gelişmiş metrik sonuçları (AdvancedMetricResult formatında)
        
        Note:
            Varsayılan implementasyon AdvancedMetricsCalculator kullanır.
            Alt sınıflar bu metodu override edebilir.
        """
        # Varsayılan implementasyon - alt sınıflar override edebilir
        from .advanced_metrics import AdvancedMetricsCalculator
        
        calculator = AdvancedMetricsCalculator()
        return calculator.calculate_all_advanced_metrics(
            raw_data=raw_data,
            detected_issues=detected_issues,
            ground_truth=ground_truth,
            scan_duration=scan_duration
        )
