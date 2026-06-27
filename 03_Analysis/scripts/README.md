# Analysis scripts (public release)

English descriptions for readers who are **not Python experts**.  
For full reproduction steps, see [`../../REPRODUCE.md`](../../REPRODUCE.md).  
For data sources and download instructions, see [`../../DATA_SOURCES.md`](../../DATA_SOURCES.md).

---

## Suggested order / 実行順序

```text
1. 01_identify_psychiatric_drug_codes.py    ← identify NDB drug codes
2. 02_extract_ndb_prescriptions.py          ← extract prescription data
3. 03_calculate_greenspace_ratio.py         ← calculate greenspace ratios
4. 04_integrate_socioeconomic_data.py       ← merge covariates
5. 05_merge_final_dataset.py                ← create analysis dataset
6. 06_spatial_exploratory_analysis.py       ← Moran's I, LISA, choropleth maps
7. 07_spatial_regression_analysis.py        ← OLS / SLM / SEM / SDM
8. 08_sensitivity_and_stratified_analysis.py ← robustness checks
9. create_figures.py                         ← manuscript figures (Fig. 1–3)
```

Scripts 01–05 require NDB raw Excel files (not in this repository).  
Script 06 onwards can run using the committed `data/processed/spatial_analysis_data.geojson`.

---

## Scripts included in the GitHub / Zenodo release

| Script | What it does (in plain language) |
|--------|----------------------------------|
| [`01_identify_psychiatric_drug_codes.py`](01_identify_psychiatric_drug_codes.py) | Reads NDB Open Data prescription Excel and identifies drug classification codes for anxiolytics, hypnotics, and psychotropics. Outputs a reference CSV of target codes. |
| [`02_extract_ndb_prescriptions.py`](02_extract_ndb_prescriptions.py) | Extracts psychiatric medication volumes from NDB Excel (outpatient and inpatient), computes age-standardized rates per 100,000 population for each of the 47 prefectures. |
| [`03_calculate_greenspace_ratio.py`](03_calculate_greenspace_ratio.py) | Loads MLIT L03-b national land-use mesh data; computes the percentage of forest and park area relative to total prefecture area (greenspace ratio %). |
| [`04_integrate_socioeconomic_data.py`](04_integrate_socioeconomic_data.py) | Assembles prefecture-level covariates from e-Stat: aging rate, unemployment, income, psychiatric clinic and physician density. |
| [`05_merge_final_dataset.py`](05_merge_final_dataset.py) | Joins prescription data, greenspace ratios, and socioeconomic covariates by prefecture code to create the final 47-row analysis dataset. Handles missing values. |
| [`06_spatial_exploratory_analysis.py`](06_spatial_exploratory_analysis.py) | Builds a Queen contiguity spatial weights matrix. Computes Global Moran's I and Local Moran's I (LISA). Generates choropleth maps of greenspace ratio and prescription rate, and a LISA cluster map. |
| [`07_spatial_regression_analysis.py`](07_spatial_regression_analysis.py) | Fits OLS, Spatial Lag (SLM), Spatial Error (SEM), and Spatial Durbin (SDM) regression models. Compares model fit by AIC, log-likelihood, and pseudo-R². Main analysis script. |
| [`08_sensitivity_and_stratified_analysis.py`](08_sensitivity_and_stratified_analysis.py) | Sensitivity checks: outlier exclusion (Cook's D), island exclusion (Hokkaido, Okinawa). Stratified analyses by urbanicity and aging rate. Interaction tests (greenspace × aging rate, greenspace × population density). |
| [`create_figures.py`](create_figures.py) | **Quick-start for reviewers.** Reads the committed GeoJSON (`data/processed/spatial_analysis_data.geojson`) and regenerates the three manuscript figures (Fig. 1 choropleth greenspace, Fig. 2 choropleth prescription, Fig. 3 LISA map). No NDB download needed. |

---

## Other scripts in this folder

Files prefixed `debug_`, `test_`, and `fix_` are **development and diagnostic** scripts used during data preparation. They are **not** required for the main analysis and are not documented here. See source code comments for details.

---

## Language policy

All **public-release** Python files use **English** module docstrings and user-facing messages so international readers can follow the workflow.

---

## Quick validation (no NDB download required)

```bash
# Activate environment
.venv\Scripts\activate  # Windows / source .venv/bin/activate (macOS/Linux)

# Regenerate figures from committed data
python 03_Analysis/scripts/create_figures.py

# Re-run spatial regression from committed GeoJSON
python 03_Analysis/scripts/07_spatial_regression_analysis.py
```

Expected output: SDM AIC = 1368.48, greenspace β = ~1,326 (p = 0.836).
