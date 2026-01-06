"""
Detaylı Analiz Raporu Oluşturucu

Benchmark sonuçlarını analiz edip detaylı bir rapor oluşturur.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def load_latest_benchmark_report() -> Dict:
    """En son benchmark raporunu yükler"""
    results_dir = Path("../results")
    benchmark_files = sorted(results_dir.glob("benchmark_report_*.json"), reverse=True)
    
    if not benchmark_files:
        raise FileNotFoundError("Benchmark raporu bulunamadı!")
    
    with open(benchmark_files[0], 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_analysis_report():
    """Detaylı analiz raporu oluşturur"""
    print("=" * 80)
    print("DETAYLI KARŞILAŞTIRMALI ANALİZ RAPORU")
    print("=" * 80)
    print()
    
    # Benchmark raporunu yükle
    benchmark_data = load_latest_benchmark_report()
    
    # Genel istatistikler
    projects = benchmark_data["projects"]
    total_projects = len(projects)
    
    snyk_success = sum(1 for p in projects.values() if p.get("snyk", {}).get("success"))
    deepsource_success = sum(1 for p in projects.values() if p.get("deepsource", {}).get("success"))
    
    print(f"[GENEL İSTATİSTİKLER]")
    print(f"Toplam Test Projesi: {total_projects}")
    print(f"Snyk Code Başarı Oranı: {snyk_success}/{total_projects} ({snyk_success/total_projects*100:.1f}%)")
    print(f"DeepSource Başarı Oranı: {deepsource_success}/{total_projects} ({deepsource_success/total_projects*100:.1f}%)")
    print()
    
    # Performans metrikleri
    snyk_times = []
    deepsource_times = []
    
    for project_data in projects.values():
        if project_data.get("snyk", {}).get("success"):
            snyk_times.append(project_data["snyk"]["scan_duration"])
        if project_data.get("deepsource", {}).get("success"):
            deepsource_times.append(project_data["deepsource"]["scan_duration"])
    
    print(f"[PERFORMANS METRİKLERİ]")
    if snyk_times:
        print(f"Snyk Code:")
        print(f"  - Ortalama Tarama Süresi: {sum(snyk_times)/len(snyk_times):.2f}s")
        print(f"  - En Hızlı: {min(snyk_times):.2f}s")
        print(f"  - En Yavaş: {max(snyk_times):.2f}s")
    if deepsource_times:
        print(f"DeepSource:")
        print(f"  - Ortalama Tarama Süresi: {sum(deepsource_times)/len(deepsource_times):.2f}s")
        print(f"  - En Hızlı: {min(deepsource_times):.2f}s")
        print(f"  - En Yavaş: {max(deepsource_times):.2f}s")
    
    if snyk_times and deepsource_times:
        speed_ratio = sum(snyk_times)/len(snyk_times) / sum(deepsource_times)/len(deepsource_times)
        print(f"\n  DeepSource, Snyk Code'dan {speed_ratio:.1f}x daha hızlı")
    print()
    
    # Doğruluk metrikleri (ground truth olan projeler için)
    projects_with_gt = {k: v for k, v in projects.items() if v.get("ground_truth_count", 0) > 0}
    
    if projects_with_gt:
        print(f"[DOĞRULUK METRİKLERİ]")
        print(f"Ground Truth Olan Projeler: {len(projects_with_gt)}")
        print()
        
        snyk_precisions = []
        snyk_recalls = []
        snyk_f1_scores = []
        snyk_tps = []
        snyk_fps = []
        snyk_fns = []
        
        deepsource_precisions = []
        deepsource_recalls = []
        deepsource_f1_scores = []
        deepsource_tps = []
        deepsource_fps = []
        deepsource_fns = []
        
        for project_name, project_data in projects_with_gt.items():
            print(f"Proje: {project_name}")
            print(f"  Ground Truth: {project_data['ground_truth_count']} issue")
            
            # Snyk metrikleri
            snyk_metrics = project_data.get("snyk", {}).get("comparison_metrics")
            if snyk_metrics:
                snyk_precisions.append(snyk_metrics["precision"])
                snyk_recalls.append(snyk_metrics["recall"])
                snyk_f1_scores.append(snyk_metrics["f1_score"])
                snyk_tps.append(snyk_metrics["true_positives"])
                snyk_fps.append(snyk_metrics["false_positives"])
                snyk_fns.append(snyk_metrics["false_negatives"])
                
                print(f"  Snyk Code:")
                print(f"    - Precision: {snyk_metrics['precision']:.2%}")
                print(f"    - Recall: {snyk_metrics['recall']:.2%}")
                print(f"    - F1 Score: {snyk_metrics['f1_score']:.2%}")
                print(f"    - TP: {snyk_metrics['true_positives']}, FP: {snyk_metrics['false_positives']}, FN: {snyk_metrics['false_negatives']}")
            
            # DeepSource metrikleri
            deepsource_metrics = project_data.get("deepsource", {}).get("comparison_metrics")
            if deepsource_metrics:
                deepsource_precisions.append(deepsource_metrics["precision"])
                deepsource_recalls.append(deepsource_metrics["recall"])
                deepsource_f1_scores.append(deepsource_metrics["f1_score"])
                deepsource_tps.append(deepsource_metrics["true_positives"])
                deepsource_fps.append(deepsource_metrics["false_positives"])
                deepsource_fns.append(deepsource_metrics["false_negatives"])
                
                print(f"  DeepSource:")
                print(f"    - Precision: {deepsource_metrics['precision']:.2%}")
                print(f"    - Recall: {deepsource_metrics['recall']:.2%}")
                print(f"    - F1 Score: {deepsource_metrics['f1_score']:.2%}")
                print(f"    - TP: {deepsource_metrics['true_positives']}, FP: {deepsource_metrics['false_positives']}, FN: {deepsource_metrics['false_negatives']}")
            print()
        
        # Genel özet
        print(f"[GENEL ÖZET - DOĞRULUK METRİKLERİ]")
        if snyk_precisions:
            print(f"Snyk Code:")
            print(f"  - Ortalama Precision: {sum(snyk_precisions)/len(snyk_precisions):.2%}")
            print(f"  - Ortalama Recall: {sum(snyk_recalls)/len(snyk_recalls):.2%}")
            print(f"  - Ortalama F1 Score: {sum(snyk_f1_scores)/len(snyk_f1_scores):.2%}")
            print(f"  - Toplam TP: {sum(snyk_tps)}, FP: {sum(snyk_fps)}, FN: {sum(snyk_fns)}")
        
        if deepsource_precisions:
            print(f"DeepSource:")
            print(f"  - Ortalama Precision: {sum(deepsource_precisions)/len(deepsource_precisions):.2%}")
            print(f"  - Ortalama Recall: {sum(deepsource_recalls)/len(deepsource_recalls):.2%}")
            print(f"  - Ortalama F1 Score: {sum(deepsource_f1_scores)/len(deepsource_f1_scores):.2%}")
            print(f"  - Toplam TP: {sum(deepsource_tps)}, FP: {sum(deepsource_fps)}, FN: {sum(deepsource_fns)}")
        
        # Karşılaştırma
        if snyk_precisions and deepsource_precisions:
            print()
            print(f"[KARŞILAŞTIRMA]")
            if sum(snyk_precisions)/len(snyk_precisions) > sum(deepsource_precisions)/len(deepsource_precisions):
                print(f"  Precision: Snyk Code daha iyi ({sum(snyk_precisions)/len(snyk_precisions):.2%} vs {sum(deepsource_precisions)/len(deepsource_precisions):.2%})")
            else:
                print(f"  Precision: DeepSource daha iyi ({sum(deepsource_precisions)/len(deepsource_precisions):.2%} vs {sum(snyk_precisions)/len(snyk_precisions):.2%})")
            
            if sum(snyk_recalls)/len(snyk_recalls) > sum(deepsource_recalls)/len(deepsource_recalls):
                print(f"  Recall: Snyk Code daha iyi ({sum(snyk_recalls)/len(snyk_recalls):.2%} vs {sum(deepsource_recalls)/len(deepsource_recalls):.2%})")
            else:
                print(f"  Recall: DeepSource daha iyi ({sum(deepsource_recalls)/len(deepsource_recalls):.2%} vs {sum(snyk_recalls)/len(snyk_recalls):.2%})")
            
            if sum(snyk_f1_scores)/len(snyk_f1_scores) > sum(deepsource_f1_scores)/len(deepsource_f1_scores):
                print(f"  F1 Score: Snyk Code daha iyi ({sum(snyk_f1_scores)/len(snyk_f1_scores):.2%} vs {sum(deepsource_f1_scores)/len(deepsource_f1_scores):.2%})")
            else:
                print(f"  F1 Score: DeepSource daha iyi ({sum(deepsource_f1_scores)/len(deepsource_f1_scores):.2%} vs {sum(snyk_f1_scores)/len(snyk_f1_scores):.2%})")
    
    print()
    print("=" * 80)
    print("RAPOR TAMAMLANDI")
    print("=" * 80)


if __name__ == "__main__":
    generate_analysis_report()

