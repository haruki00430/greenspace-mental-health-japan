"""
L03-b土地利用データ抽出スクリプト（全年度対応版）

機能:
1. L03-b-21（2021年）、L03-b-16（2016年）、L03-b-06（2006年）を抽出
2. プロジェクト専用フォルダにコピー
3. メッシュコード別に最新年度を優先的に使用
4. ファイル一覧と統計情報を出力

データ優先順位:
- 第1優先: L03-b-21（2021年）- 関東・中部・近畿・中国・四国・九州
- 第2優先: L03-b-16（2016年）- 東北・北海道
- 第3優先: L03-b-06（2006年）- 離島・一部地域

入力:
- 02_Data/raw/MLIT/L03_b_Land_Use

出力:
- projects/NDB_XXX_greenspace_mental_health/data/raw/L03_b_Land_Use_All/
"""

import os
import shutil
from pathlib import Path
import glob
from collections import defaultdict

# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
SOURCE_DIR = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\MLIT\L03_b_Land_Use")
TARGET_DIR = PROJECT_ROOT / "data" / "raw" / "L03_b_Land_Use_All"


def create_target_directory():
    """ターゲットディレクトリを作成"""
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ ターゲットディレクトリ作成: {TARGET_DIR}")


def extract_all_l03_b_files():
    """
    L03-b全年度のファイルを抽出（最新年度を優先）

    Returns:
        dict: {メッシュコード: (年度, ファイルパス)}
    """
    print("\n" + "="*60)
    print("L03-b土地利用データ抽出開始（全年度対応）")
    print("="*60 + "\n")

    # ソースディレクトリの確認
    if not SOURCE_DIR.exists():
        print(f"❌ ソースディレクトリが存在しません: {SOURCE_DIR}")
        return {}

    # 全L03-bファイルを検索
    patterns = [
        "L03-b-21_*.zip",  # 2021年
        "L03-b-16_*.zip",  # 2016年
        "L03-b-06_*.zip"   # 2006年
    ]

    all_files = []
    for pattern in patterns:
        files = glob.glob(str(SOURCE_DIR / pattern))
        all_files.extend(files)

    if not all_files:
        print(f"❌ L03-bファイルが見つかりません")
        return {}

    print(f"📁 検出したL03-bファイル総数: {len(all_files)}\n")

    # 年度別の集計
    files_by_year = defaultdict(list)
    for file_path in all_files:
        filename = Path(file_path).name
        # L03-b-21_5339-jgd_GML.zip → 21
        year_code = filename.split('_')[0].split('-')[-1]
        files_by_year[year_code].append(file_path)

    print("📊 年度別ファイル数:")
    for year_code in sorted(files_by_year.keys()):
        count = len(files_by_year[year_code])
        year_name = {"06": "2006年", "16": "2016年", "21": "2021年"}.get(year_code, f"20{year_code}年")
        print(f"   - L03-b-{year_code} ({year_name}): {count}ファイル")
    print()

    # メッシュコード別に最新年度を選択
    mesh_to_file = {}

    for file_path in all_files:
        filename = Path(file_path).name
        # ファイル名からメッシュコードと年度を抽出
        # L03-b-21_5339-jgd_GML.zip → year=21, mesh=5339
        parts = filename.split('_')
        year_code = parts[0].split('-')[-1]  # "21"
        mesh_code = parts[1].split('-')[0]   # "5339"

        # 既存のメッシュコードがあるか確認
        if mesh_code in mesh_to_file:
            # より新しい年度を優先
            existing_year = mesh_to_file[mesh_code][0]
            if year_code > existing_year:
                mesh_to_file[mesh_code] = (year_code, file_path)
        else:
            mesh_to_file[mesh_code] = (year_code, file_path)

    print(f"🗺️  ユニークなメッシュコード数: {len(mesh_to_file)}\n")

    # ファイルをコピー
    copied_files = []
    total_size = 0
    year_stats = defaultdict(int)

    for mesh_code, (year_code, source_file) in sorted(mesh_to_file.items()):
        source_path = Path(source_file)
        target_path = TARGET_DIR / source_path.name

        # 既存ファイルのスキップ
        if target_path.exists():
            print(f"⏭️  スキップ（既存）: {source_path.name}")
            copied_files.append((mesh_code, year_code, target_path))
            total_size += target_path.stat().st_size
            year_stats[year_code] += 1
            continue

        # コピー実行
        try:
            shutil.copy2(source_path, target_path)
            file_size = target_path.stat().st_size
            total_size += file_size

            year_name = {"06": "2006年", "16": "2016年", "21": "2021年"}.get(year_code, f"20{year_code}年")
            print(f"✅ コピー完了: {source_path.name} ({year_name}, {file_size / 1024 / 1024:.2f} MB)")
            copied_files.append((mesh_code, year_code, target_path))
            year_stats[year_code] += 1

        except Exception as e:
            print(f"❌ コピー失敗: {source_path.name} - {e}")

    print(f"\n✅ 抽出完了: {len(copied_files)}ファイル")
    print(f"💾 合計サイズ: {total_size / 1024 / 1024 / 1024:.2f} GB\n")

    # 使用年度の統計
    print("📊 使用年度別ファイル数:")
    for year_code in sorted(year_stats.keys()):
        year_name = {"06": "2006年", "16": "2016年", "21": "2021年"}.get(year_code, f"20{year_code}年")
        count = year_stats[year_code]
        percentage = count / len(copied_files) * 100
        print(f"   - {year_name}: {count}ファイル ({percentage:.1f}%)")
    print()

    return copied_files


