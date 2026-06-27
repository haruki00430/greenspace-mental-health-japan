# -*- coding: utf-8 -*-
"""
Script 01: Identify Psychiatric Drug Classification Codes
==========================================================
Reads NDB Open Data prescription Excel files and identifies the
drug classification codes (薬効分類) for psychiatric medications:
antidepressants, anxiolytics, and hypnotics/sedatives.

Inputs:
  - NDB Open Data No.10: 05_処方薬 / 【内服】外来（院外）_都道府県別薬効分類別数量.xlsx

Outputs:
  - data/interim/psychiatric_drug_codes.csv

NOTE: NDB raw Excel files are NOT included in this repository.
Download from: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html

------------------------------------------------------------
NDB処方薬データ：精神科薬剤の薬効分類コード特定スクリプト

機能:
1. NDB処方薬Excelファイルを読み込み
2. 薬効分類の構造を解析
3. 精神科関連薬剤（抗うつ薬、抗不安薬、睡眠薬）のコードを特定
4. 結果をCSVファイルとして出力

入力:
- 02_Data/raw/NDB_OpenData/No.10/05_処方薬/.../【内服】外来（院外）_都道府県別薬効分類別数量.xlsx

出力:
- data/interim/psychiatric_drug_codes.csv
------------------------------------------------------------
"""

import pandas as pd
from pathlib import Path

# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
NDB_BASE = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10")
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"

# NDB処方薬ファイルパス
PRESCRIPTION_FILE = NDB_BASE / "05_処方薬" / "01_公費レセプトを含まないデータ" / \
                    "01_処方薬（内服／外用／注射）" / "【内服】外来（院外）_都道府県別薬効分類別数量.xlsx"

def explore_file_structure():
    """
    Excelファイルの構造を探索
    """
    print("\n" + "="*60)
    print("NDB処方薬データ構造の探索")
    print("="*60 + "\n")

    if not PRESCRIPTION_FILE.exists():
        print(f"[ERROR] ファイルが見つかりません: {PRESCRIPTION_FILE}")
        return None

    print(f"[INFO] ファイル読み込み中...")
    print(f"   - {PRESCRIPTION_FILE.name}\n")

    # ヘッダー行の確認（最初の10行）
    df_header = pd.read_excel(PRESCRIPTION_FILE, nrows=10)
    print("[INFO] ファイルの先頭10行（ヘッダー構造確認）:")
    print(df_header.head())
    print()

    # 薬効分類列の探索
    print("[INFO] カラム名:")
    for i, col in enumerate(df_header.columns):
        print(f"   [{i}] {col}")
    print()

    return df_header


def read_prescription_data():
    """
    処方薬データを適切なヘッダー設定で読み込み
    """
    print("\n" + "="*60)
    print("処方薬データの読み込み")
    print("="*60 + "\n")

    # NDB処方薬データは通常header=[2,3]のMultiIndex
    # まずheader=2で試す
    try:
        df = pd.read_excel(PRESCRIPTION_FILE, header=2)
        print(f"[OK] データ読み込み成功 (header=2)")
        print(f"   - 行数: {len(df)}")
        print(f"   - 列数: {len(df.columns)}\n")

        # カラム名の確認
        print("[INFO] カラム名（最初の10列）:")
        for i, col in enumerate(df.columns[:10]):
            print(f"   [{i}] {col}")
        print()

        return df

    except Exception as e:
        print(f"[ERROR] 読み込み失敗: {e}")
        return None


def identify_psychiatric_drugs(df):
    """
    精神科薬剤を特定

    薬効分類番号（想定）:
    - 117: 精神神経用剤（総称）
    - 1171: 抗うつ薬
    - 1172: 抗不安薬
    - 1174: 睡眠薬
    """
    print("\n" + "="*60)
    print("精神科薬剤の特定")
    print("="*60 + "\n")

    # 薬効分類列を探す
    drug_class_col = None
    drug_name_col = None

    for col in df.columns:
        col_str = str(col).lower()
        if '薬効' in col_str or 'drug' in col_str or '分類' in col_str:
            drug_class_col = col
            print(f"[FOUND] 薬効分類列: {col}")

        if '名称' in col_str or 'name' in col_str or '薬剤' in col_str:
            drug_name_col = col
            print(f"[FOUND] 薬剤名列: {col}")

    if drug_class_col is None:
        print("[WARNING] 薬効分類列が見つかりません。")
        print("[INFO] 全カラムを表示します：")
        for i, col in enumerate(df.columns):
            print(f"   [{i}] {col}")
        return None

    print()

    # 精神科関連薬効分類コードで絞り込み
    psychiatric_keywords = [
        '精神', '神経', '抗うつ', '抗不安', '睡眠', '催眠',
        'psychiatric', 'antidepressant', 'anxiolytic', 'hypnotic'
    ]

    # データ型を文字列に変換
    df[drug_class_col] = df[drug_class_col].astype(str)

    # キーワードマッチ
    psychiatric_mask = df[drug_class_col].str.contains(
        '|'.join(psychiatric_keywords),
        case=False,
        na=False
    )

    psychiatric_drugs = df[psychiatric_mask]

    print(f"[INFO] 精神科関連薬剤候補: {len(psychiatric_drugs)}件\n")

    if len(psychiatric_drugs) > 0:
        print("[INFO] サンプル（先頭10件）:")
        display_cols = [drug_class_col]
        if drug_name_col:
            display_cols.append(drug_name_col)

        print(psychiatric_drugs[display_cols].head(10))
        print()

    return psychiatric_drugs, drug_class_col, drug_name_col


def save_drug_codes(psychiatric_drugs, drug_class_col, drug_name_col):
    """
    薬効分類コードをCSVとして保存
    """
    print("\n" + "="*60)
    print("薬効分類コード保存")
    print("="*60 + "\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 薬効分類コードを抽出
    if psychiatric_drugs is None or len(psychiatric_drugs) == 0:
        print("[WARNING] 保存するデータがありません")
        return

    output_file = OUTPUT_DIR / "psychiatric_drug_codes.csv"

    # 保存
    save_cols = [drug_class_col]
    if drug_name_col:
        save_cols.append(drug_name_col)

    psychiatric_drugs[save_cols].to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"[OK] 保存完了: {output_file}")
    print(f"   - 行数: {len(psychiatric_drugs)}\n")


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print(" NDB処方薬データ：精神科薬剤コード特定")
    print("="*80)

    # ファイル構造の探索
    df_header = explore_file_structure()

    if df_header is None:
        print("\n[ERROR] ファイル構造の探索に失敗しました")
        return

    # 処方薬データの読み込み
    df = read_prescription_data()

    if df is None:
        print("\n[ERROR] データ読み込みに失敗しました")
        return

    # 精神科薬剤の特定
    result = identify_psychiatric_drugs(df)

    if result is None:
        print("\n[ERROR] 精神科薬剤の特定に失敗しました")
        return

    psychiatric_drugs, drug_class_col, drug_name_col = result

    # 薬効分類コードの保存
    save_drug_codes(psychiatric_drugs, drug_class_col, drug_name_col)

    print("="*80)
    print("[DONE] 全処理完了")
    print("="*80 + "\n")

    print("[INFO] 次のステップ:")
    print("   1. 出力ファイルを確認:")
    print("      data/interim/psychiatric_drug_codes.csv")
    print()
    print("   2. 薬効分類コードを確認し、Phase 1データ抽出へ進む")
    print()


if __name__ == "__main__":
    main()
