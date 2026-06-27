# Reproduction Guide / 再現手順書

**Project:** `greenspace-mental-health-japan`  
**Manuscript:** *Not All Environmental Indicators Travel: Lessons from Greenspace and Mental Health Service Use in Japan*  
**Repository:** https://github.com/haruki00430/greenspace-mental-health-japan  
**Archive DOI:** `10.5281/zenodo.XXXXXXX` — replace with actual DOI at release.

This guide describes how to reproduce the **prefecture-level aggregated analysis (N = 47)** reported in the manuscript.  
本書は論文に報告した **47都道府県の集計解析** を再現する手順です。

---

## What this repository includes / 含むもの・含まないもの

| Included | Not included (download separately) |
|----------|------------------------------------|
| Analysis scripts (`03_Analysis/scripts/`) | NDB raw Excel (MHLW portal) |
| Figures (`results/figures/`) | Large land-use mesh ZIP archives (MLIT) |
| Model result summaries (`results/`) | Individual-level claims |
| `data/processed/analysis_dataset.csv` (N = 47) | Files > 100 MB (GitHub limit) |
| `REPRODUCE.md`, `DATA_SOURCES.md` | `data/processed/spatial_analysis_data.geojson` (>100 MB; Zenodo/local only) |

Under MHLW rules, **individual-level claims cannot be redistributed.**  
Prefecture-level values in `data/processed/` are derived from publicly available open data only.

---

## System requirements / システム要件

| Item | Requirement |
|------|-------------|
| Python | 3.10 or later (3.11+ tested on Windows) |
| OS | Windows 10/11, macOS 12+, Ubuntu 20.04+ |
| RAM | 8 GB minimum (16 GB if rebuilding greenspace from mesh data) |
| Disk | ~3 GB for NDB Excel + interim files; >10 GB if rebuilding greenspace pipeline |

---

## Step 0: Clone and environment / 環境構築

```bash
git clone https://github.com/haruki00430/greenspace-mental-health-japan.git
cd greenspace-mental-health-japan

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Route 1 — Minimal reproduce (recommended for reviewers) / 最小再現（推奨）

Uses **committed data** (`data/processed/spatial_analysis_data.geojson`, N = 47) only.  
No NDB download required. Reproduces the spatial regression models and figures.

### 1.1 Verify committed data

The committed GeoJSON contains all 47 prefecture-level analysis variables:

```bash
python - <<'EOF'
import geopandas as gpd
gdf = gpd.read_file("data/processed/spatial_analysis_data.geojson")
print(f"N prefectures: {len(gdf)}")
print("Columns:", list(gdf.columns))
EOF
```

Expected: N = 47; columns include `prescription_per_100k`, `total_greenspace_ratio_percent`, etc.

### 1.2 Re-run spatial regression

```bash
python 03_Analysis/scripts/07_spatial_regression_analysis.py
```

**Expected headline checks:**

| Quantity | Expected | Notes |
|----------|----------|-------|
| N prefectures | 47 | Exact |
| Best model | SDM | AIC = 1368.48 |
| SDM pseudo-R² | 0.735 | ±0.01 |
| SDM greenspace β | ~1,326 | p = 0.836 (not significant) |
| Global Moran's I (greenspace) | 0.270 | p = 0.006 |

### 1.3 Regenerate figures

```bash
python 03_Analysis/scripts/create_figures.py
```

Outputs: `results/figures/choropleth_greenspace.png`, `choropleth_prescription.png`, `lisa_map_prescription.png`

---

## Route 2 — Full rebuild from public sources / 公式データからのフル再構築

Follow **`DATA_SOURCES.md`** to download:

1. **NDB Open Data No.10** — psychiatric medication prescriptions (`05_処方薬`)  
2. **MLIT L03-b** — national land-use mesh data (greenspace ratio)  
3. **e-Stat / Census 2020** — population, aging rate, unemployment, income  
4. **MHLW Medical Facility Survey** — psychiatric clinic and physician density

### 2.1 Run scripts in order

```bash
python 03_Analysis/scripts/01_identify_psychiatric_drug_codes.py
python 03_Analysis/scripts/02_extract_ndb_prescriptions.py
python 03_Analysis/scripts/03_calculate_greenspace_ratio.py
python 03_Analysis/scripts/04_integrate_socioeconomic_data.py
python 03_Analysis/scripts/05_merge_final_dataset.py
python 03_Analysis/scripts/06_spatial_exploratory_analysis.py
python 03_Analysis/scripts/07_spatial_regression_analysis.py
python 03_Analysis/scripts/08_sensitivity_and_stratified_analysis.py
python 03_Analysis/scripts/create_figures.py
```

**Prerequisites (before Step 01):**  
- NDB Excel files downloaded to local path configured in Script 01  
- MLIT land-use mesh ZIP files in `data/raw/L03_b_Land_Use_All/`  
- e-Stat data manually downloaded or via API

See `03_Analysis/scripts/README.md` for plain-language descriptions of each step.

### 2.2 Manuscript rendering (optional)

```bash
cd 04_Manuscripts
quarto render Manuscript_CMHJ.qmd --to docx
```

Requires Quarto and `apa.csl` (included in repository).

---

## Zenodo ↔ GitHub release workflow / リリース手順

1. Ensure no secrets or raw NDB data in repository (`git status --short`)
2. Tag `v1.0.0` on GitHub after acceptance notification
3. Enable **Zenodo–GitHub integration** for `haruki00430/greenspace-mental-health-japan`
4. Create GitHub Release → Zenodo auto-archives and issues DOI
5. Edit Zenodo metadata per `docs/ZENODO_DEPOSIT_MANIFEST.md`
6. Replace `XXXXXXX` in `CITATION.cff` and `04_Manuscripts/Manuscript_CMHJ.qmd` § Data availability
7. Re-render `Manuscript_CMHJ.qmd` with updated DOI and submit final version to journal

---

## Troubleshooting / トラブルシュート

| Issue | Action |
|-------|--------|
| `FileNotFoundError` for NDB Excel | Configure NDB paths in script or download from MHLW portal |
| `ModuleNotFoundError: libpysal` | Run `pip install -r requirements.txt` |
| Japanese characters garbled | Scripts use UTF-8; run `chcp 65001` on Windows or use Python 3.10+ |
| `spatial_analysis_data.geojson` missing | Pull latest from GitHub (`git pull`) |
| Headline β mismatch | Verify FY 2020 NDB round and same psychiatric drug classification codes |

---

## Citation / 引用

If you use this repository or the Zenodo archive, cite:

- **Code/software:** GitHub repository URL + Zenodo DOI (see `CITATION.cff`)
- **Data:** MHLW NDB Open Data + MLIT + e-Stat (see `DATA_SOURCES.md`)
- **Paper:** Saito H, Ohira T. Not All Environmental Indicators Travel. *Community Mental Health Journal*. 2026 [in review].

---

## Document map / 関連ドキュメント

| File | Purpose |
|------|---------|
| `DATA_SOURCES.md` | Official download URLs and file descriptions |
| `docs/ZENODO_DEPOSIT_MANIFEST.md` | Files bundled in Zenodo `v1.0.0` |
| `03_Analysis/scripts/README.md` | Plain-English guide to each analysis script |
| `CITATION.cff` | Machine-readable citation metadata |
| `LICENSE` | CC-BY 4.0 (code and aggregated data) |
| `LICENSE-DATA` | CC-BY 4.0 details for `data/release/` |

**Last updated:** 2026-06-27
