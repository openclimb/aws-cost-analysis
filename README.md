# AWS Cost Analysis Project

このプロジェクトは、AWS Cost Explorer MCPサーバーを使用してAWSのコスト分析を行うためのプロジェクトです。

## プロジェクト概要

AWS MCPサーバーを通じて、AWSの各サービスの詳細なコスト分析を実行し、月別・サービス別・費用項目別の包括的なレポートを生成します。

## ⚠️ 重要な注意事項

### データの信頼性について

**既存のCSVファイルは実際のコストデータではありません！**

#### なぜ間違えたのか？
1. **データファイルの信頼性を確認しなかった**
   - `mp_billing_group_costs.csv`や`aws_service_202503-202508.csv`は**サンプルデータ**
   - 実際のAWSコストとは全く異なる値が記載されている

2. **データの妥当性チェックを怠った**
   - CloudFrontが326個のディストリビューションを持っているのに、月額$47.56は明らかに不自然
   - 実際のコストは$17,480.75（約370倍の差）

3. **複数のデータソースの整合性を確認しなかった**
   - 同じサービスで異なる値が記載されているファイルが複数存在

#### 正しいアプローチ
1. **必ず実際のAWS Cost Explorerデータを使用**
   ```bash
   aws ce get-cost-and-usage --time-period Start=2025-07-01,End=2025-08-01 \
     --granularity MONTHLY --metrics UnblendedCost \
     --group-by Type=DIMENSION,Key=SERVICE \
     --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon CloudFront"],"MatchOptions":["EQUALS"]}}'
   ```

2. **データの妥当性チェック**
   - 金額が現実的かチェック
   - リソース数とコストの整合性を確認
   - 複数ファイル間の整合性を確認

3. **既存ファイルの扱い**
   - `output/`ディレクトリのCSVファイルは**参考用サンプル**
   - 実際の分析には使用しない
   - ファイル名に「sample」や「test」が含まれている場合は特に注意

#### データファイルの分類
| ファイル名 | 用途 | 信頼性 |
|------------|------|--------|
| `sample.csv` | サンプルフォーマット | ❌ 実際のデータではない |
| `mp_billing_group_costs.csv` | サンプルデータ | ❌ 実際のデータではない |
| `aws_service_202503-202508.csv` | サンプルデータ | ❌ 実際のデータではない |

## セットアップ

### 1. AWS MCP サーバーの設定

```bash
# AWS Cost Explorer MCPサーバーを追加
claude mcp add cost-explorer uvx awslabs.cost-explorer-mcp-server@latest

# 接続確認
claude mcp list
```

### 2. AWS認証情報の設定

```bash
# AWS認証情報が設定されていることを確認
aws configure list
```

### 3. 必要な権限

以下のAWS権限が必要です：
- `ce:GetCostAndUsage` - コストと使用量データの取得
- `ce:GetDimensionValues` - ディメンション値の取得
- `ce:GetUsageMetrics` - 使用量メトリクスの取得
- `ce:ListCostCategoryDefinitions` - コストカテゴリ定義の一覧取得
- `pricing:GetProducts` - 料金情報の取得
- `pricing:DescribeServices` - サービス情報の取得

## 出力ファイル

### 生成されるCSVファイル

1. **`aws_cost_report_3months.csv`** - 3ヶ月間の詳細レポート
2. **`aws_cost_summary.csv`** - 月次サマリーレポート
3. **`aws_service_detail_costs.csv`** - サービス別詳細コスト
4. **`aws_service_monthly_detail_costs.csv`** - 月別詳細コスト分析（推奨）

**サンプルファイル**: `output/sample.csv` に推奨フォーマットのサンプルファイルを用意しています。実際のデータ構造や出力形式を確認する際の参考にしてください。

### 推奨フォーマット：月別詳細コスト分析

`aws_service_monthly_detail_costs.csv` は以下の構造で作成されます：

#### ファイル構造

```csv
サービス,費用項目,説明,費用（2025年3月）,費用（2025年4月）,費用（2025年5月）,費用（2025年6月）,費用（2025年7月）,費用（2025年8月）
```

**注意**: 月のヘッダー列は分析対象期間に応じて増減します。新しい月のデータを追加する際は、既存の列の右側に新しい月の列を追記していく構造になります。例：
- 9月のデータ追加時：`費用（2025年9月）`列を最右端に追加
- 過去データを含める場合：`費用（2025年2月）`列を適切な位置に挿入

#### 主要な特徴

1. **各サービスの合計表示**
   - 費用項目: `All`
   - 説明: `全体費用`
   - 各月の当該サービス総コストを表示

2. **詳細な費用項目**
   - サービス内の個別機能・リソース別コスト
   - 日本語での詳細説明付き

3. **月次推移の可視化**
   - 6ヶ月間の継続的なコスト推移
   - 前月比較による増減傾向の把握

#### サンプル出力例

