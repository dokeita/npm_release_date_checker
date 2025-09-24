#!/usr/bin/env python3
import json
import requests
import time
import sys
import os
from datetime import datetime


def get_all_packages(data, packages=None):
    """再帰的にすべてのパッケージとバージョンを取得"""
    if packages is None:
        packages = {}

    if isinstance(data, dict):
        if 'dependencies' in data:
            for name, info in data['dependencies'].items():
                if isinstance(info, dict) and 'version' in info:
                    packages[name] = info['version']
                get_all_packages(info, packages)
        elif 'version' in data:
            # ルートレベルのパッケージ
            pass

    return packages


def get_release_date(package_name, version):
    """npmレジストリからパッケージのバージョンリリース日を取得"""
    try:
        url = f"https://registry.npmjs.org/{package_name}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'time' in data and version in data['time']:
                return data['time'][version]

        return None
    except Exception as e:
        print(f"エラー: {package_name}@{version} - {e}")
        return None


def main():
    # コマンドライン引数の確認
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("使用方法: python3 get_release_dates.py <json_file> [UTC日時]")
        print("例: python3 get_release_dates.py test.json")
        print("例: python3 get_release_dates.py test.json 2023-01-01T00:00:00Z")
        sys.exit(1)

    json_file = sys.argv[1]
    filter_date = None

    if len(sys.argv) == 3:
        try:
            filter_date = datetime.fromisoformat(sys.argv[2].replace(
                'Z', '+00:00'))
        except ValueError:
            print(f"エラー: 日時形式が正しくありません: {sys.argv[2]}")
            print("形式: YYYY-MM-DDTHH:MM:SSZ")
            sys.exit(1)

    # ファイルの存在確認
    if not os.path.exists(json_file):
        print(f"エラー: ファイル '{json_file}' が見つかりません")
        sys.exit(1)

    # JSONファイルを読み込み
    with open(json_file, 'r', encoding='utf-8') as f:
        npm_data = json.load(f)

    # すべてのパッケージを取得
    packages = get_all_packages(npm_data)

    print(f"合計 {len(packages)} 個のパッケージが見つかりました")
    if filter_date:
        print(f"フィルタ日時: {filter_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 80)

    results = []
    newer_packages = []

    # outディレクトリを作成
    os.makedirs('out', exist_ok=True)

    # 結果をファイルにも出力
    with open('out/result.txt', 'w', encoding='utf-8') as result_file:
        result_file.write(f"合計 {len(packages)} 個のパッケージが見つかりました\n")
        if filter_date:
            result_file.write(
                f"フィルタ日時: {filter_date.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        result_file.write("=" * 80 + "\n")

    for i, (package_name, version) in enumerate(packages.items(), 1):
        print(f"[{i}/{len(packages)}] {package_name}@{version} を処理中...")

        # result.txtに追記
        with open('out/result.txt', 'a', encoding='utf-8') as result_file:
            result_file.write(
                f"[{i}/{len(packages)}] {package_name}@{version} を処理中...\n")

        release_date = get_release_date(package_name, version)

        if release_date:
            # ISO形式の日付を読みやすい形式に変換
            try:
                dt = datetime.fromisoformat(release_date.replace(
                    'Z', '+00:00'))
                formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except:
                formatted_date = release_date

            result = {
                'package': package_name,
                'version': version,
                'release_date': release_date,
                'formatted_date': formatted_date
            }

            results.append(result)

            # フィルタ日時より後のパッケージをチェック
            if filter_date and dt > filter_date:
                newer_packages.append(result)

            print(f"  リリース日: {formatted_date}")
            with open('out/result.txt', 'a', encoding='utf-8') as result_file:
                result_file.write(f"  リリース日: {formatted_date}\n")
        else:
            print(f"  リリース日: 取得できませんでした")
            with open('out/result.txt', 'a', encoding='utf-8') as result_file:
                result_file.write(f"  リリース日: 取得できませんでした\n")

        # APIレート制限を避けるため少し待機
        time.sleep(0.1)

    # 結果をJSONファイルに保存
    output_file = f"out/{os.path.splitext(os.path.basename(json_file))[0]}_release_dates.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # フィルタ日時より後のパッケージを別ファイルに保存
    if filter_date and newer_packages:
        newer_file = f"out/{os.path.splitext(os.path.basename(json_file))[0]}_newer_packages.json"
        with open(newer_file, 'w', encoding='utf-8') as f:
            json.dump(newer_packages, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"完了! 結果は {output_file} に保存されました")
    print(f"成功: {len(results)} 個のパッケージ")
    print(f"失敗: {len(packages) - len(results)} 個のパッケージ")

    # result.txtに最終結果を追記
    with open('out/result.txt', 'a', encoding='utf-8') as result_file:
        result_file.write("\n" + "=" * 80 + "\n")
        result_file.write(f"完了! 結果は {output_file} に保存されました\n")
        result_file.write(f"成功: {len(results)} 個のパッケージ\n")
        result_file.write(f"失敗: {len(packages) - len(results)} 個のパッケージ\n")

    if filter_date:
        print(f"フィルタ日時より後: {len(newer_packages)} 個のパッケージ")
        with open('out/result.txt', 'a', encoding='utf-8') as result_file:
            result_file.write(f"フィルタ日時より後: {len(newer_packages)} 個のパッケージ\n")
        if newer_packages:
            print(f"新しいパッケージは {newer_file} に保存されました")
            with open('out/result.txt', 'a', encoding='utf-8') as result_file:
                result_file.write(f"新しいパッケージは {newer_file} に保存されました\n")


if __name__ == "__main__":
    main()
