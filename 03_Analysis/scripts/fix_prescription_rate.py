# -*- coding: utf-8 -*-
"""
処方率の修正スクリプト

問題点:
- 現在の prescription_per_100k は total_quantity と同一（人口正規化なし）
- 正しい処方率 = (total_quantity / total_pop) * 100000

修正内容:
1. total_quantity の単位を明確化
2. 人口10万人あたり処方量を正しく計算
3. 修正後のデータセットを保存

入力:
- data/processed/analysis_dataset.csv

出力:
- data/processed/analysis_dataset_corrected.csv
- docs/prescription_rate_correction_report.md（修正レポート）
"""

import pandas as pd
import numpy as np
from pathlib import Path

# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = DATA_DIR / "analysis_dataset.csv"
OUTPUT_FILE = DATA_DIR / "analysis_dataset_corrected.csv"
REPORT_FILE = DOCS_DIR / "prescription_rate_correction_report.md"


def load_data():
    """
    データを読み込み

    Returns:
        DataFrame: 元データ
    """
    print("\n" + "="*80)
    print(" 処方率修正スクリプト")
    print("="*80 + "\n")

    print(f"[INFO] データ読み込み: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        print(f"[ERROR] ファイルが見つかりません: {INPUT_FILE}")
        return None

    df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')

    print(f"[OK] 読み込み成功")
    print(f"   - 行数: {len(df)}")
    print(f"   - 列数: {len(df.columns)}\n")

    return df


def analyze_current_data(df):
    """
    現在のデータを分析

    Args:
        df: データセット

    Returns:
        dict: 分析結果
    """
    print("\n" + "="*80)
    print(" 現在のデータ分析")
    print("="*80 + "\n")

    # 必須列の確認
    required_cols = ['total_quantity', 'total_pop', 'prescription_per_100k']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"[ERROR] 必須列が不足: {', '.join(missing_cols)}")
        return None

    # 現在の prescription_per_100k と total_quantity の比較
    print("[INFO] prescription_per_100k と total_quantity の比較:")
    comparison = df[['prefecture_name', 'total_quantity', 'prescription_per_100k', 'total_pop']].head(5)
    print(comparison.to_string(index=False))
    print()

    # 一致度チェック
    is_identical = np.allclose(df['total_quantity'], df['prescription_per_100k'], rtol=1e-5)

    if is_identical:
        print("[PROBLEM] prescription_per_100k は total_quantity と同一（人口正規化なし）\n")
    else:
        print("[OK] prescription_per_100k は total_quantity と異なる（既に正規化済み）\n")

    # 統計量
    print("[INFO] 現在の prescription_per_100k の統計量:")
    print(df['prescription_per_100k'].describe())
    print()

    analysis = {
        'is_identical': is_identical,
        'mean_quantity': df['total_quantity'].mean(),
        'mean_pop': df['total_pop'].mean(),
        'mean_prescription_per_100k_old': df['prescription_per_100k'].mean()
    }

    return analysis


def calculate_correct_rate(df):
    """
    正しい処方率を計算

    Args:
        df: データセット

    Returns:
        DataFrame: 修正後のデータセット
    """
    print("\n" + "="*80)
    print(" 正しい処方率の計算")
    print("="*80 + "\n")

    df_corrected = df.copy()

    # 古い列を削除
    if 'prescription_per_100k' in df_corrected.columns:
        df_corrected = df_corrected.drop(columns=['prescription_per_100k'])
        print("[INFO] 古い prescription_per_100k 列を削除")

    # 正しい処方率を計算
    df_corrected['prescription_per_100k'] = (df_corrected['total_quantity'] / df_corrected['total_pop']) * 100000

    print("[OK] 新しい処方率を計算:")
    print("   prescription_per_100k = (total_quantity / total_pop) × 100,000\n")

    # 結果表示（上位5都道府県）
    print("[INFO] 修正後の処方率（上位5都道府県）:")
    result = df_corrected[['prefecture_name', 'total_quantity', 'total_pop', 'prescription_per_100k']].copy()
    result = result.sort_values('prescription_per_100k', ascending=False).head(5)
    print(result.to_string(index=False))
    print()

    # 統計量
    print("[INFO] 修正後の prescription_per_100k の統計量:")
    print(df_corrected['prescription_per_100k'].describe())
    print()

    return df_corrected


