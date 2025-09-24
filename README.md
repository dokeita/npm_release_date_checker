# NPM Package Release Date Checker

npm依存関係のリリース日を取得し、指定日時でフィルタリングするツール

## 使用方法

```bash
# 基本実行
uv run python get_release_dates.py <json_file>

# 日時フィルタ付き実行
uv run python get_release_dates.py <json_file> <UTC日時>
```

## 例

```bash
# test.jsonの全パッケージのリリース日を取得
uv run python get_release_dates.py test.json

# 2023年1月1日以降にリリースされたパッケージを抽出
uv run python get_release_dates.py test.json 2023-01-01T00:00:00Z
```

## 出力ファイル
- out ディレクトリ配下に格納されます。
- `<入力ファイル名>_release_dates.json` - 全パッケージのリリース日
- `<入力ファイル名>_newer_packages.json` - フィルタ日時より後のパッケージ（フィルタ指定時のみ）
- `result.txt` - 実行ログ
