# Greenspace and Psychiatric Medication Prescriptions in Japan

**A Nationwide Spatial Ecological Study (N = 47 Prefectures, FY 2020)**

> **Reproduce · Public-data only:** [`REPRODUCE.md`](REPRODUCE.md) · [`DATA_SOURCES.md`](DATA_SOURCES.md) · [`03_Analysis/scripts/README.md`](03_Analysis/scripts/README.md) · [`docs/ZENODO_DEPOSIT_MANIFEST.md`](docs/ZENODO_DEPOSIT_MANIFEST.md) · [`CITATION.cff`](CITATION.cff)

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20951145.svg)](https://doi.org/10.5281/zenodo.20951145)

> **日本語概要は下部の「概要（日本語）」セクションを参照してください。**

---

## Overview

This repository contains the analysis code and result outputs for the study:

> Saito H, Ohira T. "Not All Environmental Indicators Travel: Lessons from Greenspace and Mental Health Service Use in Japan." *International Journal of Environmental Health Research*. [Submitted 2026-06-28; previously declined without peer review at *Community Mental Health Journal*, 2026-06-28]

We examined whether **prefecture-level greenspace coverage** predicts **psychiatric medication prescription rates** across all 47 Japanese prefectures using spatial ecological methods and NDB Open Data (FY 2020).

**Key finding:** After socioeconomic and spatial adjustment, greenspace quantity was not a significant predictor of prescription volume (β = 1,326; p = 0.836 in the best-fit Spatial Durbin Model). We interpret this as a proxy-validation result: administrative greenspace area may be too coarse a proxy for the environmental pathways that actually mediate mental health outcomes.

---

## Key Results

| Model | AIC | Pseudo-R² | Greenspace β (p) |
|-------|-----|-----------|-----------------|
| OLS | 1382.77 | 0.529 | 1,483 (p = 0.856) |
| Spatial Lag Model | 1381.44 | 0.562 | −939 (p = 0.899) |
| Spatial Error Model | 1379.61 | 0.493 | — |
| **Spatial Durbin Model** | **1368.48** | **0.735** | **1,326 (p = 0.836)** |

- Global Moran's I: Greenspace ratio = 0.270 (p = 0.006); Prescription rate = 0.349 (p = 0.001)
- Significant predictors: Aging rate, per-capita income, psychiatric clinic density
- N = 47 prefectures; stratified analyses (urban/rural) showed no significant interaction

---

## Data Sources

| Variable | Source | Provider |
|---------|--------|---------|
| Psychiatric medication prescriptions | NDB Open Data No.10 (FY 2020) | Ministry of Health, Labour and Welfare |
| Greenspace ratio | National Land Numerical Information (Land use) | Ministry of Land, Infrastructure, Transport and Tourism |
| Aging rate, unemployment, income | Population census / Tax statistics | Statistics Bureau of Japan (e-Stat) |
| Psychiatric clinic density | Medical facility survey | Ministry of Health, Labour and Welfare |
| Prefecture boundaries | National Land Numerical Information (A30) | MLIT |

**Note:** NDB raw data are not included in this repository. They are publicly available at:
https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html

---

## Repository Structure

```
NDB_XXX_greenspace_mental_health/
├── README.md                         # This file
├── LICENSE                           # CC-BY 4.0
├── requirements.txt                  # Python dependencies
├── config/
│   └── config.yaml                   # Project configuration
├── 03_Analysis/
│   └── scripts/                      # Analysis scripts (run in numerical order)
│       ├── 01_identify_psychiatric_drug_codes.py   # Step 1: Identify NDB drug codes
│       ├── 02_extract_ndb_prescriptions.py         # Step 2: Extract prescription data
│       ├── 03_calculate_greenspace_ratio.py        # Step 3: Compute greenspace ratios
│       ├── 04_integrate_socioeconomic_data.py      # Step 4: Merge socioeconomic variables
│       ├── 05_merge_final_dataset.py               # Step 5: Create analysis dataset
│       ├── 06_spatial_exploratory_analysis.py      # Step 6: Spatial autocorrelation (Moran's I, LISA)
│       ├── 07_spatial_regression_analysis.py       # Step 7: OLS / SLM / SEM / SDM
│       ├── 08_sensitivity_and_stratified_analysis.py  # Step 8: Sensitivity & stratified analyses
│       └── create_figures.py                       # Figure generation (Fig. 1–3)
├── data/
│   ├── raw/           # NDB raw data — NOT included (download from MHLW)
│   ├── interim/       # Intermediate outputs
│   └── processed/     # Final analysis dataset (N = 47 prefectures)
├── results/
│   ├── figures/       # Map and plot outputs (PNG)
│   └── tables/        # Model results (CSV)
│       ├── model_comparison.csv
│       ├── regression_results.txt
│       ├── morans_i_results.txt
│       ├── sensitivity_analysis_results.txt
│       └── stratified_analysis_results.txt
├── 04_Manuscripts/
│   ├── Manuscript_IJEHR.qmd           # Quarto source (CSE format, IJEHR submission)
│   ├── Manuscript_CMHJ.qmd           # Prior CMHJ submission source (APA)
│   ├── references.bib                # BibTeX references
│   └── apa.csl                       # APA 7th edition citation style
└── docs/                             # Research protocol and progress reports
```

---

## Requirements

Python 3.14 is used in the development environment (`requirements.txt`).

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

Key packages: `pandas`, `geopandas`, `libpysal`, `esda`, `spreg`, `statsmodels`, `matplotlib`, `seaborn`

---

## Usage

### 1. Data Preparation (requires NDB raw data downloaded separately)

```bash
python 03_Analysis/scripts/01_identify_psychiatric_drug_codes.py
python 03_Analysis/scripts/02_extract_ndb_prescriptions.py
python 03_Analysis/scripts/03_calculate_greenspace_ratio.py
python 03_Analysis/scripts/04_integrate_socioeconomic_data.py
python 03_Analysis/scripts/05_merge_final_dataset.py
```

### 2. Spatial Analysis

```bash
python 03_Analysis/scripts/06_spatial_exploratory_analysis.py
python 03_Analysis/scripts/07_spatial_regression_analysis.py
python 03_Analysis/scripts/08_sensitivity_and_stratified_analysis.py
```

### 3. Figure Generation

```bash
python 03_Analysis/scripts/create_figures.py
```

### 4. Manuscript Rendering (requires Quarto and apa.csl)

```bash
cd 04_Manuscripts
quarto render Manuscript_IJEHR.qmd --to docx
```

---

## License

Code and aggregate data in this repository are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
See [`LICENSE`](LICENSE) (code) and [`LICENSE-DATA`](LICENSE-DATA) (prefecture-level aggregate tables).

NDB raw Excel files are not redistributed; see [`DATA_SOURCES.md`](DATA_SOURCES.md).

---

## Citation

If you use this code or data, please cite:

```
Saito H, Ohira T. Not All Environmental Indicators Travel: Lessons from Greenspace and
Mental Health Service Use in Japan. International Journal of Environmental Health Research. [Submitted 2026].
```

Or use the Zenodo DOI (see [`CITATION.cff`](CITATION.cff)):  
`https://doi.org/10.5281/zenodo.20951145`

---

## Authors / 著者

**Haruki Saito** (Corresponding)  
Department of Epidemiology, Fukushima Medical University School of Medicine  
1 Hikarigaoka, Fukushima-shi, Fukushima 960-1295, Japan  
Email: m211039@fmu.ac.jp · ORCID: [0009-0009-7890-6068](https://orcid.org/0009-0009-7890-6068)

**Tetsuya Ohira**  
Department of Epidemiology, Fukushima Medical University School of Medicine, Fukushima, Japan  
Radiation Medical Science Center for the Fukushima Health Management Survey, Fukushima Medical University, Fukushima, Japan  
ORCID: [0000-0003-4532-7165](https://orcid.org/0000-0003-4532-7165)

---

---

## 概要（日本語）

### 研究タイトル

「緑地環境指標の適用限界：日本における都道府県別精神科処方薬データを用いた空間疫学的検証」

### 背景・目的

行政指標（面積ベースの緑地率）が精神科処方薬という健康サービス指標を予測できるかを、日本全47都道府県のNDBオープンデータ（FY2020）と空間回帰モデルを用いて検証しました。

### 主要結果

- 最適モデル（空間ダービンモデル：AIC = 1368.48、Pseudo-R² = 0.735）において、緑地率は処方量の有意な予測因子ではありませんでした（β = 1,326; p = 0.836）
- 緑地率・処方量はいずれも有意な空間的自己相関を示しました（Moran's I > 0.27, p < 0.01）
- 有意な予測因子：高齢化率、1人あたり所得、精神科診療所密度
- 都市・農村層別解析では方向性が逆転したが、交互作用検定で有意差なし

### 解釈

この結果は「自然環境が精神保健に影響しない」ことを意味するのではなく、**面積ベースの緑地率が精神保健関連経路（アクセシビリティ・質・利用頻度）を適切に反映していない**ことを示すproxy-validation研究として解釈されます。

### データ・コード

- NDB生データ：[厚生労働省NDBオープンデータ](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html)（要手動ダウンロード）
- 解析コード・結果ファイル：本リポジトリ（CC-BY 4.0）
- 都道府県別集計値（N=47）：`data/processed/`、`results/` フォルダ

---

*Last updated: 2026-06-28*
