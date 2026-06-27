# -*- coding: utf-8 -*-
"""
Script 02: Extract NDB Psychiatric Prescription Data
=====================================================
Reads NDB Open Data prescription Excel files (outpatient / inpatient),
filters for psychiatric drug categories (hypnotics/anxiolytics,
psychotropics), and computes age-standardized rates per 100,000 population
for each of the 47 Japanese prefectures.

Inputs:
  - NDB Open Data No.10: 05_処方薬 / 【内服】外来（院外/院内）_都道府県別薬効分類別数量.xlsx
  - data/interim/psychiatric_drug_codes.csv  (from Script 01)

Outputs:
  - data/interim/psychiatric_prescriptions.csv  (N = 47 prefectures)

NOTE: NDB raw Excel files are NOT included in this repository.
Download from: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html

------------------------------------------------------------
NDB処方薬データ抽出スクリプト
精神科薬剤（催眠鎮静剤・抗不安剤、精神神経用剤）の都道府県別処方量算出
------------------------------------------------------------
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# プロジェクトルート設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT.parent.parent))

# NDBベースパス
NDB_BASE = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10")
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 処方薬データパス
PRESCRIPTION_BASE = NDB_BASE / "05_処方薬" / "01_公費レセプトを含まないデータ" / "01_処方薬（内服／外用／注射）"

# 対象ファイル（精神科薬剤は主に内服）
PRESCRIPTION_FILES = {
    "outpatient_out": PRESCRIPTION_BASE / "【内服】外来（院外）_都道府県別薬効分類別数量.xlsx",
    "outpatient_in": PRESCRIPTION_BASE / "【内服】外来（院内）_都道府県別薬効分類別数量.xlsx"
}

# 薬効分類コードファイル
DRUG_CODES_FILE = OUTPUT_DIR / "psychiatric_drug_codes.csv"

# 都道府県コードマッピング（JIS X 0401）
PREFECTURE_CODES = {
    '01': '北海道', '02': '青森県', '03': '岩手県', '04': '宮城県', '05': '秋田県',
    '06': '山形県', '07': '福島県', '08': '茨城県', '09': '栃木県', '10': '群馬県',
    '11': '埼玉県', '12': '千葉県', '13': '東京都', '14': '神奈川県', '15': '新潟県',
    '16': '富山県', '17': '石川県', '18': '福井県', '19': '山梨県', '20': '長野県',
    '21': '岐阜県', '22': '静岡県', '23': '愛知県', '24': '三重県', '25': '滋賀県',
    '26': '京都府', '27': '大阪府', '28': '兵庫県', '29': '奈良県', '30': '和歌山県',
    '31': '鳥取県', '32': '島根県', '33': '岡山県', '34': '広島県', '35': '山口県',
    '36': '徳島県', '37': '香川県', '38': '愛媛県', '39': '高知県', '40': '福岡県',
    '41': '佐賀県', '42': '長崎県', '43': '熊本県', '44': '大分県', '45': '宮崎県',
    '46': '鹿児島県', '47': '沖縄県'
}


def load_target_drug_codes():
    """
    対象薬効分類コードを読み込み

    Returns:
        list: 薬効分類名称のリスト
    """
    print("\n" + "="*60)
    print("対象薬効分類コードの読み込み")
    print("="*60 + "\n")

    if not DRUG_CODES_FILE.exists():
        print(f"[ERROR] 薬効分類コードファイルが見つかりません: {DRUG_CODES_FILE}")
        return None

    df_codes = pd.read_csv(DRUG_CODES_FILE, encoding='utf-8-sig')
    print(f"[OK] 薬効分類コード読み込み成功")
    print(f"   - 行数: {len(df_codes)}\n")

    # 対象薬効分類（催眠鎮静剤・抗不安剤、精神神経用剤）
    target_keywords = ['催眠鎮静剤', '抗不安剤', '精神神経用剤']

    # 薬効分類名称列を取得
    drug_col = df_codes.columns[0] if len(df_codes.columns) > 0 else None

    if drug_col is None:
        print("[ERROR] 薬効分類名称列が見つかりません")
        return None

    # 対象薬効分類を抽出
    target_codes = []
    for keyword in target_keywords:
        mask = df_codes[drug_col].str.contains(keyword, na=False)
        matched = df_codes[mask][drug_col].tolist()
        target_codes.extend(matched)

    target_codes = list(set(target_codes))  # 重複除去

    print(f"[INFO] 対象薬効分類:")
    for code in target_codes:
        print(f"   - {code}")
    print()

    return target_codes


def read_prescription_file(file_path, file_type):
    """
    NDB処方薬Excelファイルを読み込み

    Args:
        file_path: Excelファイルパス
        file_type: ファイル種別（outpatient_out, outpatient_in）

    Returns:
        DataFrame: 処方薬データ
    """
    print(f"\n[INFO] {file_type} データ読み込み中...")
    print(f"   - {file_path.name}")

    if not file_path.exists():
        print(f"[WARNING] ファイルが見つかりません: {file_path}")
        return None

    try:
        # NDB処方薬データはheader=[2,3]のMultiIndex
        df = pd.read_excel(file_path, header=[2, 3])
        print(f"[OK] 読み込み成功 (MultiIndex)")
        print(f"   - 行数: {len(df)}")
        print(f"   - 列数: {len(df.columns)}\n")

        return df

    except Exception as e:
        print(f"[ERROR] 読み込み失敗: {e}")
        return None


def extract_psychiatric_data(df, target_codes):
    """
    精神科薬剤データを抽出

    Args:
        df: 処方薬データ（MultiIndex columns）
        target_codes: 対象薬効分類リスト

    Returns:
        DataFrame: 抽出データ
    """
    print("[INFO] 精神科薬剤データ抽出中...")

    # MultiIndex構造から薬効分類名称列を探す
    drug_class_col = None
    for col in df.columns:
        # MultiIndexの第1レベルに'薬効分類名称'を含むか確認
        if isinstance(col, tuple):
            if '薬効分類名称' in str(col[0]):
                drug_class_col = col
                break
        else:
            if '薬効分類名称' in str(col):
                drug_class_col = col
                break

    if drug_class_col is None:
        print("[ERROR] 薬効分類名称列が見つかりません")
        print(f"[INFO] 利用可能な列（最初の5列）: {df.columns[:5].tolist()}")
        return None

    print(f"[FOUND] 薬効分類列: {drug_class_col}")

    # 欠損値を前方埋め（同じ薬効分類内の薬品を含める）
    df_filled = df.copy()
    df_filled[drug_class_col] = df_filled[drug_class_col].ffill()

    # データ型を文字列に変換
    df_filled[drug_class_col] = df_filled[drug_class_col].astype(str)

    # 対象薬効分類でフィルタ
    mask = df_filled[drug_class_col].isin(target_codes)
    df_psych = df_filled[mask].copy()

    print(f"[OK] 抽出完了: {len(df_psych)}行\n")

    return df_psych


def calculate_age_standardized_rate(df_psych):
    """
    年齢標準化処方量を算出（都道府県別）

    Args:
        df_psych: 精神科薬剤データ（MultiIndex columns）

    Returns:
        DataFrame: 都道府県別年齢標準化処方量
    """
    print("\n" + "="*60)
    print("年齢標準化処方量の算出")
    print("="*60 + "\n")

    print("[INFO] 列構造を確認中（MultiIndex）...")
    print(f"[INFO] カラム数: {len(df_psych.columns)}")

    # MultiIndex構造のサンプル出力
    print("\n[INFO] 先頭10列のカラム名:")
    for i, col in enumerate(df_psych.columns[:10]):
        print(f"   [{i}] {col}")
    print()

    # 都道府県別集計用辞書
    prefecture_data = {}

    # 各都道府県コードで処理
    for pref_code, pref_name in PREFECTURE_CODES.items():
        # MultiIndex構造で都道府県列を探す
        # 例: ('01', '北海道'), ('01', 'Unnamed: XX_level_1') など
        pref_cols = []
        for col in df_psych.columns:
            if isinstance(col, tuple):
                # 第1レベルが都道府県コード、または第2レベルが都道府県名
                if str(col[0]) == pref_code or pref_name in str(col[1]):
                    pref_cols.append(col)
            else:
                # 単一レベルの場合（念のため）
                if pref_code in str(col) or pref_name in str(col):
                    pref_cols.append(col)

        if len(pref_cols) == 0:
            # print(f"[WARNING] {pref_name} のデータが見つかりません")
            continue

        # 都道府県の処方量を合計（性別・年齢階級を統合）
        total_quantity = 0
        for col in pref_cols:
            values = pd.to_numeric(df_psych[col], errors='coerce')
            total_quantity += values.sum()

        prefecture_data[pref_code] = {
            'prefecture_name': pref_name,
            'total_quantity': total_quantity
        }

        print(f"[OK] {pref_name}: 処方量={total_quantity:,.0f}")

    # DataFrameに変換
    df_result = pd.DataFrame.from_dict(prefecture_data, orient='index')
    df_result.index.name = 'prefecture_code'
    df_result = df_result.reset_index()

    print(f"\n[OK] 都道府県別集計完了: {len(df_result)}都道府県\n")

    return df_result


def merge_multiple_files(prescription_files, target_codes):
    """
    複数の処方薬ファイルを統合

    Args:
        prescription_files: ファイルパス辞書
        target_codes: 対象薬効分類リスト

    Returns:
        DataFrame: 統合データ
    """
    print("\n" + "="*60)
    print("複数ファイルの統合処理")
    print("="*60 + "\n")

    all_results = []

    for file_type, file_path in prescription_files.items():
        print(f"\n[INFO] 処理中: {file_type}")
        print("-" * 60)

        # ファイル読み込み
        df = read_prescription_file(file_path, file_type)

        if df is None:
            continue

        # 精神科薬剤抽出
        df_psych = extract_psychiatric_data(df, target_codes)

        if df_psych is None or len(df_psych) == 0:
            continue

        # 年齢標準化処方量算出
        df_result = calculate_age_standardized_rate(df_psych)

        if df_result is not None and len(df_result) > 0:
            df_result['file_type'] = file_type
            all_results.append(df_result)

    if len(all_results) == 0:
        print("[ERROR] 統合するデータがありません")
        return None

    # 統合（都道府県別に処方量を合算）
    df_merged = pd.concat(all_results, ignore_index=True)

    df_final = df_merged.groupby(['prefecture_code', 'prefecture_name']).agg({
        'total_quantity': 'sum'
    }).reset_index()

    print("\n" + "="*60)
    print("[OK] 統合完了")
    print("="*60)
    print(f"   - 都道府県数: {len(df_final)}")
    print(f"   - 総処方量: {df_final['total_quantity'].sum():,.0f}\n")

    return df_final


def save_results(df_final):
    """
    結果を保存

    Args:
        df_final: 都道府県別処方量データ
    """
    print("\n" + "="*60)
    print("結果の保存")
    print("="*60 + "\n")

    output_file = OUTPUT_DIR / "psychiatric_prescriptions.csv"

    # 並び替え（都道府県コード順）
    df_final = df_final.sort_values('prefecture_code')

    # 保存
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"[OK] 保存完了: {output_file}")
    print(f"   - 行数: {len(df_final)}")
    print(f"   - 列数: {len(df_final.columns)}\n")

    # サンプル表示
    print("[INFO] 先頭10行:")
    print(df_final.head(10).to_string(index=False))
    print()


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print(" NDB処方薬データ抽出スクリプト")
    print("="*80)

    # 1. 対象薬効分類コード読み込み
    target_codes = load_target_drug_codes()

    if target_codes is None or len(target_codes) == 0:
        print("\n[ERROR] 対象薬効分類コードが見つかりません")
        return

    # 2. 複数ファイルを統合
    df_final = merge_multiple_files(PRESCRIPTION_FILES, target_codes)

    if df_final is None:
        print("\n[ERROR] データ抽出に失敗しました")
        return

    # 3. 結果保存
    save_results(df_final)

    print("="*80)
    print("[DONE] 全処理完了")
    print("="*80 + "\n")

    print("[INFO] 次のステップ:")
    print("   1. 出力ファイル確認:")
    print("      data/interim/psychiatric_prescriptions.csv")
    print()
    print("   2. 緑地率計算スクリプトの実行:")
    print("      python 03_Analysis/scripts/03_calculate_greenspace_ratio.py")
    print()


if __name__ == "__main__":
    main()