def interpret_prescription_rate(df):
    """
    処方率の解釈を提供

    Args:
        df: 修正後のデータセット

    Returns:
        dict: 解釈結果
    """
    print("\n" + "="*80)
    print(" 処方率の解釈")
    print("="*80 + "\n")

    mean_rate = df['prescription_per_100k'].mean()
    median_rate = df['prescription_per_100k'].median()

    # 北海道の例（最大の都道府県）
    # prefecture_codeは文字列または数値の可能性があるため、両方対応
    hokkaido = df[(df['prefecture_code'] == '1') | (df['prefecture_code'] == 1) |
                  (df['prefecture_name'] == '北海道')].iloc[0]

    total_quantity_hokkaido = hokkaido['total_quantity']
    total_pop_hokkaido = hokkaido['total_pop']
    rate_hokkaido = hokkaido['prescription_per_100k']

    # 1人当たり年間処方量
    per_capita_hokkaido = total_quantity_hokkaido / total_pop_hokkaido

    print(f"[INFO] 全国平均:")
    print(f"   - 平均: {mean_rate:,.0f} 錠/10万人")
    print(f"   - 中央値: {median_rate:,.0f} 錠/10万人\n")

    print(f"[INFO] 北海道の例:")
    print(f"   - 総処方量: {total_quantity_hokkaido:,.0f} 錠")
    print(f"   - 総人口: {total_pop_hokkaido:,.0f} 人")
    print(f"   - 処方率: {rate_hokkaido:,.0f} 錠/10万人")
    print(f"   - 1人当たり年間処方量: {per_capita_hokkaido:,.0f} 錠/人\n")

    print("[NOTE] 単位の解釈:")
    print("   - total_quantity: 精神科内服薬の総処方量（錠数・包数の合計）")
    print("   - prescription_per_100k: 人口10万人当たり処方量（錠数）")
    print("   - データソース: NDB Open Data No.10「【内服】外来_都道府県別薬効分類別数量」\n")

    interpretation = {
        'mean_rate': mean_rate,
        'median_rate': median_rate,
        'per_capita_mean': mean_rate / 100000,
        'unit': '錠数・包数（内服薬の合計）',
        'data_source': 'NDB Open Data No.10【内服】外来'
    }

    return interpretation


def save_corrected_data(df_corrected):
    """
    修正後のデータを保存

    Args:
        df_corrected: 修正後のデータセット
    """
    print("\n" + "="*80)
    print(" 修正データの保存")
    print("="*80 + "\n")

    # 並び替え（都道府県コード順）
    df_corrected = df_corrected.sort_values('prefecture_code')

    # 保存
    df_corrected.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

    print(f"[OK] 保存完了: {OUTPUT_FILE}")
    print(f"   - 行数: {len(df_corrected)}")
    print(f"   - 列数: {len(df_corrected.columns)}\n")


