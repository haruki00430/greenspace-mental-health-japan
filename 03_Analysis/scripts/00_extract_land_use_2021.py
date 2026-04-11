"""
L03-b-21（令和3年版）土地利用データ抽出スクリプト

機能:
1. 既存のMLITフォルダからL03-b-21ファイルのみを抽出
2. プロジェクト専用フォルダにコピー
3. ファイル一覧と統計情報を出力

入力:
- C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\MLIT\L03_b_Land_Use

出力:
- projects/NDB_XXX_greenspace_mental_health/data/raw/L03_b_Land_Use_2021/
"""

import os
import shutil
from pathlib import Path
import glob

# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_DIR = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\MLIT\L03_b_Land_Use")
TARGET_DIR = PROJECT_ROOT / "data" / "raw" / "L03_b_Land_Use_2021"


def create_target_directory():
    """ターゲットディレクトリを作成"""
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ ターゲットディレクトリ作成: {TARGET_DIR}")


def extract_l03_b_21_files():
    """
    L03-b-21ファイルのみを抽出してコピー

    Returns:
        List[Path]: コピーしたファイルのリスト
    """
    print("\n" + "="*60)
    print("L03-b-21（令和3年版）ファイル抽出開始")
    print("="*60 + "\n")

    # ソースディレクトリの確認
    if not SOURCE_DIR.exists():
        print(f"❌ ソースディレクトリが存在しません: {SOURCE_DIR}")
        return []

    # L03-b-21ファイルを検索
    pattern = str(SOURCE_DIR / "L03-b-21_*.zip")
    source_files = glob.glob(pattern)

    if not source_files:
        print(f"❌ L03-b-21ファイルが見つかりません: {pattern}")
        return []

    print(f"📁 検出したL03-b-21ファイル数: {len(source_files)}\n")

    # ファイルをコピー
    copied_files = []
    total_size = 0

    for source_file in sorted(source_files):
        source_path = Path(source_file)
        target_path = TARGET_DIR / source_path.name

        # 既存ファイルのスキップ
        if target_path.exists():
            print(f"⏭️  スキップ（既存）: {source_path.name}")
            copied_files.append(target_path)
            total_size += target_path.stat().st_size
            continue

        # コピー実行
        try:
            shutil.copy2(source_path, target_path)
            file_size = target_path.stat().st_size
            total_size += file_size

            print(f"✅ コピー完了: {source_path.name} ({file_size / 1024 / 1024:.2f} MB)")
            copied_files.append(target_path)

        except Exception as e:
            print(f"❌ コピー失敗: {source_path.name} - {e}")

    print(f"\n✅ 抽出完了: {len(copied_files)}ファイル")
    print(f"💾 合計サイズ: {total_size / 1024 / 1024 / 1024:.2f} GB\n")

    return copied_files


def analyze_files(file_list):
    """
    ファイルの統計情報を出力

    Args:
        file_list: ファイルパスのリスト
    """
    print("\n" + "="*60)
    print("ファイル統計情報")
    print("="*60 + "\n")

    # メッシュコードを抽出
    mesh_codes = []
    for file_path in file_list:
        # L03-b-21_5339-jgd_GML.zip → 5339
        filename = file_path.stem  # 拡張子を除く
        parts = filename.split('_')
        if len(parts) >= 2:
            mesh_code = parts[1].split('-')[0]  # "5339-jgd" → "5339"
            mesh_codes.append(mesh_code)

    print(f"📊 メッシュコード数: {len(set(mesh_codes))}種類")
    print(f"📁 総ファイル数: {len(file_list)}\n")

    # メッシュコードの範囲
    if mesh_codes:
        mesh_codes_sorted = sorted(set(mesh_codes))
        print(f"🗺️  メッシュコード範囲:")
        print(f"   - 最小: {mesh_codes_sorted[0]}")
        print(f"   - 最大: {mesh_codes_sorted[-1]}")
        print(f"   - サンプル: {', '.join(mesh_codes_sorted[:5])}...\n")

    # ファイルサイズ統計
    sizes = [f.stat().st_size for f in file_list]
    if sizes:
        print(f"💾 ファイルサイズ統計:")
        print(f"   - 平均: {sum(sizes) / len(sizes) / 1024 / 1024:.2f} MB")
        print(f"   - 最小: {min(sizes) / 1024 / 1024:.2f} MB")
        print(f"   - 最大: {max(sizes) / 1024 / 1024:.2f} MB")
        print(f"   - 合計: {sum(sizes) / 1024 / 1024 / 1024:.2f} GB\n")


def create_file_list_csv(file_list):
    """
    ファイル一覧をCSV形式で保存

    Args:
        file_list: ファイルパスのリスト
    """
    import csv

    output_path = TARGET_DIR.parent.parent / "interim" / "land_use_file_list.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'mesh_code', 'file_size_mb', 'file_path'])

        for file_path in sorted(file_list):
            filename = file_path.name
            # メッシュコード抽出
            parts = file_path.stem.split('_')
            mesh_code = parts[1].split('-')[0] if len(parts) >= 2 else 'N/A'
            # ファイルサイズ
            size_mb = file_path.stat().st_size / 1024 / 1024

            writer.writerow([filename, mesh_code, f"{size_mb:.2f}", str(file_path)])

    print(f"📄 ファイル一覧を保存: {output_path}\n")


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print(" L03-b-21（令和3年版）土地利用データ抽出スクリプト")
    print("="*80 + "\n")

    # ターゲットディレクトリ作成
    create_target_directory()

    # L03-b-21ファイル抽出
    copied_files = extract_l03_b_21_files()

    if not copied_files:
        print("❌ 抽出に失敗しました。")
        return

    # 統計情報出力
    analyze_files(copied_files)

    # ファイル一覧CSV作成
    create_file_list_csv(copied_files)

    print("="*80)
    print("✅ 全処理完了！")
    print("="*80 + "\n")

    print("📌 次のステップ:")
    print("   1. 緑地率計算スクリプトの実行:")
    print("      python 03_Analysis/scripts/01_greenspace_calculation.py")
    print()
    print(f"   2. データ所在:")
    print(f"      {TARGET_DIR}")
    print()


if __name__ == "__main__":
    main()