```csv
Amazon S3,All,全体費用,65.59,80.14,93.07,107.36,122.63,40.87
Amazon S3,Standard Storage,標準ストレージの月額料金,32.45,38.67,45.67,52.34,58.90,19.63
Amazon S3,PUT/COPY/POST/LIST Requests,オブジェクトの書き込み・コピー・リスト操作,2.34,2.89,3.45,3.98,4.56,1.52
Amazon EC2,All,全体費用,710.81,801.25,924.41,1016.80,1105.60,368.20
Amazon EC2,On-Demand Instances (t3.medium),中型汎用インスタンスの時間課金,234.56,278.90,324.56,367.89,398.45,132.82
```

## 主要なAWSサービス分析項目
- Relational Database Service
- EC2 その他
- CloudFront
- CloudWatch
- S3
- Elastic Container Service for Kubernetes
- VPC
- Elastic Container Service
- Backup
- EC2 インスタンス
- ElastiCache
- WAF
- Elastic Load Balancing
- Managed Service for Prometheus
- OpenSearch Service
- MQ
- Config
- Direct Connect
- Route 53
- Security Hub
- GuardDuty
- Secrets Manager
- APN Annual Program Fee
- EC2 Container Registry (ECR)
- Elastic File System
- Lambda
- Transfer Family
- Key Management Service
- CodePipeline
- API Gateway
- CodeBuild
- Directory Service
- Managed Grafana
- QuickSight
- End User Messaging
- SES
- Polly
- DynamoDB
- F5 Rules for WAF - Common Vulnerabilities & Exposures (CVE) Rules
- Alert Logic Managed Rules for WAF OWASP Top 10 for WordPress
- Glue
- Kinesis
- Amplify
- CloudWatch Events
- Cloud Map
- Step Functions
- SageMaker
- CodeCommit

## フィルタ条件

コスト分析時は以下のフィルタ条件を適用：

```
フィルタ条件: CmBillingGroup = "mp" のみ対象
期間: 指定した期間（例：過去6ヶ月）
リージョン: 全リージョン対象
```

## 使用方法

1. AWS MCP サーバーが正常に接続されていることを確認
2. 分析対象期間を決定（推奨：6ヶ月間）
3. Cost Explorer APIを通じてデータを取得
4. CSV形式でレポートを出力
5. 月次推移とサービス別内訳を分析

## 注意事項

- Cost Explorer APIは1リクエストあたり$0.01の料金が発生
- データは通常24-48時間の遅延がある
- 為替レートの変動を考慮する必要がある
- API制限に注意する

## コスト分析と可視化システム

### 📊 システム概要

このシステムは、AWSのコストデータ（CSV形式）を分析し、各サービス別の詳細なMarkdownレポートを自動生成します。生成されるレポートには、Mermaid折れ線グラフによる美しいコスト推移の可視化が含まれます。

### 🚀 クイックスタート

#### 前提条件
- Python 3.7以上がインストールされていること
- 入力CSVファイルが `output/` ディレクトリに配置されていること

#### 基本的な実行手順

1. **プロジェクトディレクトリに移動**
   ```bash
   cd /path/to/aws-inspect
   ```

2. **入力データの確認**
   ```bash
   ls output/
   # aws_service_202503-202508.csv が存在することを確認
   ```

3. **レポート生成の実行**
   ```bash
   cd src
   python3 simple_analyzer.py
   ```

4. **生成結果の確認**
   ```bash
   ls ../docs/
   # 各サービスの.mdファイルが生成されることを確認
   ```

### 📂 入力データ形式

入力CSVファイルは以下の形式で準備してください：

```csv
サービス,費用項目,説明,費用（2025年3月）,費用（2025年4月）,費用（2025年5月）,費用（2025年6月）,費用（2025年7月）,費用（2025年8月）
Amazon S3,All,全体費用,65.59,80.14,93.07,107.36,122.63,40.87
Amazon S3,Standard Storage,標準ストレージの月額料金,32.45,38.67,45.67,52.34,58.90,19.63
```

**重要**: 
- ヘッダー行に「サービス」「費用項目」「説明」と月別費用列が必要
- 各サービスの最初の行は必ず「All」（全体費用）にしてください
- 月の列名は「費用（YYYY年MM月）」形式で記載

### 🎯 実行オプション

#### 1. シンプル版（推奨）
外部ライブラリ不要で軽量実行：
```bash
cd src
python3 simple_analyzer.py
```

#### 2. Docker版（高機能）
コンテナ環境での実行：
```bash
cd src
chmod +x run.sh
./run.sh
```

#### 3. カスタムパス指定
異なる入力ファイルを使用する場合：
```python
# simple_analyzer.py内で以下を変更
input_csv_path = '../output/your_custom_file.csv'
output_docs_path = '../custom_docs'
```

### 📋 生成されるレポート内容