def generate_report(analysis, interpretation, df_original, df_corrected):
    """
    修正レポートを生成

    Args:
        analysis: 分析結果
        interpretation: 解釈結果
        df_original: 元データ
        df_corrected: 修正後データ
    """
    print("\n" + "="*80)
    print(" 修正レポート生成")
    print("="*80 + "\n")

    report = f"""# 処方率修正レポート

**日付**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. 問題の特定

### 誤った実装
- **ファイル**: `03_Analysis/scripts/05_merge_final_dataset.py` (Line 208-213)
- **コード**:
  ```python
  # 暫定: 総処方量をそのまま使用（後で人口データと結合して補正）
  df_derived['prescription_per_100k'] = df_derived['total_quantity']  # ❌ 誤り
  ```

### 問題点
- `prescription_per_100k` という名前なのに、人口正規化されていない
- `total_quantity`（処方総量）がそのまま代入されている
- 論文の記述統計（Table 1）で異常な数値: **6,595,793 per 100,000 population**

---

## 2. 修正内容

### 正しい計算式
```python
prescription_per_100k = (total_quantity / total_pop) × 100,000
```

### 修正前後の比較（上位5都道府県）

| 都道府県 | total_quantity | total_pop | prescription_per_100k（誤） | prescription_per_100k（正） |
|---------|----------------|-----------|---------------------------|---------------------------|
"""

    # 修正前後の比較表を追加
    df_comparison = pd.DataFrame({
        'prefecture_name': df_original['prefecture_name'].head(5).values,
        'total_quantity': df_original['total_quantity'].head(5).values,
        'total_pop': df_original['total_pop'].head(5).values,
        'prescription_per_100k_old': df_original['prescription_per_100k'].head(5).values,
        'prescription_per_100k_new': df_corrected['prescription_per_100k'].head(5).values
    })

    for _, row in df_comparison.iterrows():
        report += f"| {row['prefecture_name']} | {row['total_quantity']:,.0f} | {row['total_pop']:,.0f} | {row['prescription_per_100k_old']:,.0f} | {row['prescription_per_100k_new']:,.0f} |\n"

    report += f"""
---

## 3. 修正後の統計量

### 全国（N=47都道府県）

| 統計量 | 値 |
|--------|-----|
| 平均 | {interpretation['mean_rate']:,.0f} 錠/10万人 |
| 中央値 | {interpretation['median_rate']:,.0f} 錠/10万人 |
| 最小値 | {df_corrected['prescription_per_100k'].min():,.0f} 錠/10万人 |
| 最大値 | {df_corrected['prescription_per_100k'].max():,.0f} 錠/10万人 |
| 標準偏差 | {df_corrected['prescription_per_100k'].std():,.0f} 錠/10万人 |

### 解釈
- **1人当たり年間処方量**: 約 {interpretation['per_capita_mean']:,.0f} 錠/人
- これは、平均的な都道府県で、1人当たり年間約 {interpretation['per_capita_mean']:,.0f} 錠の精神科内服薬が処方されていることを意味します。

---

## 4. 単位の明確化

### `total_quantity` の定義
- **単位**: 錠数・包数（内服薬の合計）
- **データソース**: NDB Open Data No.10
  - ファイル: `05_処方薬/01_公費レセプトを含まないデータ/01_処方薬（内服／外用／注射）/【内服】外来_都道府県別薬効分類別数量.xlsx`
- **薬効分類**:
  - 催眠鎮静剤・抗不安剤
  - 精神神経用剤

### `prescription_per_100k` の定義
- **単位**: 錠数/10万人
- **計算式**: `(total_quantity / total_pop) × 100,000`
- **解釈**: 人口10万人当たりの精神科内服薬処方量（年間）

---

## 5. 論文への影響

### Methods セクションの修正
**修正前**:
> "Prescription rates were calculated per 100,000 population using the total population from the Population Census."

**修正後**:
> "Psychiatric medication prescription quantities (total number of tablets/packages for oral medications including hypnotics, anxiolytics, and psychotropics) were obtained from the NDB Open Data No.10. Prescription rates per 100,000 population were calculated by dividing the total quantity by the prefecture's total population and multiplying by 100,000."

### Results セクションの修正（Table 1）
**修正前**:
| Variable | Mean (SD) |
|----------|-----------|
| Prescription per 100k | 6,595,793 (666,996) |  ❌ 異常

**修正後**:
| Variable | Mean (SD) |
|----------|-----------|
| Prescription per 100k | {interpretation['mean_rate']:,.0f} ({df_corrected['prescription_per_100k'].std():,.0f}) |  ✅ 妥当

---

## 6. 今後の対応

### 必須
1. ✅ **データ再計算**: `analysis_dataset_corrected.csv` を使用
2. ⏭️ **解析スクリプト再実行**:
   - `05_descriptive_statistics.py`
   - `06_spatial_exploratory_analysis.py`
   - `07_spatial_regression_analysis.py`
   - `08_sensitivity_and_stratified_analysis.py`
3. ⏭️ **論文修正**: `Manuscript_greenspace_mental_health.qmd`
   - Abstract の記述統計
   - Table 1（記述統計）
   - Methods の詳細説明

### 推奨
- 論文に「1人当たり年間処方量」も記載（解釈しやすい）
- Sensitivity analysis: 薬効分類別（抗うつ薬のみ、抗不安薬のみ）

---

**生成日時**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # レポート保存
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[OK] レポート保存完了: {REPORT_FILE}\n")


def main():
    """メイン処理"""

    # 1. データ読み込み
    df_original = load_data()

    if df_original is None:
        return

    # 2. 現在のデータ分析
    analysis = analyze_current_data(df_original)

    if analysis is None:
        return

    # 3. 正しい処方率を計算
    df_corrected = calculate_correct_rate(df_original)

    # 4. 処方率の解釈
    interpretation = interpret_prescription_rate(df_corrected)

    # 5. 修正データ保存
    save_corrected_data(df_corrected)

    # 6. レポート生成
    generate_report(analysis, interpretation, df_original, df_corrected)

    print("="*80)
    print("[DONE] 全処理完了")
    print("="*80 + "\n")

    print("[INFO] 次のステップ:")
    print("   1. 修正データ確認:")
    print(f"      {OUTPUT_FILE}")
    print()
    print("   2. レポート確認:")
    print(f"      {REPORT_FILE}")
    print()
    print("   3. 解析スクリプト再実行（修正データを使用）:")
    print("      python 03_Analysis/scripts/05_descriptive_statistics.py")
    print("      python 03_Analysis/scripts/06_spatial_exploratory_analysis.py")
    print("      python 03_Analysis/scripts/07_spatial_regression_analysis.py")
    print()
    print("   4. 論文修正:")
    print("      04_Manuscripts/Manuscript_greenspace_mental_health.qmd")
    print()


if __name__ == "__main__":
    main()
