#!/bin/bash

# AWS Cost Analysis Runner
# AWSコスト分析実行スクリプト

echo "=== AWS Cost Analysis Tool ==="
echo "開始時刻: $(date)"

# Dockerが利用可能かチェック
if ! command -v docker &> /dev/null; then
    echo "エラー: Dockerがインストールされていません"
    exit 1
fi

# Docker Composeが利用可能かチェック
if ! command -v docker-compose &> /dev/null; then
    echo "エラー: Docker Composeがインストールされていません"
    exit 1
fi

# CSVファイルの存在確認
if [ ! -f "../output/aws_service_202503-202508.csv" ]; then
    echo "エラー: 入力CSVファイルが見つかりません: ../output/aws_service_202503-202508.csv"
    exit 1
fi

# ディレクトリ作成
echo "出力ディレクトリを作成中..."
mkdir -p ../docs
mkdir -p ./charts

# Docker Composeでコンテナを構築・実行
echo "Dockerコンテナを構築・実行中..."
docker-compose up --build

# 実行結果の確認
if [ $? -eq 0 ]; then
    echo "=== 分析完了 ==="
    echo "生成されたファイル:"
    echo "  - ドキュメント: docs/*.md"
    echo "  - チャート: src/charts/*.html"
    echo "完了時刻: $(date)"
else
    echo "エラー: 分析の実行に失敗しました"
    exit 1
fi