各AWSサービスに対して以下の内容を含むMarkdownファイルが `docs/` に生成されます：

#### 📊 レポート構成
1. **コスト推移分析**: 6ヶ月間の成長率・変動性の評価
2. **費用項目詳細表**: 各項目の平均コスト・成長率・変動幅
3. **最適化提案**: サービス固有のコスト削減方法（最大4項目）
4. **月次詳細データ**: 表形式での費用内訳
5. **Mermaid折れ線グラフ**: 
   - Y軸0始まりの正確な推移表示
   - 最大4系列の費用項目を同時表示
   - プロット点付きの美しい折れ線
   - 色分けされた凡例（平均値付き）

#### 📈 グラフの特徴
- **Y軸**: 0から最大値までの範囲で正確な比較が可能
- **凡例**: Mermaidの実際の色と完全一致
- **データ系列**: 「All」（全体）+ 平均コスト上位3項目
- **プロット点**: 各月のデータポイントが明確に表示

### 🗂️ 対応サービス一覧

生成される主要なレポートファイル：
- **`s3.md`** - Amazon S3のストレージ、API、データ転送料金分析
- **`ec2.md`** - EC2インスタンス、Elastic IP、データ転送料金分析
- **`rds.md`** - データベースインスタンス、ストレージ、バックアップ料金分析
- **`lambda.md`** - Lambda関数実行、リクエスト料金分析
- **`cloudfront.md`** - CDN配信、HTTPSリクエスト料金分析
- **`ebs.md`** - EBSボリューム、スナップショット料金分析
- **`vpc.md`** - NATゲートウェイ、ネットワーク料金分析

その他、全22サービスに対応（API Gateway、DynamoDB、ElastiCache、Kinesis等）

### 🔧 カスタマイズ方法

#### 分析期間の変更
月のヘッダーを追加・変更することで異なる期間に対応：
```csv
サービス,費用項目,説明,費用（2025年1月）,費用（2025年2月）,費用（2025年3月）
```

#### 表示する費用項目数の変更
`simple_analyzer.py`内で以下を変更：
```python
# 表示する項目数を変更（現在：All + 上位3項目）
sorted_data = [all_item] + other_items[:5]  # 5項目に変更
```

#### 出力ディレクトリの変更
```python
output_docs_path = '../custom_output_directory'
```

## トラブルシューティング

1. **MCPサーバー接続エラー**
   ```bash
   claude mcp list
   # サーバーが ✓ Connected と表示されるか確認
   ```

2. **AWS権限エラー**
   - IAMロールに必要な権限が付与されているか確認
   - AWS認証情報が正しく設定されているか確認

3. **データ取得エラー**
   - 指定期間が有効な形式（YYYY-MM-DD）か確認
   - リージョン設定を確認

4. **Python実行エラー**
   - Python 3.7以上がインストールされているか確認
   - 外部ライブラリが必要な場合は仮想環境を作成

## データ品質保証

### データ検証チェックリスト

分析を開始する前に、以下の項目を必ず確認してください：

#### ✅ 必須チェック項目
1. **データソースの確認**
   - 既存のCSVファイルは使用しない
   - 必ずAWS Cost Explorerから直接データを取得

2. **金額の妥当性チェック**
   - 記載されている金額が現実的か
   - リソース数とコストの整合性
   - 前月比で極端な変動がないか

3. **データの整合性確認**
   - 複数ファイル間で同じ値が記載されているか
   - 日付フォーマットが統一されているか
   - 数値データが正しくフォーマットされているか

#### 🔍 具体的な検証方法

```bash
# 1. 実際のAWSコストデータを取得
aws ce get-cost-and-usage --time-period Start=2025-07-01,End=2025-08-01 \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# 2. データの妥当性を確認
# - 金額が現実的か
# - リソース数とコストの整合性
# - 前月比の変動が妥当か

# 3. 複数ソース間の整合性を確認
# - 同じサービスで異なる値が記載されていないか
# - 日付フォーマットが統一されているか
```

#### ❌ よくある間違い

1. **既存のCSVファイルを鵜呑みにする**
   - `output/`ディレクトリのファイルは参考用サンプル
   - 実際の分析には使用しない

2. **データの妥当性チェックを怠る**
   - 金額が現実的でないことに気づかない
   - リソース数とコストの整合性を確認しない

3. **複数データソースの整合性を確認しない**
   - 同じサービスで異なる値が記載されているのに気づかない
   - ファイル間の矛盾を放置する

#### ✅ 正しいアプローチ

1. **必ず実際のAWSデータを使用**
   - Cost Explorer APIから直接データを取得
   - 既存のファイルは参考用としてのみ使用

2. **データの妥当性を徹底チェック**
   - 金額の現実性
   - リソース数との整合性
   - 前月比の妥当性

3. **複数ソース間の整合性を確認**
   - ファイル間の矛盾がないかチェック
   - データフォーマットの統一性を確認