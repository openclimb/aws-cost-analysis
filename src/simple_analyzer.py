#!/usr/bin/env python3
"""
AWS Cost Analysis - Simple Version
外部ライブラリを使わないシンプルなバージョン
"""

import csv
import os
from datetime import datetime
from pathlib import Path

class SimpleAWSCostAnalyzer:
    def __init__(self, csv_path: str, output_docs_path: str):
        self.csv_path = csv_path
        self.output_docs_path = Path(output_docs_path)
        self.data = []
        self.services = set()
        
        # 出力ディレクトリを作成
        self.output_docs_path.mkdir(parents=True, exist_ok=True)
        
        # データを読み込み
        self.load_data()
    
    def load_data(self):
        """CSVデータを読み込み"""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.data.append(row)
                    self.services.add(row['サービス'])
            
            print(f"データ読み込み完了: {len(self.data)}行")
            print(f"検出されたサービス数: {len(self.services)}")
            
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            raise
    
    def analyze_service_characteristics(self, service_name: str) -> dict:
        """サービスの料金特徴を分析"""
        service_data = [row for row in self.data if row['サービス'] == service_name]
        
        if not service_data:
            return {}
        
        analysis = {
            'total_items': len(service_data),
            'cost_trends': {},
            'characteristics': []
        }
        
        # 月のカラムを特定
        month_columns = [col for col in service_data[0].keys() if '費用（' in col and '）' in col]
        
        # 各費用項目の傾向分析
        for row in service_data:
            item_name = row['費用項目']
            costs = [float(row[col]) for col in month_columns if row[col]]
            
            # 傾向計算
            if len(costs) > 1:
                growth_rate = ((costs[-1] - costs[0]) / costs[0]) * 100 if costs[0] != 0 else 0
                avg_cost = sum(costs) / len(costs)
                max_cost = max(costs)
                min_cost = min(costs)
                
                analysis['cost_trends'][item_name] = {
                    'growth_rate': growth_rate,
                    'average': avg_cost,
                    'max': max_cost,
                    'min': min_cost,
                    'volatility': max_cost - min_cost
                }
        
        # 特徴の判定
        all_data = analysis['cost_trends'].get('All', {})
        if all_data:
            if all_data['growth_rate'] > 20:
                analysis['characteristics'].append("急成長トレンド（20%以上の増加）")
            elif all_data['growth_rate'] > 5:
                analysis['characteristics'].append("成長トレンド（5%以上の増加）")
            elif all_data['growth_rate'] < -10:
                analysis['characteristics'].append("コスト削減トレンド（10%以上の削減）")
            else:
                analysis['characteristics'].append("安定したコスト推移")
            
            if all_data['volatility'] > all_data['average'] * 0.5:
                analysis['characteristics'].append("変動性が高い")
            else:
                analysis['characteristics'].append("変動性が低い")
        
        return analysis
    
    def generate_service_markdown(self, service_name: str, analysis: dict):
        """サービス別のMarkdownファイルを生成"""
        service_data = [row for row in self.data if row['サービス'] == service_name]
        
        if not service_data:
            return
        
        # 現在の日付を取得
        current_date = datetime.now().strftime("%Y/%m/%d")
        
        # ファイル名を決定
        filename = f"{service_name.replace(' ', '_').replace('Amazon_', '').lower()}.md"
        output_path = self.output_docs_path / filename
        
        # 月のカラムを特定
        month_columns = [col for col in service_data[0].keys() if '費用（' in col and '）' in col]
        
        # Markdownコンテンツを生成
        markdown_content = f"""# {service_name} コスト分析レポート

**分析日**: {current_date}

## 概要

{service_name}の2025年3月から8月までの6ヶ月間のコスト分析結果です。

## 料金の特徴

### 分析サマリー
"""
        
        # 特徴を追加
        if analysis.get('characteristics'):
            for characteristic in analysis['characteristics']:
                markdown_content += f"- {characteristic}\n"
        
        markdown_content += f"""
### 費用項目詳細

| 費用項目 | 説明 | 6ヶ月平均 | 成長率 | 変動幅 |
|---------|------|----------|--------|--------|
"""
        
        # 各費用項目の詳細を追加
        for row in service_data:
            item_name = row['費用項目']
            description = row['説明']
            
            trend_data = analysis['cost_trends'].get(item_name, {})
            avg_cost = trend_data.get('average', 0)
            growth_rate = trend_data.get('growth_rate', 0)
            volatility = trend_data.get('volatility', 0)
            
            markdown_content += f"| {item_name} | {description} | ${avg_cost:.2f} | {growth_rate:+.1f}% | ${volatility:.2f} |\n"
        
        # コスト最適化提案
        markdown_content += f"""
## コスト最適化提案

### 主要な推奨事項
"""
        
        # サービス固有の最適化提案を生成
        optimization_suggestions = self.generate_optimization_suggestions(service_name, analysis)
        for suggestion in optimization_suggestions:
            markdown_content += f"- {suggestion}\n"
        
        markdown_content += f"""
### 月次コスト詳細

| 費用項目 |"""
        
        # 月のヘッダーを追加
        for month_col in month_columns:
            month_name = month_col.replace('費用（', '').replace('）', '')
            markdown_content += f" {month_name} |"
        
        markdown_content += "\n|---------|"
        for _ in month_columns:
            markdown_content += "---------|"
        markdown_content += "\n"
        
        # 各行のデータを追加
        for row in service_data:
            item_name = row['費用項目']
            markdown_content += f"| {item_name} |"
            
            for month_col in month_columns:
                cost = float(row[month_col]) if row[month_col] else 0
                markdown_content += f" ${cost:.2f} |"
            markdown_content += "\n"
        
        # Mermaid折れ線グラフを生成
        mermaid_chart, legend = self.create_mermaid_chart(service_data, month_columns)
        markdown_content += f"""
### コスト推移グラフ

```mermaid
{mermaid_chart}
```

**凡例:**
{legend}
"""
        
        markdown_content += f"""
---
*このレポートは自動生成されました。最新の分析結果については定期的に更新してください。*
"""
        
        # ファイルに書き込み
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"生成完了: {filename}")
    
    def create_mermaid_chart(self, service_data, month_columns):
        """Mermaid折れ線グラフを生成"""
        # 主要な費用項目を取得（All + 上位3項目）
        chart_data = []
        
        for row in service_data:
            item_name = row['費用項目']
            costs = []
            for month_col in month_columns:
                cost = float(row[month_col]) if row[month_col] else 0
                costs.append(cost)
            
            # Allは必ず含める、その他は平均額の高い順
            avg_cost = sum(costs) / len(costs) if costs else 0
            chart_data.append({
                'name': item_name,
                'costs': costs,
                'avg': avg_cost
            })
        
        # 平均コストの高い順にソート（Allは最初に保持）
        all_item = None
        other_items = []
        for item in chart_data:
            if item['name'] == 'All':
                all_item = item
            else:
                other_items.append(item)
        
        other_items.sort(key=lambda x: x['avg'], reverse=True)
        sorted_data = [all_item] + other_items[:3] if all_item else other_items[:4]
        
        if not sorted_data:
            return "データなし"
        
        # 月の名前を短縮
        month_names = []
        for month_col in month_columns:
            month_name = month_col.replace('費用（', '').replace('）', '').replace('2025年', '')
            month_names.append(month_name)
        
        # Mermaidチャートを生成 (GitGraph風の表現を使用)
        mermaid_lines = ["gitgraph"]
        mermaid_lines.append("    options:")
        mermaid_lines.append("    {")
        mermaid_lines.append("        \"theme\": \"base\",")
        mermaid_lines.append("        \"themeVariables\": {")
        mermaid_lines.append("            \"primaryColor\": \"#ff6b6b\"")
        mermaid_lines.append("        }")
        mermaid_lines.append("    }")
        
        # より適切なMermaidフォーマットとして、flowchartを使用
        mermaid_lines = ["flowchart LR"]
        
        # 各月をノードとして作成
        for i, month in enumerate(month_names):
            mermaid_lines.append(f"    {month}[{month}]")
        
        # データ系列の接続を作成
        if sorted_data:
            main_item = sorted_data[0]  # Allまたは最初の項目
            costs = main_item['costs']
            
            # コスト情報をノードのラベルに含める
            for i in range(len(month_names)):
                if i < len(costs):
                    cost = costs[i]
                    month = month_names[i]
                    mermaid_lines.append(f"    {month}[\"{month}<br/>${cost:.2f}\"]")
            
            # 月間の接続を作成
            for i in range(len(month_names) - 1):
                if i + 1 < len(month_names):
                    curr_month = month_names[i]
                    next_month = month_names[i + 1]
                    mermaid_lines.append(f"    {curr_month} --> {next_month}")
        
        # より良い選択肢：XYチャート形式
        mermaid_lines = ["xychart-beta"]
        mermaid_lines.append("    title \"コスト推移\"")
        
        # X軸の月を設定
        x_axis_data = '[' + ', '.join([f'"{m}"' for m in month_names]) + ']'
        mermaid_lines.append(f"    x-axis {x_axis_data}")
        
        # Y軸の設定（最小値を0に固定）
        max_cost = max(max(item['costs']) for item in sorted_data if item['costs'])
        y_max = int(max_cost * 1.1)
        mermaid_lines.append(f"    y-axis \"コスト (USD)\" 0 --> {y_max}")
        
        # データ系列を追加（グラフ内凡例付き）
        legend_lines = []
        # Mermaidのxychart-betaのデフォルト色順序
        mermaid_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        
        for i, item in enumerate(sorted_data):
            if item['costs']:
                costs_data = '[' + ', '.join([f"{cost:.2f}" for cost in item['costs']]) + ']'
                # 項目名を短縮
                display_name = item['name']
                if len(display_name) > 20:
                    display_name = display_name[:17] + "..."
                
                # プロット点付きの線を追加
                mermaid_lines.append(f"    line \"{display_name}\" {costs_data}")
                
                # 凡例用の情報を保存（Mermaidの実際の色順序に合わせる）
                color = mermaid_colors[i % len(mermaid_colors)]
                legend_lines.append(f"- <span style=\"color:{color}\">●</span> **{item['name']}** (平均: ${item['avg']:.2f})")
        
        return "\n".join(mermaid_lines), "\n".join(legend_lines)
    
    def create_ascii_chart_backup(self, service_data, month_columns):
        """簡易ASCII折れ線グラフを生成"""
        chart_lines = []
        
        # 主要な費用項目を取得（All + 上位3項目）
        chart_data = []
        
        for row in service_data:
            item_name = row['費用項目']
            costs = []
            for month_col in month_columns:
                cost = float(row[month_col]) if row[month_col] else 0
                costs.append(cost)
            
            # Allは必ず含める、その他は平均額の高い順
            if item_name == 'All' or len(chart_data) < 4:
                avg_cost = sum(costs) / len(costs) if costs else 0
                chart_data.append({
                    'name': item_name,
                    'costs': costs,
                    'avg': avg_cost
                })
        
        # 平均コストの高い順にソート（Allは最初に保持）
        all_item = None
        other_items = []
        for item in chart_data:
            if item['name'] == 'All':
                all_item = item
            else:
                other_items.append(item)
        
        other_items.sort(key=lambda x: x['avg'], reverse=True)
        sorted_data = [all_item] + other_items[:3] if all_item else other_items[:4]
        
        if not sorted_data:
            return "データなし"
        
        # 月の名前を短縮
        month_names = []
        for month_col in month_columns:
            month_name = month_col.replace('費用（', '').replace('）', '').replace('2025年', '')
            month_names.append(month_name)
        
        # 全データの最大・最小を取得
        all_costs = []
        for item in sorted_data:
            all_costs.extend(item['costs'])
        
        if not all_costs:
            return "データなし"
        
        max_cost = max(all_costs)
        min_cost = min(all_costs)
        height = 20  # グラフの高さ
        width = len(month_names)
        
        chart_lines.append(f"コスト推移 (最大: ${max_cost:.2f}, 最小: ${min_cost:.2f})")
        chart_lines.append("")
        
        # Y軸を作成（上から下へ）
        y_scale = []
        for i in range(height + 1):
            if max_cost > min_cost:
                value = max_cost - (max_cost - min_cost) * i / height
            else:
                value = max_cost
            y_scale.append(value)
        
        # グラフエリアを初期化
        grid = [[' ' for _ in range(width * 4)] for _ in range(height + 1)]
        
        # 折れ線を描画
        symbols = ['●', '■', '▲', '♦']  # 各データ系列用のシンボル
        
        for data_idx, item in enumerate(sorted_data):
            symbol = symbols[data_idx % len(symbols)]
            costs = item['costs']
            
            for i in range(len(costs)):
                cost = costs[i]
                # Y座標を計算
                if max_cost > min_cost:
                    y = int((max_cost - cost) * height / (max_cost - min_cost))
                else:
                    y = height // 2
                
                y = max(0, min(height, y))
                x = i * 4
                
                # ポイントをプロット
                if x < len(grid[y]):
                    grid[y][x] = symbol
                
                # 前のポイントと線で結ぶ
                if i > 0:
                    prev_cost = costs[i-1]
                    if max_cost > min_cost:
                        prev_y = int((max_cost - prev_cost) * height / (max_cost - min_cost))
                    else:
                        prev_y = height // 2
                    prev_y = max(0, min(height, prev_y))
                    prev_x = (i-1) * 4
                    
                    # 線を引く
                    self._draw_line(grid, prev_x, prev_y, x, y, '─' if prev_y == y else ('/' if y < prev_y else '\\'))
        
        # グリッドを文字列に変換
        for i, row in enumerate(grid):
            y_label = f"${y_scale[i]:>7.1f} |"
            line = ''.join(row).rstrip()
            chart_lines.append(y_label + line)
        
        # X軸ラベル
        x_axis = "        |"
        for i, month in enumerate(month_names):
            x_axis += f"{month:>4}"
        chart_lines.append(x_axis)
        
        # 凡例
        chart_lines.append("")
        chart_lines.append("凡例:")
        for i, item in enumerate(sorted_data):
            symbol = symbols[i % len(symbols)]
            chart_lines.append(f"  {symbol} {item['name']} (平均: ${item['avg']:.2f})")
        
        return "\n".join(chart_lines)
    
    def _draw_line(self, grid, x1, y1, x2, y2, char):
        """2点間に線を描画"""
        if x1 == x2:  # 垂直線
            start_y, end_y = (y1, y2) if y1 < y2 else (y2, y1)
            for y in range(start_y, end_y + 1):
                if 0 <= y < len(grid) and 0 <= x1 < len(grid[y]):
                    if grid[y][x1] == ' ':
                        grid[y][x1] = '│'
        elif y1 == y2:  # 水平線
            start_x, end_x = (x1, x2) if x1 < x2 else (x2, x1)
            for x in range(start_x, end_x + 1):
                if 0 <= y1 < len(grid) and 0 <= x < len(grid[y1]):
                    if grid[y1][x] == ' ':
                        grid[y1][x] = '─'
        else:  # 斜め線
            steps = max(abs(x2 - x1), abs(y2 - y1))
            for i in range(1, steps):
                x = x1 + (x2 - x1) * i // steps
                y = y1 + (y2 - y1) * i // steps
                if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
                    if grid[y][x] == ' ':
                        grid[y][x] = char
    
    def generate_optimization_suggestions(self, service_name: str, analysis: dict) -> list:
        """サービス固有のコスト最適化提案を生成"""
        suggestions = []
        
        # サービス別の固有提案
        service_suggestions = {
            'Amazon S3': [
                "ライフサイクルポリシーを設定して、古いデータをGlacierに自動移行",
                "アクセス頻度の低いデータにはIntelligent Tieringを活用",
                "不要な重複データの削除とデータ重複排除の実装",
                "リージョン間レプリケーションの必要性を定期的に見直し"
            ],
            'Amazon EC2': [
                "予約インスタンスの購入でオンデマンド料金を削減",
                "使用率の低いインスタンスのサイジング見直し",
                "スポットインスタンスの活用検討",
                "不要なElastic IPアドレスの解放"
            ],
            'Amazon RDS': [
                "データベースインスタンスのサイジング最適化",
                "自動バックアップ期間の見直し",
                "読み取り専用レプリカの必要性評価",
                "予約インスタンスの活用検討"
            ],
            'Amazon CloudFront': [
                "キャッシュ設定の最適化でオリジンアクセス削減",
                "価格クラスの見直しで配信コスト削減",
                "Origin Shieldの利用効果検証",
                "不要なディストリビューションの削除"
            ],
            'Amazon Lambda': [
                "メモリサイズと実行時間の最適化",
                "不要な関数実行の削除",
                "プロビジョンド同時実行の見直し",
                "関数の統合・集約検討"
            ]
        }
        
        # サービス固有の提案を追加
        if service_name in service_suggestions:
            suggestions.extend(service_suggestions[service_name])
        
        # 成長率に基づく提案
        all_trends = analysis['cost_trends'].get('All', {})
        if all_trends.get('growth_rate', 0) > 20:
            suggestions.append("急激なコスト増加が見られるため、使用量とリソース配置の緊急見直しが必要")
        
        return suggestions[:4]  # 最大4つの提案
    
    def run_analysis(self):
        """全サービスの分析を実行"""
        print("AWS コスト分析を開始...")
        
        for service_name in self.services:
            print(f"\n{service_name} の分析中...")
            
            # 特徴分析
            analysis = self.analyze_service_characteristics(service_name)
            
            # Markdownファイル生成
            self.generate_service_markdown(service_name, analysis)
        
        print(f"\n分析完了! 全{len(self.services)}サービスのレポートを生成しました。")
        print(f"ドキュメント出力先: {self.output_docs_path}")

def main():
    # パスを指定
    input_csv_path = '../output/aws_service_202503-202508.csv'
    output_docs_path = '../docs'
    
    # 分析器を初期化して実行
    analyzer = SimpleAWSCostAnalyzer(input_csv_path, output_docs_path)
    analyzer.run_analysis()

if __name__ == "__main__":
    main()