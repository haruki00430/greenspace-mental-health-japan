# -*- coding: utf-8 -*-
"""
Script 05: Merge Final Analysis Dataset
========================================
Joins prescription data, greenspace ratios, and socioeconomic covariates
by prefecture code to create the final analysis dataset (N = 47 prefectures).
Applies KNN imputation for missing values where applicable.

Inputs:
  - data/interim/psychiatric_prescriptions.csv  (from Script 02)
  - data/interim/greenspace_ratio.csv           (from Script 03)
  - data/interim/socioeconomic_data.csv         (from Script 04)

Outputs:
  - data/processed/analysis_dataset.csv         (N = 47 × ~15 variables)
  - data/processed/analysis_dataset_per100k.csv (normalized per 100,000 pop)

------------------------------------------------------------
最終データセット統合スクリプト
処方薬・緑地率・調整変数を都道府県コードで結合し、解析データセットを生成
------------------------------------------------------------
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.impute import KNNImputer

# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 入力ファイル
INPUT_FILES = {
    'prescriptions': INTERIM_DIR / "psychiatric_prescriptions.csv",
    'greenspace': INTERIM_DIR / "greenspace_ratio.csv",
    'socioeconomic': INTERIM_DIR / "socioeconomic_data.csv"
}


def load_all_datasets():
    """
    全データセットを読み込み

    Returns:
        dict: データセット辞書
    """
    print("\n" + "="*60)
    print("データセット読み込み")
    print("="*60 + "\n")

    datasets = {}

    for key, file_path in INPUT_FILES.items():
        if not file_path.exists():
            print(f"[ERROR] ファイルが見つかりません: {file_path}")
            datasets[key] = None
            continue

        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"[OK] {key}: {len(df)}行 × {len(df.columns)}列")

            # カラム名表示
            print(f"   - カラム: {', '.join(df.columns[:5].tolist())}...")

            datasets[key] = df

        except Exception as e:
            print(f"[ERROR] 読み込み失敗 ({key}): {e}")
            datasets[key] = None

    print()

    return datasets


def merge_datasets(datasets):
    """
    データセットを統合

    Args:
        datasets: データセット辞書

    Returns:
        DataFrame: 統合データセット
    """
    print("\n" + "="*60)
    print("データセット統合")
    print("="*60 + "\n")

    # 必須データセットの確認
    required_keys = ['prescriptions', 'greenspace', 'socioeconomic']
    missing_keys = [key for key in required_keys if datasets.get(key) is None]

    if missing_keys:
        print(f"[ERROR] 必須データセットが不足: {', '.join(missing_keys)}")
        return None

    # 処方薬データを基準に結合
    df_merged = datasets['prescriptions'].copy()
    print(f"[INFO] 基準データセット: prescriptions ({len(df_merged)}行)")

    # 緑地率データを結合
    if datasets['greenspace'] is not None:
        df_merged = df_merged.merge(
            datasets['greenspace'],
            on='prefecture_code',
            how='left',
            suffixes=('', '_green')
        )
        print(f"[OK] 緑地率データ結合: {len(df_merged)}行")

    # 調整変数データを結合
    if datasets['socioeconomic'] is not None:
        df_merged = df_merged.merge(
            datasets['socioeconomic'],
            on='prefecture_code',
            how='left',
            suffixes=('', '_socio')
        )
        print(f"[OK] 調整変数データ結合: {len(df_merged)}行")

    # 重複列の削除
    duplicate_cols = [col for col in df_merged.columns if col.endswith('_green') or col.endswith('_socio')]

    if duplicate_cols:
        print(f"\n[INFO] 重複列を削除: {', '.join(duplicate_cols)}")
        df_merged = df_merged.drop(columns=duplicate_cols)

    # prefecture_name列の重複確認
    pref_name_cols = [col for col in df_merged.columns if 'prefecture_name' in col]
    if len(pref_name_cols) > 1:
        # 最初の列を残して他を削除
        df_merged = df_merged.drop(columns=pref_name_cols[1:])

    print(f"\n[OK] 統合完了: {len(df_merged)}行 × {len(df_merged.columns)}列\n")

    return df_merged


def handle_missing_values(df_merged):
    """
    欠損値処理（KNN補完）

    Args:
        df_merged: 統合データセット

    Returns:
        DataFrame: 欠損値処理後のデータセット
    """
    print("\n" + "="*60)
    print("欠損値処理")
    print("="*60 + "\n")

    # 欠損値の確認
    missing_counts = df_merged.isnull().sum()
    missing_vars = missing_counts[missing_counts > 0]

    if len(missing_vars) == 0:
        print("[OK] 欠損値なし\n")
        return df_merged

    print("[INFO] 欠損値が存在する変数:")
    for var, count in missing_vars.items():
        percentage = (count / len(df_merged)) * 100
        print(f"   - {var}: {count}件 ({percentage:.1f}%)")
    print()

    # 数値列のみ抽出
    numeric_cols = df_merged.select_dtypes(include=[np.number]).columns.tolist()

    # prefecture_codeとprefix_nameを除外
    impute_cols = [col for col in numeric_cols
                   if col not in ['prefecture_code'] and 'prefecture' not in col]

    if len(impute_cols) == 0:
        print("[WARNING] 補完対象の数値列がありません")
        return df_merged

    print(f"[INFO] KNN補完対象: {len(impute_cols)}変数")

    # KNN補完
    imputer = KNNImputer(n_neighbors=5)

    df_imputed = df_merged.copy()
    df_imputed[impute_cols] = imputer.fit_transform(df_merged[impute_cols])

    print("[OK] KNN補完完了\n")

    return df_imputed


def calculate_derived_variables(df):
    """
    派生変数を計算

    Args:
        df: データセット

    Returns:
        DataFrame: 派生変数追加後のデータセット
    """
    print("\n" + "="*60)
    print("派生変数の計算")
    print("="*60 + "\n")

    df_derived = df.copy()

    # 人口10万人あたり処方量の計算（簡易版）
    # ※実際には都道府県別人口データが必要
    if 'total_quantity' in df_derived.columns:
        # 暫定: 総処方量をそのまま使用（後で人口データと結合して補正）
        df_derived['prescription_per_100k'] = df_derived['total_quantity']
        print("[OK] 人口10万人あたり処方量（暫定値）")

    # 緑地率のカテゴリ化（四分位）
    if 'total_greenspace_ratio_percent' in df_derived.columns:
        # Note: greenspace_ratio_percent was renamed to total_greenspace_ratio_percent in 03_ analysis
        df_derived['greenspace_quartile'] = pd.qcut(
            df_derived['total_greenspace_ratio_percent'],
            q=4,
            labels=False, # Use False then map to handle varying number of bins if duplicates drop
            duplicates='drop'
        )
        # Map back to labels if we have 4 bins, otherwise just use numbers
        bins_count = df_derived['greenspace_quartile'].nunique()
        if bins_count == 4:
            df_derived['greenspace_quartile'] = df_derived['greenspace_quartile'].map({
                0: 'Q1_Low', 1: 'Q2_Medium-Low', 2: 'Q3_Medium-High', 3: 'Q4_High'
            })
        print("[OK] 緑地率カテゴリ作成")
    elif 'greenspace_ratio_percent' in df_derived.columns:
        df_derived['greenspace_quartile'] = pd.qcut(
            df_derived['greenspace_ratio_percent'],
            q=4,
            labels=False,
            duplicates='drop'
        )
        print("[OK] 緑地率カテゴリ作成")
        print("[OK] 緑地率四分位カテゴリ")

    print()

    return df_derived


def create_data_summary(df):
    """
    データサマリーを作成

    Args:
        df: 最終データセット
    """
    print("\n" + "="*60)
    print("データサマリー")
    print("="*60 + "\n")

    print(f"[INFO] 最終データセット:")
    print(f"   - 行数: {len(df)}")
    print(f"   - 列数: {len(df.columns)}\n")

    print("[INFO] 変数リスト:")
    for i, col in enumerate(df.columns, 1):
        dtype = df[col].dtype
        print(f"   [{i:2d}] {col:40s} ({dtype})")
    print()

    # 数値変数の基本統計量
    print("[INFO] 数値変数の基本統計量:")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_cols) > 0:
        print(df[numeric_cols].describe().to_string())
    print()


def save_results(df):
    """
    結果を保存

    Args:
        df: 最終データセット
    """
    print("\n" + "="*60)
    print("結果の保存")
    print("="*60 + "\n")

    output_file = OUTPUT_DIR / "analysis_dataset.csv"

    # 並び替え（都道府県コード順）
    df = df.sort_values('prefecture_code')

    # 保存
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"[OK] 保存完了: {output_file}")
    print(f"   - 行数: {len(df)}")
    print(f"   - 列数: {len(df.columns)}\n")

    # 先頭5行表示
    print("[INFO] 先頭5行:")
    print(df.head(5).to_string(index=False))
    print()


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print(" 最終データセット統合スクリプト")
    print("="*80)

    # 1. データセット読み込み
    datasets = load_all_datasets()

    # 2. データセット統合
    df_merged = merge_datasets(datasets)

    if df_merged is None:
        print("\n[ERROR] データセット統合に失敗しました")
        return

    # 3. 欠損値処理
    df_imputed = handle_missing_values(df_merged)

    # 4. 派生変数計算
    df_final = calculate_derived_variables(df_imputed)

    # 5. データサマリー作成
    create_data_summary(df_final)

    # 6. 結果保存
    save_results(df_final)

    print("="*80)
    print("[DONE] 全処理完了")
    print("="*80 + "\n")

    print("[INFO] Phase 1完了！")
    print()
    print("[INFO] 次のフェーズ:")
    print("   Phase 2: 記述統計・空間探索的分析")
    print("   - コロプレスマップ作成")
    print("   - Global Moran's I計算")
    print("   - 相関分析")
    print()
    print("[INFO] 最終データセット:")
    print("   - data/processed/analysis_dataset.csv")
    print()


if __name__ == "__main__":
    main()