def analyze_files(file_list):
    """
    ファイルの統計情報を出力

    Args:
        file_list: [(メッシュコード, 年度, ファイルパス), ...]
    """
    print("\n" + "="*60)
    print("ファイル統計情報")
    print("="*60 + "\n")

    # メッシュコード分析
    mesh_codes = [mesh for mesh, _, _ in file_list]
    print(f"📊 ユニークメッシュコード数: {len(set(mesh_codes))}")
    print(f"📁 総ファイル数: {len(file_list)}\n")

    # メッシュコードの範囲
    if mesh_codes:
        mesh_codes_sorted = sorted(set(mesh_codes))
        print(f"🗺️  メッシュコード範囲:")
        print(f"   - 最小: {mesh_codes_sorted[0]}")
        print(f"   - 最大: {mesh_codes_sorted[-1]}")
        print(f"   - サンプル: {', '.join(mesh_codes_sorted[:5])}...\n")

    # 年度別統計
    year_counts = defaultdict(int)
    for _, year_code, _ in file_list:
        year_counts[year_code] += 1

    print("📅 年度別内訳:")
    for year_code in sorted(year_counts.keys()):
        year_name = {"06": "2006年", "16": "2016年", "21": "2021年"}.get(year_code, f"20{year_code}年")
        count = year_counts[year_code]
        percentage = count / len(file_list) * 100
        print(f"   - {year_name}: {count}ファイル ({percentage:.1f}%)")
    print()

    # ファイルサイズ統計
    sizes = [fp.stat().st_size for _, _, fp in file_list]
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
        file_list: [(メッシュコード, 年度, ファイルパス), ...]
    """
    import csv

    output_path = TARGET_DIR.parent.parent / "interim" / "land_use_file_list.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['mesh_code', 'year_code', 'year_name', 'filename', 'file_size_mb', 'file_path'])

        for mesh_code, year_code, file_path in sorted(file_list):
            filename = file_path.name
            year_name = {"06": "2006年", "16": "2016年", "21": "2021年"}.get(year_code, f"20{year_code}年")
            size_mb = file_path.stat().st_size / 1024 / 1024

            writer.writerow([mesh_code, year_code, year_name, filename, f"{size_mb:.2f}", str(file_path)])

    print(f"📄 ファイル一覧を保存: {output_path}\n")


def create_data_quality_note():
    """
    データ品質に関する注記を作成
    """
    note_path = TARGET_DIR / "DATA_QUALITY_NOTE.md"

    content = """# L03-b土地利用データ品質に関する注記

**作成日**: 2026年2月22日

## データ年度の混在について

本研究では、国土数値情報L03-b（土地利用細分メッシュ）の複数年度データを組み合わせて使用しています。

### 年度選択の基準

各メッシュについて、以下の優先順位で最新のデータを採用：

1. **第1優先**: L03-b-21（令和3年、2021年）
   - 主に関東、中部、近畿、中国、四国、九州地方
   - NDB第10回（令和2年度、2020年）と時期的に最も近い

2. **第2優先**: L03-b-16（平成28年、2016年）
   - 主に東北地方、北海道
   - 2021年データが未公開の地域

3. **第3優先**: L03-b-06（平成18年、2006年）
   - 主に離島・一部島嶼部
   - より新しいデータが存在しない地域

### データ品質への影響

#### 土地利用の安定性
- **森林・公園**: 短期間（5-15年）での大きな変化は少ない
- **田畑**: 耕作放棄地の増加などの変化はあるが、都道府県レベルでは影響軽微
- **都市化**: 人口減少地域では都市化の進行が鈍化

#### 都道府県単位での影響評価
- 本研究は**都道府県単位（N=47）**での解析
- メッシュレベルの年度差は、都道府県集計時に平滑化される
- 緑地率の都道府県順位に大きな影響を与える可能性は低い

### 年度差の許容性

#### 先行研究の例
- 土地利用変化研究では、5年程度の時期差は許容されることが多い
- 本研究の目的は「緑地率の地域差」であり、「経年変化」ではない

#### 感度分析
- Phase 4（感度分析）で、年度別データの影響を検討
- 2021年データのみの都道府県で別途解析し、結果の頑健性を確認

### 研究の限界

以下を論文のLimitationsセクションに明記：
1. 土地利用データの年度が2006-2021年と幅がある
2. 一部地域（東北、北海道、離島）では2016年または2006年データを使用
3. 都道府県レベルの集計により、メッシュレベルの時期差の影響は軽減される見込み

---

**結論**: データ年度の混在は本研究の限界として明記するが、都道府県単位の解析では影響は限定的と考えられる。
"""

    with open(note_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"📝 データ品質注記を作成: {note_path}\n")


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print(" L03-b土地利用データ抽出スクリプト（全年度対応版）")
    print("="*80 + "\n")

    # ターゲットディレクトリ作成
    create_target_directory()

    # 全年度L03-bファイル抽出
    copied_files = extract_all_l03_b_files()

    if not copied_files:
        print("❌ 抽出に失敗しました。")
        return

    # 統計情報出力
    analyze_files(copied_files)

    # ファイル一覧CSV作成
    create_file_list_csv(copied_files)

    # データ品質注記作成
    create_data_quality_note()

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
    print("   3. データ品質注記の確認:")
    print(f"      {TARGET_DIR / 'DATA_QUALITY_NOTE.md'}")
    print()


if __name__ == "__main__":
    main()
