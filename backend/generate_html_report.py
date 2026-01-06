"""
HTML Rapor Oluşturucu

JSON raporunu HTML formatına dönüştürür.
"""

import json
from pathlib import Path
from datetime import datetime


def generate_html_report(json_file: Path):
    """JSON raporunu HTML formatına dönüştürür"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    html_file = json_file.parent / f"report_{json_file.stem.split('_')[-1]}.html"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kapsamlı Test Raporu</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .card .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .metric {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            margin: 5px;
            font-weight: bold;
        }}
        .precision {{ background-color: #e8f5e9; color: #2e7d32; }}
        .recall {{ background-color: #e3f2fd; color: #1565c0; }}
        .f1 {{ background-color: #fff3e0; color: #e65100; }}
        .good {{ color: #27ae60; font-weight: bold; }}
        .bad {{ color: #e74c3c; font-weight: bold; }}
        .performance {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .performance-card {{
            padding: 20px;
            border-radius: 8px;
            background: #f8f9fa;
        }}
        .performance-card h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Kapsamlı Test Raporu</h1>
        <p><strong>Rapor Tarihi:</strong> {datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Test Edilen Projeler:</strong> {data['test_summary']['total_projects']}</p>
        <p><strong>Test Edilen Araçlar:</strong> {', '.join(data['test_summary']['tools_tested'])}</p>
        
        <h2>📊 Genel İstatistikler</h2>
        <div class="summary">
"""
    
    # Başarı oranları
    snyk_success = sum(1 for p in data["projects"].values() if p.get("snyk", {}).get("success"))
    deepsource_success = sum(1 for p in data["projects"].values() if p.get("deepsource", {}).get("success"))
    total = data['test_summary']['total_projects']
    
    html_content += f"""
            <div class="card">
                <h3>Snyk Code Başarı Oranı</h3>
                <div class="value">{snyk_success}/{total}</div>
                <div>{snyk_success/total*100:.1f}%</div>
            </div>
            <div class="card">
                <h3>DeepSource Başarı Oranı</h3>
                <div class="value">{deepsource_success}/{total}</div>
                <div>{deepsource_success/total*100:.1f}%</div>
            </div>
        </div>
        
        <h2>⚡ Performans Metrikleri</h2>
        <div class="performance">
"""
    
    # Performans metrikleri
    snyk_times = [p["snyk"]["scan_duration"] for p in data["projects"].values() 
                  if p.get("snyk", {}).get("success")]
    deepsource_times = [p["deepsource"]["scan_duration"] for p in data["projects"].values() 
                        if p.get("deepsource", {}).get("success")]
    
    if snyk_times:
        avg_snyk = sum(snyk_times)/len(snyk_times)
        html_content += f"""
            <div class="performance-card">
                <h3>Snyk Code</h3>
                <p><strong>Ortalama Süre:</strong> {avg_snyk:.2f}s</p>
                <p><strong>En Hızlı:</strong> {min(snyk_times):.2f}s</p>
                <p><strong>En Yavaş:</strong> {max(snyk_times):.2f}s</p>
            </div>
"""
    
    if deepsource_times:
        avg_deepsource = sum(deepsource_times)/len(deepsource_times)
        html_content += f"""
            <div class="performance-card">
                <h3>DeepSource</h3>
                <p><strong>Ortalama Süre:</strong> {avg_deepsource:.2f}s</p>
                <p><strong>En Hızlı:</strong> {min(deepsource_times):.2f}s</p>
                <p><strong>En Yavaş:</strong> {max(deepsource_times):.2f}s</p>
            </div>
        </div>
"""
    
    if snyk_times and deepsource_times:
        speed_ratio = avg_snyk / avg_deepsource
        html_content += f"""
        <p><strong>DeepSource, Snyk Code'dan {speed_ratio:.1f}x daha hızlı</strong></p>
"""
    
    # Doğruluk metrikleri
    html_content += """
        <h2>🎯 Doğruluk Metrikleri</h2>
        <table>
            <thead>
                <tr>
                    <th>Proje</th>
                    <th>Ground Truth</th>
                    <th>Araç</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1 Score</th>
                    <th>TP</th>
                    <th>FP</th>
                    <th>FN</th>
                </tr>
            </thead>
            <tbody>
"""
    
    projects_with_gt = {k: v for k, v in data["projects"].items() if v.get("ground_truth_count", 0) > 0}
    
    for project_name, project_data in projects_with_gt.items():
        gt_count = project_data['ground_truth_count']
        
        snyk_metrics = project_data.get("snyk", {}).get("comparison_metrics")
        if snyk_metrics:
            html_content += f"""
                <tr>
                    <td rowspan="2"><strong>{project_name}</strong></td>
                    <td rowspan="2">{gt_count}</td>
                    <td>Snyk Code</td>
                    <td><span class="metric precision">{snyk_metrics['precision']:.2%}</span></td>
                    <td><span class="metric recall">{snyk_metrics['recall']:.2%}</span></td>
                    <td><span class="metric f1">{snyk_metrics['f1_score']:.2%}</span></td>
                    <td>{snyk_metrics['true_positives']}</td>
                    <td>{snyk_metrics['false_positives']}</td>
                    <td>{snyk_metrics['false_negatives']}</td>
                </tr>
"""
        
        deepsource_metrics = project_data.get("deepsource", {}).get("comparison_metrics")
        if deepsource_metrics:
            html_content += f"""
                <tr>
                    <td>DeepSource</td>
                    <td><span class="metric precision">{deepsource_metrics['precision']:.2%}</span></td>
                    <td><span class="metric recall">{deepsource_metrics['recall']:.2%}</span></td>
                    <td><span class="metric f1">{deepsource_metrics['f1_score']:.2%}</span></td>
                    <td>{deepsource_metrics['true_positives']}</td>
                    <td>{deepsource_metrics['false_positives']}</td>
                    <td>{deepsource_metrics['false_negatives']}</td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>
        
        <h2>📈 Genel Özet</h2>
"""
    
    # Genel özet
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
    
    for project_data in projects_with_gt.values():
        snyk_metrics = project_data.get("snyk", {}).get("comparison_metrics")
        if snyk_metrics:
            snyk_precisions.append(snyk_metrics["precision"])
            snyk_recalls.append(snyk_metrics["recall"])
            snyk_f1_scores.append(snyk_metrics["f1_score"])
            snyk_tps.append(snyk_metrics["true_positives"])
            snyk_fps.append(snyk_metrics["false_positives"])
            snyk_fns.append(snyk_metrics["false_negatives"])
        
        deepsource_metrics = project_data.get("deepsource", {}).get("comparison_metrics")
        if deepsource_metrics:
            deepsource_precisions.append(deepsource_metrics["precision"])
            deepsource_recalls.append(deepsource_metrics["recall"])
            deepsource_f1_scores.append(deepsource_metrics["f1_score"])
            deepsource_tps.append(deepsource_metrics["true_positives"])
            deepsource_fps.append(deepsource_metrics["false_positives"])
            deepsource_fns.append(deepsource_metrics["false_negatives"])
    
    if snyk_precisions:
        avg_precision_snyk = sum(snyk_precisions)/len(snyk_precisions)
        avg_recall_snyk = sum(snyk_recalls)/len(snyk_recalls)
        avg_f1_snyk = sum(snyk_f1_scores)/len(snyk_f1_scores)
        
        html_content += f"""
        <div class="performance">
            <div class="performance-card">
                <h3>Snyk Code - Genel Metrikler</h3>
                <p><strong>Ortalama Precision:</strong> <span class="metric precision">{avg_precision_snyk:.2%}</span></p>
                <p><strong>Ortalama Recall:</strong> <span class="metric recall">{avg_recall_snyk:.2%}</span></p>
                <p><strong>Ortalama F1 Score:</strong> <span class="metric f1">{avg_f1_snyk:.2%}</span></p>
                <p><strong>Toplam TP:</strong> {sum(snyk_tps)} | <strong>FP:</strong> {sum(snyk_fps)} | <strong>FN:</strong> {sum(snyk_fns)}</p>
            </div>
"""
    
    if deepsource_precisions:
        avg_precision_ds = sum(deepsource_precisions)/len(deepsource_precisions)
        avg_recall_ds = sum(deepsource_recalls)/len(deepsource_recalls)
        avg_f1_ds = sum(deepsource_f1_scores)/len(deepsource_f1_scores)
        
        html_content += f"""
            <div class="performance-card">
                <h3>DeepSource - Genel Metrikler</h3>
                <p><strong>Ortalama Precision:</strong> <span class="metric precision">{avg_precision_ds:.2%}</span></p>
                <p><strong>Ortalama Recall:</strong> <span class="metric recall">{avg_recall_ds:.2%}</span></p>
                <p><strong>Ortalama F1 Score:</strong> <span class="metric f1">{avg_f1_ds:.2%}</span></p>
                <p><strong>Toplam TP:</strong> {sum(deepsource_tps)} | <strong>FP:</strong> {sum(deepsource_fps)} | <strong>FN:</strong> {sum(deepsource_fns)}</p>
            </div>
        </div>
"""
    
    # Karşılaştırma
    if snyk_precisions and deepsource_precisions:
        html_content += """
        <h2>⚖️ Karşılaştırma</h2>
        <ul>
"""
        if avg_precision_snyk > avg_precision_ds:
            html_content += f'<li><strong>Precision:</strong> <span class="good">Snyk Code daha iyi</span> ({avg_precision_snyk:.2%} vs {avg_precision_ds:.2%})</li>'
        else:
            html_content += f'<li><strong>Precision:</strong> <span class="good">DeepSource daha iyi</span> ({avg_precision_ds:.2%} vs {avg_precision_snyk:.2%})</li>'
        
        if avg_recall_snyk > avg_recall_ds:
            html_content += f'<li><strong>Recall:</strong> <span class="good">Snyk Code daha iyi</span> ({avg_recall_snyk:.2%} vs {avg_recall_ds:.2%})</li>'
        else:
            html_content += f'<li><strong>Recall:</strong> <span class="good">DeepSource daha iyi</span> ({avg_recall_ds:.2%} vs {avg_recall_snyk:.2%})</li>'
        
        if avg_f1_snyk > avg_f1_ds:
            html_content += f'<li><strong>F1 Score:</strong> <span class="good">Snyk Code daha iyi</span> ({avg_f1_snyk:.2%} vs {avg_f1_ds:.2%})</li>'
        else:
            html_content += f'<li><strong>F1 Score:</strong> <span class="good">DeepSource daha iyi</span> ({avg_f1_ds:.2%} vs {avg_f1_snyk:.2%})</li>'
        
        html_content += """
        </ul>
"""
    
    html_content += """
        <h2>⚠️ Önemli Notlar</h2>
        <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
            <h3 style="margin-top: 0;">DeepSource Metrikleri Hakkında</h3>
            <p><strong>DeepSource API repository-based çalışır:</strong> DeepSource GraphQL API, sadece GitHub repository'sindeki kodları analiz eder. 
            Local test projeleri (<code>vulnerable_sql_injection</code>, <code>vulnerable_command_injection</code>, vb.) GitHub repository'sinde 
            bulunmadığı için DeepSource API bu projeler için issue tespit edememiştir.</p>
            <p><strong>Çözüm seçenekleri:</strong></p>
            <ul>
                <li><strong>DeepSource CLI kurulumu:</strong> Local dosyaları analiz etmek için DeepSource CLI kurulabilir</li>
                <li><strong>Test projelerini GitHub'a push:</strong> Test projeleri repository'ye eklendiğinde DeepSource API bunları analiz edebilir</li>
                <li><strong>Hibrit yaklaşım:</strong> Snyk Code local analiz için, DeepSource repository analizi için kullanılabilir</li>
            </ul>
            <p><strong>Not:</strong> Bu rapor, DeepSource API'nin repository'deki mevcut kodları analiz ettiğini gösterir. 
            Repository'de aktif issue olmadığı için metrikler %0 görünmektedir.</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML rapor kaydedildi: {html_file}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
    else:
        # En son raporu bul
        results_dir = Path("../results")
        json_files = sorted(results_dir.glob("comprehensive_test_report_*.json"), reverse=True)
        if json_files:
            json_file = json_files[0]
        else:
            print("Rapor dosyası bulunamadı!")
            sys.exit(1)
    
    generate_html_report(json_file)

