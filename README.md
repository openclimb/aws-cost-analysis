# AWS コスト調査プロジェクト

このプロジェクトは、AWS MCPを使用してAWSリソースのコスト分析と調査を行うためのプロジェクトです。

## 概要

AWSの各種リソースのコスト情報を調査・分析し、コスト最適化のための洞察を提供します。
コストは期間によって大きく変動するため、調査時期や期間を明確に指定して分析を行います。

## プロジェクト構成

```
aws-inspect/
├── README.md                 # プロジェクト概要
├── CLAUDE.md                 # Claude用の設定・プロンプト
├── .cursor/                  # Cursor IDE設定
│   └── rules                 # Cursor用ルール
└── docs/                     # AWSリソース別コスト調査結果
    ├── ec2.md                # EC2のコスト調査
    ├── s3.md                 # S3のコスト調査
    ├── rds.md                # RDSのコスト調査
    └── ...                   # その他のリソース
```

## 使用ツール

- **AWS MCP**: AWSリソースの情報取得とコスト分析
- **Claude Code**: コスト調査の実行とドキュメント生成
- **Cursor**: 開発環境

## 調査対象リソース

**対象範囲**: CmBillingGroupが"mp"のリソースのみを調査対象とします。

主要なAWSリソースのコスト分析を行います：

- EC2 (Elastic Compute Cloud)
- S3 (Simple Storage Service)
- RDS (Relational Database Service)
- Lambda
- CloudFront
- ELB (Elastic Load Balancing)
- その他必要に応じて追加

**重要**: すべてのコスト分析は、Cost Explorerのフィルタ条件として「CmBillingGroup = "mp"」を適用して実行します。

## 使用方法

1. AWS MCP の設定を確認
2. 調査期間を指定してコスト分析を実行
3. 各リソースの詳細なコスト情報を `docs/` ディレクトリに保存
4. 結果を元にコスト最適化提案を作成

## 注意事項

- コスト情報は調査時点での情報であり、リアルタイムで変動します
- 調査期間や地域（リージョン）によってコストが大きく異なります
- 料金体系の変更により、過去のデータと現在の料金に差異が生じる場合があります