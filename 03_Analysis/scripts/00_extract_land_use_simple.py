# -*- coding: utf-8 -*-
"""
L03-b土地利用データ抽出スクリプト（簡易版・絵文字なし）
"""

import shutil
from pathlib import Path
import glob
from collections import defaultdict

# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_DIR = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\MLIT\L03_b_Land_Use")
TARGET_DIR = PROJECT_ROOT / "data" / "raw" / "L03_b_Land_Use_All"

def main():
    print("\n" + "="*60)
    print("L03-b土地利用データ抽出開始")
    print("="*60 + "\n")

    # ターゲットディレクトリ作成
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[OK] ターゲットディレクトリ作成: {TARGET_DIR}\n")

    # ソースディレクトリ確認
    if not SOURCE_DIR.exists():
        print(f"[ERROR] ソースディレクトリが存在しません: {SOURCE_DIR}")
        return

    # 全L03-bファイルを検索
    patterns = ["L03-b-21_*.zip", "L03-b-16_*.zip", "L03-b-06_*.zip"]
    all_files = []
    for pattern in patterns:
        files = glob.glob(str(SOURCE_DIR / pattern))
        all_files.extend(files)

    if not all_files:
        print("[ERROR] L03-bファイルが見つかりません")
        return

    print(f"[INFO] 検出したL03-bファイル総数: {len(all_files)}\n")

    # 年度別の集計
    files_by_year = defaultdict(list)
    for file_path in all_files:
        filename = Path(file_path).name
        year_code = filename.split('_')[0].split('-')[-1]
        files_by_year[year_code].append(file_path)

    print("[INFO] 年度別ファイル数:")
    for year_code in sorted(files_by_year.keys()):
        count = len(files_by_year[year_code])
        year_name = {"06": "2006年", "16": "2016年", "21": "2021年"}.get(year_code, f"20{year_code}年")
        print(f"   - L03-b-{year_code} ({year_name}): {count}ファイル")
    print()

    # メッシュコード別に最新年度を選択
    mesh_to_file = {}
    for file_path in all_files:
        filename = Path(file_path).name
        parts = filename.split('_')
        year_code = parts[0].split('-')[-1]
        mesh_code = parts[1].split('-')[0]

        if mesh_code in mesh_to_file:
            existing_year = mesh_to_file[mesh_code][0]
            if year_code > existing_year:
                mesh_to_file[mesh_code] = (year_code, file_path)
        else:
            mesh_to_file[mesh_code] = (year_code, file_path)

    print(f"[INFO] ユニークなメッシュコード数: {len(mesh_to_file)}\n")

    # ファイルをコピー
    copied_count = 0
    skipped_count = 0
    total_size = 0
    year_stats = defaultdict(int)

    for mesh_code, (year_code, source_file) in sorted(mesh_to_file.items()):
        source_path = Path(source_file)
        target_path = TARGET_DIR / source_path.name

        if target_path.exists():
            print(f"[SKIP] {source_path.name}")
            skipped_count += 1
            total_size += target_path.stat().st_size
            year_stats[year_code] += 1
            continue

        try:
            shutil.copy2(source_path, target_path)
            file_size = target_path.stat().st_size
            total_size += file_size

            year_name = {"06": "2006年", "16": "2016年", "21": "2021年"}.get(year_code, f"20{year_code}年")
            print(f"[COPY] {source_path.name} ({year_name}, {file_size / 1024 / 1024:.2f} MB)")
            copied_count += 1
            year_stats[year_code] += 1

        except Exception as e:
            print(f"[ERROR] {source_path.name} - {e}")

    print(f"\n[OK] 抽出完了: {copied_count + skipped_count}ファイル")
    print(f"   - コピー: {copied_count}ファイル")
    print(f"   - スキップ: {skipped_count}ファイル")
    print(f"   - 合計サイズ: {total_size / 1024 / 1024 / 1024:.2f} GB\n")

    # 使用年度の統計
    print("[INFO] 使用年度別ファイル数:")
    for year_code in sorted(year_stats.keys()):
        year_name = {"06": "2006年", "16": "2016年", "21": "2021年"}.get(year_code, f"20{year_code}年")
        count = year_stats[year_code]
        percentage = count / (copied_count + skipped_count) * 100
        print(f"   - {year_name}: {count}ファイル ({percentage:.1f}%)")

    print("\n" + "="*60)
    print("[DONE] 全処理完了")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
