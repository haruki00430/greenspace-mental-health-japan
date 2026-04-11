# 処方率修正レポート

**日付**: 2026-02-28 11:39:03

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
| 北海道 | 418,089,187 | 5,043,000 | 418,089,187 | 8,290,486 |
| 青森県 | 88,912,826 | 1,165,000 | 88,912,826 | 7,632,002 |
| 岩手県 | 88,115,657 | 1,145,000 | 88,115,657 | 7,695,691 |
| 宮城県 | 155,511,165 | 2,248,000 | 155,511,165 | 6,917,756 |
| 秋田県 | 83,420,160 | 897,000 | 83,420,160 | 9,299,906 |

---

## 3. 修正後の統計量

### 全国（N=47都道府県）

| 統計量 | 値 |
|--------|-----|
| 平均 | 6,812,617 錠/10万人 |
| 中央値 | 6,541,695 錠/10万人 |
| 最小値 | 5,680,676 錠/10万人 |
| 最大値 | 9,299,906 錠/10万人 |
| 標準偏差 | 767,166 錠/10万人 |

### 解釈
- **1人当たり年間処方量**: 約 68 錠/人
- これは、平均的な都道府県で、1人当たり年間約 68 錠の精神科内服薬が処方されていることを意味します。

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
| Prescription per 100k | 6,812,617 (767,166) |  ✅ 妥当

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

**生成日時**: 2026-02-28 11:39:03
