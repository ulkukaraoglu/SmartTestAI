"""
Advanced Metrics Calculator

Bu modül, AI kod analiz araçlarının performansını değerlendirmek için
gelişmiş metrikler hesaplar.

Hesaplanan Metrikler:
1. Defect Detection Accuracy (Hata Tespit Başarısı):
   - Precision: Doğru pozitif / (Doğru pozitif + Yanlış pozitif)
   - Recall: Doğru pozitif / (Doğru pozitif + Yanlış negatif)
   - F1 Score: Precision ve Recall'un harmonik ortalaması
   - False Positive Rate: Yanlış pozitif / (Yanlış pozitif + Doğru negatif)

2. Code Coverage (Kod Kapsama):
   - Taranan kod satırı yüzdesi
   - Analiz edilen dosya sayısı
   - Analiz edilen satır sayısı

3. Operational Efficiency (Operasyonel Verimlilik):
   - Ortalama tarama süresi
   - CPU kullanım yüzdesi
   - Bellek kullanımı (MB)

Kullanım:
    calculator = AdvancedMetricsCalculator()
    result = calculator.calculate_all_advanced_metrics(
        raw_data=raw_data,
        detected_issues=detected_issues,
        ground_truth=ground_truth,
        scan_duration=12.5
    )
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import time
import psutil
import os


@dataclass
class AdvancedMetricResult:
    """Gelişmiş metrik sonuçları"""
    # Hata Tespit Başarısı (Defect Detection Accuracy)
    precision: float  # Doğruluk: TP / (TP + FP)
    recall: float     # Geri çağırma: TP / (TP + FN)
    f1_score: float   # F1 skoru: 2 * (precision * recall) / (precision + recall)
    
    # Kod Kapsama Oranı (Code Coverage)
    code_coverage: float  # Taranan kod satırı yüzdesi
    files_analyzed: int   # Analiz edilen dosya sayısı
    lines_analyzed: int   # Analiz edilen satır sayısı
    
    # Yanlış Alarm Eğilimi (False Positive Rate)
    false_positive_rate: float  # FP / (FP + TN)
    false_positives: int        # Yanlış pozitif sayısı
    true_positives: int         # Doğru pozitif sayısı
    false_negatives: int       # Yanlış negatif sayısı
    true_negatives: int        # Doğru negatif sayısı
    
    # Operasyonel Verimlilik
    average_scan_time: float    # Ortalama tarama süresi (saniye)
    cpu_usage_percent: float    # CPU kullanım yüzdesi
    memory_usage_mb: float      # Bellek kullanımı (MB)
    
    # Kod Kalitesi ve Standart Uyumu (opsiyonel - manuel değerlendirme gerekebilir)
    code_quality_score: Optional[float] = None  # 0-100 arası kod kalitesi skoru


class AdvancedMetricsCalculator:
    """
    Gelişmiş metrik hesaplama sınıfı
    """
    
    def __init__(self):
        self.scan_times = []  # Tarama sürelerini saklamak için
        self.process = psutil.Process(os.getpid())
    
    def calculate_defect_detection_accuracy(
        self,
        detected_issues: List[Dict],
        ground_truth: List[Dict],
        issue_matching_func=None
    ) -> Dict[str, float]:
        """
        Hata Tespit Başarısı (Defect Detection Accuracy) hesaplar
        
        Args:
            detected_issues: Araç tarafından bulunan issue'lar
            ground_truth: Gerçekte var olan issue'lar (test verisi)
            issue_matching_func: Issue'ları eşleştirmek için fonksiyon (opsiyonel)
        
        Returns:
            {
                "precision": float,
                "recall": float,
                "f1_score": float,
                "true_positives": int,
                "false_positives": int,
                "false_negatives": int
            }
        """
        if issue_matching_func is None:
            # Varsayılan eşleştirme: Issue key'lerine göre
            issue_matching_func = self._default_issue_matcher
        
        # True Positives: Hem bulundu hem de gerçekte var
        # False Positives: Bulundu ama gerçekte yok
        # False Negatives: Bulunmadı ama gerçekte var
        
        true_positives = 0
        false_positives = 0
        matched_ground_truth = set()
        
        for detected in detected_issues:
            matched = False
            for i, truth in enumerate(ground_truth):
                if i not in matched_ground_truth and issue_matching_func(detected, truth):
                    true_positives += 1
                    matched_ground_truth.add(i)
                    matched = True
                    break
            
            if not matched:
                false_positives += 1
        
        false_negatives = len(ground_truth) - len(matched_ground_truth)
        true_negatives = 0  # Genellikle hesaplanmaz (çok büyük sayı)
        
        # Precision: TP / (TP + FP)
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        
        # Recall: TP / (TP + FN)
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        
        # F1 Score: 2 * (precision * recall) / (precision + recall)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # False Positive Rate: FP / (FP + TN)
        # TN genellikle çok büyük olduğu için, FP / total_detected kullanılabilir
        false_positive_rate = false_positives / len(detected_issues) if len(detected_issues) > 0 else 0.0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "true_negatives": true_negatives,
            "false_positive_rate": false_positive_rate
        }
    
    def _default_issue_matcher(self, detected: Dict, truth: Dict) -> bool:
        """
        Varsayılan issue eşleştirme fonksiyonu
        Issue'ları dosya yolu ve satır numarasına göre eşleştirir
        """
        detected_file = detected.get("file", detected.get("location", {}).get("file", ""))
        detected_line = detected.get("line", detected.get("location", {}).get("line", -1))
        
        truth_file = truth.get("file", truth.get("location", {}).get("file", ""))
        truth_line = truth.get("line", truth.get("location", {}).get("line", -1))
        
        # Dosya adı ve satır numarası eşleşiyorsa aynı issue kabul et
        if detected_file and truth_file:
            detected_file_name = detected_file.split("/")[-1] if "/" in detected_file else detected_file
            truth_file_name = truth_file.split("/")[-1] if "/" in truth_file else truth_file
            
            return detected_file_name == truth_file_name and detected_line == truth_line
        
        return False
    
    def calculate_code_coverage(
        self,
        raw_data: Dict,
        detected_issues: List[Dict] = None,
        total_lines: Optional[int] = None,
        total_files: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Kod Kapsama Oranı (Code Coverage) hesaplar
        
        Args:
            raw_data: Araçtan gelen ham veri
            detected_issues: Bulunan issue'lar (dosya bilgisi çıkarmak için)
            total_lines: Toplam kod satırı sayısı (opsiyonel)
            total_files: Toplam dosya sayısı (opsiyonel)
        
        Returns:
            {
                "code_coverage": float,  # 0-100 arası yüzde
                "files_analyzed": int,
                "lines_analyzed": int
            }
        """
        files_analyzed = set()
        lines_analyzed = 0
        
        # Snyk SARIF formatından dosya bilgilerini çıkar
        if "runs" in raw_data and len(raw_data.get("runs", [])) > 0:
            run = raw_data["runs"][0]
            
            # Artifacts (dosyalar) bilgisini al
            artifacts = run.get("artifacts", [])
            if artifacts:
                for artifact in artifacts:
                    location = artifact.get("location", {})
                    uri = location.get("uri", "")
                    if uri:
                        files_analyzed.add(uri)
            
            # Results (issue'lar) içinden dosya bilgilerini çıkar
            results = run.get("results", [])
            for result in results:
                locations = result.get("locations", [])
                for location in locations:
                    physical_location = location.get("physicalLocation", {})
                    artifact_location = physical_location.get("artifactLocation", {})
                    uri = artifact_location.get("uri", "")
                    if uri:
                        files_analyzed.add(uri)
                    
                    # Satır bilgisi
                    region = physical_location.get("region", {})
                    start_line = region.get("startLine", 0)
                    if start_line > 0:
                        lines_analyzed = max(lines_analyzed, start_line)
        
        # DeepSource GraphQL formatından
        elif "data" in raw_data and "repository" in raw_data["data"]:
            repo_data = raw_data["data"]["repository"]
            issues = repo_data.get("issues", {})
            edges = issues.get("edges", [])
            
            # Issue'lardan dosya bilgisi çıkar (eğer varsa)
            for edge in edges:
                node = edge.get("node", {})
                issue = node.get("issue", {})
                # DeepSource API'sinde dosya bilgisi genelde yok
                pass
        
        # detected_issues listesinden dosya bilgilerini çıkar
        if detected_issues:
            for issue in detected_issues:
                file_path = issue.get("file", "")
                if file_path:
                    files_analyzed.add(file_path)
                
                line = issue.get("line", 0)
                if line > 0:
                    lines_analyzed = max(lines_analyzed, line)
        
        files_count = len(files_analyzed)
        
        # Code coverage hesapla
        if total_files and total_files > 0:
            code_coverage = (files_count / total_files) * 100
        elif files_count > 0:
            # Total files bilgisi yoksa, en azından analiz edilen dosyaları göster
            code_coverage = 100.0  # Analiz edilen dosyalar için %100
        else:
            code_coverage = 0.0
        
        return {
            "code_coverage": code_coverage,
            "files_analyzed": files_count,
            "lines_analyzed": lines_analyzed
        }
    
    def calculate_operational_efficiency(self, scan_duration: float = 0.0) -> Dict[str, float]:
        """
        Operasyonel Verimlilik metriklerini hesaplar
        
        Args:
            scan_duration: Mevcut tarama süresi (eğer scan_times boşsa kullanılır)
        
        Returns:
            {
                "average_scan_time": float,
                "cpu_usage_percent": float,
                "memory_usage_mb": float
            }
        """
        # Ortalama tarama süresi
        if self.scan_times:
            average_scan_time = sum(self.scan_times) / len(self.scan_times)
        else:
            # İlk taramada scan_times boşsa, mevcut scan_duration'ı kullan
            average_scan_time = scan_duration if scan_duration > 0 else 0.0
        
        # CPU ve Memory kullanımı
        try:
            cpu_usage = self.process.cpu_percent(interval=0.1)
        except:
            cpu_usage = 0.0
        
        try:
            memory_info = self.process.memory_info()
            memory_usage_mb = memory_info.rss / (1024 * 1024)  # Bytes to MB
        except:
            memory_usage_mb = 0.0
        
        return {
            "average_scan_time": average_scan_time,
            "cpu_usage_percent": cpu_usage,
            "memory_usage_mb": memory_usage_mb
        }
    
    def record_scan_time(self, scan_duration: float):
        """Tarama süresini kaydeder"""
        self.scan_times.append(scan_duration)
    
    def calculate_all_advanced_metrics(
        self,
        raw_data: Dict,
        detected_issues: List[Dict],
        ground_truth: Optional[List[Dict]] = None,
        scan_duration: float = 0.0,
        total_lines: Optional[int] = None,
        total_files: Optional[int] = None
    ) -> AdvancedMetricResult:
        """
        Tüm gelişmiş metrikleri hesaplar
        
        Args:
            raw_data: Araçtan gelen ham veri
            detected_issues: Bulunan issue'lar
            ground_truth: Gerçek issue'lar (opsiyonel, precision/recall için gerekli)
            scan_duration: Tarama süresi
            total_lines: Toplam kod satırı sayısı
            total_files: Toplam dosya sayısı
        
        Returns:
            AdvancedMetricResult
        """
        # Tarama süresini kaydet
        if scan_duration > 0:
            self.record_scan_time(scan_duration)
        
        # Hata Tespit Başarısı
        if ground_truth:
            accuracy_metrics = self.calculate_defect_detection_accuracy(
                detected_issues, ground_truth
            )
        else:
            # Ground truth yoksa varsayılan değerler
            accuracy_metrics = {
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "true_positives": 0,
                "false_positives": len(detected_issues) if detected_issues else 0,
                "false_negatives": 0,
                "true_negatives": 0,
                "false_positive_rate": 1.0 if detected_issues else 0.0
            }
        
        # Kod Kapsama (detected_issues parametresini de geçir)
        coverage_metrics = self.calculate_code_coverage(
            raw_data, detected_issues=detected_issues, total_lines=total_lines, total_files=total_files
        )
        
        # Operasyonel Verimlilik (scan_duration parametresini geçir)
        efficiency_metrics = self.calculate_operational_efficiency(scan_duration=scan_duration)
        
        return AdvancedMetricResult(
            precision=accuracy_metrics["precision"],
            recall=accuracy_metrics["recall"],
            f1_score=accuracy_metrics["f1_score"],
            code_coverage=coverage_metrics["code_coverage"],
            files_analyzed=coverage_metrics["files_analyzed"],
            lines_analyzed=coverage_metrics["lines_analyzed"],
            false_positive_rate=accuracy_metrics["false_positive_rate"],
            false_positives=accuracy_metrics["false_positives"],
            true_positives=accuracy_metrics["true_positives"],
            false_negatives=accuracy_metrics["false_negatives"],
            true_negatives=0,  # Genellikle hesaplanmaz
            average_scan_time=efficiency_metrics["average_scan_time"],
            cpu_usage_percent=efficiency_metrics["cpu_usage_percent"],
            memory_usage_mb=efficiency_metrics["memory_usage_mb"],
            code_quality_score=None  # Manuel değerlendirme gerekebilir
        )

