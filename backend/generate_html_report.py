"""
HTML Rapor Oluşturucu

JSON raporunu HTML formatına dönüştürür.
Modern koyu tema ile uyumlu tasarım.
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
    <title>Kapsamlı Test Raporu - SmartTestAI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            /* Dark Theme Colors */
            --bg-primary: #0a0e27;
            --bg-secondary: #141b2d;
            --bg-tertiary: #1a2332;
            --bg-card: #1e2838;
            --bg-hover: #252f42;
            
            /* Accent Colors */
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
            
            /* Text Colors */
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            
            /* Status Colors */
            --success: #10b981;
            --error: #ef4444;
            --warning: #f59e0b;
            --info: #3b82f6;
            
            /* Shadows */
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 20px rgba(99, 102, 241, 0.3);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: var(--bg-secondary);
            border-radius: 20px;
            padding: 40px;
            box-shadow: var(--shadow-lg);
            border: 1px solid rgba(99, 102, 241, 0.1);
            backdrop-filter: blur(10px);
        }}
        
        h1 {{
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 20px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 40px rgba(99, 102, 241, 0.5);
            border-bottom: 3px solid var(--accent-primary);
            padding-bottom: 15px;
            position: relative;
        }}
        
        h1::after {{
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 100px;
            height: 3px;
            background: var(--accent-gradient);
        }}
        
        h2 {{
            color: var(--text-primary);
            margin-top: 40px;
            margin-bottom: 25px;
            font-size: 2rem;
            font-weight: 700;
            border-left: 4px solid var(--accent-primary);
            padding-left: 20px;
            position: relative;
        }}
        
        h2::before {{
            content: '';
            position: absolute;
            left: -4px;
            top: 0;
            bottom: 0;
            width: 4px;
            background: var(--accent-gradient);
        }}
        
        h3 {{
            color: var(--text-primary);
            font-weight: 600;
            margin-bottom: 15px;
        }}
        
        p {{
            color: var(--text-secondary);
            margin: 10px 0;
        }}
        
        strong {{
            color: var(--text-primary);
            font-weight: 600;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        
        .card {{
            background: var(--bg-card);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 30px;
            box-shadow: var(--shadow-md);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--accent-gradient);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-glow);
            border-color: var(--accent-primary);
        }}
        
        .card:hover::before {{
            opacity: 1;
        }}
        
        .card h3 {{
            margin: 0 0 15px 0;
            font-size: 0.95rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }}
        
        .card .value {{
            font-size: 3rem;
            font-weight: 800;
            color: var(--text-primary);
            margin-bottom: 5px;
            text-shadow: 0 0 10px currentColor;
        }}
        
        .card div:last-child {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            background: var(--bg-card);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(99, 102, 241, 0.1);
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(99, 102, 241, 0.1);
        }}
        
        th {{
            background: var(--bg-tertiary);
            color: var(--text-primary);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1px;
        }}
        
        td {{
            color: var(--text-secondary);
        }}
        
        tr:hover {{
            background: var(--bg-hover);
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .metric {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 8px;
            margin: 3px;
            font-weight: 600;
            font-size: 0.9rem;
            border: 1px solid;
        }}
        
        .precision {{
            background: rgba(16, 185, 129, 0.15);
            color: var(--success);
            border-color: rgba(16, 185, 129, 0.3);
        }}
        
        .recall {{
            background: rgba(59, 130, 246, 0.15);
            color: var(--info);
            border-color: rgba(59, 130, 246, 0.3);
        }}
        
        .f1 {{
            background: rgba(245, 158, 11, 0.15);
            color: var(--warning);
            border-color: rgba(245, 158, 11, 0.3);
        }}
        
        .good {{
            color: var(--success);
            font-weight: 700;
        }}
        
        .bad {{
            color: var(--error);
            font-weight: 700;
        }}
        
        .performance {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        
        .performance-card {{
            padding: 25px;
            border-radius: 12px;
            background: var(--bg-card);
            border: 1px solid rgba(99, 102, 241, 0.2);
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
        }}
        
        .performance-card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
            border-color: var(--accent-primary);
        }}
        
        .performance-card h3 {{
            margin-top: 0;
            margin-bottom: 20px;
            color: var(--text-primary);
            font-size: 1.3rem;
            font-weight: 700;
        }}
        
        .performance-card p {{
            margin: 12px 0;
            color: var(--text-secondary);
        }}
        
        .performance-card strong {{
            color: var(--text-primary);
        }}
        
        .warning-box {{
            background: rgba(245, 158, 11, 0.15);
            border-left: 4px solid var(--warning);
            padding: 20px;
            margin: 30px 0;
            border-radius: 12px;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}
        
        .warning-box h3 {{
            margin-top: 0;
            color: var(--warning);
            font-weight: 700;
        }}
        
        .warning-box p {{
            color: var(--text-secondary);
            margin: 10px 0;
        }}
        
        .warning-box ul {{
            margin: 15px 0;
            padding-left: 25px;
            color: var(--text-secondary);
        }}
        
        .warning-box li {{
            margin: 8px 0;
        }}
        
        .warning-box code {{
            background: var(--bg-tertiary);
            padding: 2px 8px;
            border-radius: 4px;
            color: var(--text-primary);
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        ul {{
            list-style: none;
            padding: 0;
        }}
        
        ul li {{
            padding: 12px 0;
            border-bottom: 1px solid rgba(99, 102, 241, 0.1);
            color: var(--text-secondary);
        }}
        
        ul li:last-child {{
            border-bottom: none;
        }}
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {{
            width: 12px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--bg-card);
            border-radius: 6px;
            border: 2px solid var(--bg-secondary);
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--accent-primary);
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            h2 {{
                font-size: 1.5rem;
            }}
            
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .performance {{
                grid-template-columns: 1fr;
            }}
            
            table {{
                font-size: 0.9rem;
            }}
            
            th, td {{
                padding: 10px;
            }}
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
        <p style="text-align: center; font-size: 1.2rem; color: var(--text-primary); margin: 20px 0;"><strong>DeepSource, Snyk Code'dan {speed_ratio:.1f}x daha hızlı</strong></p>
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
        <div class="warning-box">
            <h3>DeepSource Metrikleri Hakkında</h3>
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
    return html_file


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
