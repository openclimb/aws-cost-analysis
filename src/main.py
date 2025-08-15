#!/usr/bin/env python3
"""
AWS Cost Analysis and Visualization Tool
サービス別コスト分析と可視化ツール
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
from datetime import datetime
from pathlib import Path
import json

# 日本語フォント設定
plt.rcParams['font.family'] = ['DejaVu Sans']
sns.set_style("whitegrid")

class AWSCostAnalyzer:
    def __init__(self, csv_path: str, output_docs_path: str, output_charts_path: str):
        self.csv_path = csv_path
        self.output_docs_path = Path(output_docs_path)
        self.output_charts_path = Path(output_charts_path)
        self.df = None
        self.services = []
        
        # 出力ディレクトリを作成
        self.output_docs_path.mkdir(parents=True, exist_ok=True)
        self.output_charts_path.mkdir(parents=True, exist_ok=True)
        
        # データを読み込み
        self.load_data()
    
    def load_data(self):
        """CSVデータを読み込み、前処理を実行"""
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"データ読み込み完了: {len(self.df)}行")
            
            # サービス一覧を取得
            self.services = self.df['サービス'].unique()
            print(f"検出されたサービス数: {len(self.services)}")
            
            # 月のカラムを特定
            self.month_columns = [col for col in self.df.columns if '費用（' in col and '）' in col]
            print(f"月次データ列: {self.month_columns}")
            
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            raise
    
    def create_service_line_chart(self, service_name: str) -> str:
        """指定サービスの費用項目別折れ線グラフを生成"""
        service_data = self.df[self.df['サービス'] == service_name].copy()
        
        if service_data.empty:
            return ""
        
        # Plotlyでインタラクティブなチャートを作成
        fig = go.Figure()
        
        # 各費用項目に対して折れ線を追加
        for _, row in service_data.iterrows():
            item_name = row['費用項目']
            description = row['説明']
            
            # 月次データを取得
            costs = []
            months = []
            for month_col in self.month_columns:
                cost = float(row[month_col])
                month_name = month_col.replace('費用（', '').replace('）', '')
                costs.append(cost)
                months.append(month_name)
            
            # Allは太線で表示
            line_width = 4 if item_name == 'All' else 2
            line_dash = 'solid' if item_name == 'All' else 'solid'
            
            fig.add_trace(go.Scatter(
                x=months,
                y=costs,
                mode='lines+markers',
                name=f"{item_name}",
                line=dict(width=line_width, dash=line_dash),
                hovertemplate=f"<b>{item_name}</b><br>" +
                             f"{description}<br>" +
                             "月: %{x}<br>" +
                             "費用: $%{y:.2f}<extra></extra>"
            ))
        
        # レイアウト設定
        fig.update_layout(
            title=f"{service_name} - 費用項目別推移",
            xaxis_title="月",
            yaxis_title="費用 (USD)",
            hovermode='x unified',
            width=1000,
            height=600,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.01
            )
        )
        
        # HTMLファイルとして保存
        chart_filename = f"{service_name.replace(' ', '_').lower()}_cost_trend.html"
        chart_path = self.output_charts_path / chart_filename
        fig.write_html(str(chart_path))
        
        return chart_filename
    
    def analyze_service_characteristics(self, service_name: str) -> dict:
        """サービスの料金特徴を分析"""
        service_data = self.df[self.df['サービス'] == service_name].copy()
        
        if service_data.empty:
            return {}
        
        analysis = {
            'total_items': len(service_data),
            'cost_trends': {},
            'characteristics': []
        }
        
        # 各費用項目の傾向分析
        for _, row in service_data.iterrows():
            item_name = row['費用項目']
            costs = [float(row[col]) for col in self.month_columns]
            
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
    
    def generate_service_markdown(self, service_name: str, chart_filename: str, analysis: dict):
        """サービス別のMarkdownファイルを生成"""
        service_data = self.df[self.df['サービス'] == service_name].copy()
        
        if service_data.empty:
            return
        
        # 現在の日付を取得
        current_date = datetime.now().strftime("%Y/%m/%d")
        
        # ファイル名を決定
        filename = f"{service_name.replace(' ', '_').replace('Amazon_', '').lower()}.md"
        output_path = self.output_docs_path / filename
        
        # Markdownコンテンツを生成
        markdown_content = f"""# {service_name} コスト分析レポート

**分析日**: {current_date}

## 概要

{service_name}の2025年3月から8月までの6ヶ月間のコスト分析結果です。

## コスト推移グラフ

![{service_name} コスト推移](../src/charts/{chart_filename})

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
        for _, row in service_data.iterrows():
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
        for month_col in self.month_columns:
            month_name = month_col.replace('費用（', '').replace('）', '')
            markdown_content += f" {month_name} |"
        
        markdown_content += "\n|---------|"
        for _ in self.month_columns:
            markdown_content += "---------|"
        markdown_content += "\n"
        
        # 各行のデータを追加
        for _, row in service_data.iterrows():
            item_name = row['費用項目']
            markdown_content += f"| {item_name} |"
            
            for month_col in self.month_columns:
                cost = float(row[month_col])
                markdown_content += f" ${cost:.2f} |"
            markdown_content += "\n"
        
        markdown_content += f"""
---
*このレポートは自動生成されました。最新の分析結果については定期的に更新してください。*
"""
        
        # ファイルに書き込み
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"生成完了: {filename}")
    
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
            
            # グラフ生成
            chart_filename = self.create_service_line_chart(service_name)
            
            # 特徴分析
            analysis = self.analyze_service_characteristics(service_name)
            
            # Markdownファイル生成
            self.generate_service_markdown(service_name, chart_filename, analysis)
        
        print(f"\n分析完了! 全{len(self.services)}サービスのレポートを生成しました。")
        print(f"ドキュメント出力先: {self.output_docs_path}")
        print(f"チャート出力先: {self.output_charts_path}")

def main():
    # 環境変数からパスを取得
    input_csv_path = os.getenv('INPUT_CSV_PATH', '../output/aws_service_202503-202508.csv')
    output_docs_path = os.getenv('OUTPUT_DOCS_PATH', '../docs')
    output_charts_path = os.getenv('OUTPUT_CHARTS_PATH', './charts')
    
    # 分析器を初期化して実行
    analyzer = AWSCostAnalyzer(input_csv_path, output_docs_path, output_charts_path)
    analyzer.run_analysis()

if __name__ == "__main__":
    main()