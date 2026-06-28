# Zenodo Deposit Manifest (v1.0.3)

**Record type:** Software + dataset (prefecture-level aggregate, N = 47)  
**DOI:** *pending* — assign after Zenodo archives `v1.0.3`; concept DOI `10.5281/zenodo.20950806` (latest)  
**Previous version:** `10.5281/zenodo.20951145` (`v1.0.2`, 2026-06-27)  
**GitHub tag:** `v1.0.3` (Zenodo archival release, 2026-06-28)  
**License:** Code CC-BY 4.0; data CC-BY 4.0 (derived prefecture-level aggregates only)

---

## 1. Purpose / 目的

Bundle everything needed to:

1. Cite a **version-fixed** snapshot (Zenodo DOI).  
2. Reproduce manuscript headline statistics **without** NDB raw files (via committed GeoJSON + results).  
3. Document how to rebuild from MHLW / e-Stat / MLIT primary sources (`DATA_SOURCES.md`).

**Do not upload:** NDB raw Excel, individual-level records, land-use mesh ZIPs, machine-specific paths with usernames.

---

## 2. Required files (Zenodo archive) / 必須同梱

### 2.1 Metadata and policy

| Path | Description |
|------|-------------|
| `CITATION.cff` | Citation metadata (update DOI/ORCID at release) |
| `LICENSE` | CC-BY 4.0 (code) |
| `LICENSE-DATA` | CC-BY 4.0 for `data/release/` and `data/processed/` aggregate tables |
| `README.md` | Project overview + badges (DOI, license) |
| `REPRODUCE.md` | Step-by-step reproduction guide |
| `DATA_SOURCES.md` | Official download URLs |
| `docs/ZENODO_DEPOSIT_MANIFEST.md` | This file |

### 2.2 Analysis code

| Path | Description |
|------|-------------|
| `requirements.txt` | Python dependencies |
| `config/config.yaml` | Project configuration (no secrets; uses public URLs) |
| `03_Analysis/scripts/01_identify_psychiatric_drug_codes.py` | Step 1: Identify NDB drug codes |
| `03_Analysis/scripts/02_extract_ndb_prescriptions.py` | Step 2: Extract prescription data |
| `03_Analysis/scripts/03_calculate_greenspace_ratio.py` | Step 3: Compute greenspace ratios |
| `03_Analysis/scripts/04_integrate_socioeconomic_data.py` | Step 4: Merge covariates |
| `03_Analysis/scripts/05_merge_final_dataset.py` | Step 5: Create analysis dataset |
| `03_Analysis/scripts/06_spatial_exploratory_analysis.py` | Step 6: Moran's I, LISA, choropleth maps |
| `03_Analysis/scripts/07_spatial_regression_analysis.py` | Step 7: OLS / SLM / SEM / SDM |
| `03_Analysis/scripts/08_sensitivity_and_stratified_analysis.py` | Step 8: Sensitivity & stratified |
| `03_Analysis/scripts/create_figures.py` | Manuscript figures (Fig. 1–3) |
| `03_Analysis/scripts/README.md` | Plain-English descriptions of each script |

### 2.3 Data (committed — aggregate N = 47 only)

| Path | Description |
|------|-------------|
| `data/processed/spatial_analysis_data.geojson` | Final analysis GeoJSON (N = 47 prefectures; all model variables + LISA results) |
| `results/model_comparison.csv` | AIC / R² comparison of OLS / SLM / SEM / SDM |
| `results/regression_results.txt` | Full regression coefficient table |
| `results/morans_i_results.txt` | Global Moran's I statistics |
| `results/sensitivity_analysis_results.txt` | Sensitivity analysis results |
| `results/stratified_analysis_results.txt` | Urban/rural stratified analysis |
| `results/figures/choropleth_greenspace.png` | Fig. 1 — Greenspace ratio choropleth map |
| `results/figures/choropleth_prescription.png` | Fig. 2 — Prescription rate choropleth map |
| `results/figures/lisa_map_prescription.png` | Fig. 3 — LISA cluster map |

### 2.4 Manuscript source

| Path | Description |
|------|-------------|
| `04_Manuscripts/Manuscript_IJEHR.qmd` | Quarto source (CSE format; IJEHR submission) |
| `04_Manuscripts/Manuscript_CMHJ.qmd` | Quarto source (APA format; prior CMHJ submission) |
| `04_Manuscripts/references.bib` | BibTeX references |
| `04_Manuscripts/apa.csl` | APA 7th edition citation style |
| `04_Manuscripts/cse.csl` | CSE citation style (IJEHR) |

---

## 3. Files to EXCLUDE from Zenodo / Zenodoから除外するファイル

| Pattern | Reason |
|---------|--------|
| `data/raw/` | NDB raw Excel (MHLW redistribution terms) |
| `data/interim/` | Intermediate files; large; regenerable |
| `04_Manuscripts/submission_package_CMHJ/` | Author identity info (TitlePage, CoverLetter) |
| `04_Manuscripts/submission_package_IJEHR/` | Author identity info (TitlePage, CoverLetter, anonymous DOCX) |
| `04_Manuscripts/*.docx` | Submission DOCXs; not required for reproduction |
| `git_names.txt`, `git_push_error.txt` | Internal debug files |
| `*.pyc`, `__pycache__/`, `.venv/` | Python build artifacts |

---

## 4. Zenodo metadata template / メタデータ入力テンプレート

After GitHub Release triggers Zenodo archival, edit the Zenodo record:

| Field | Value |
|-------|-------|
| **Title** | Not All Environmental Indicators Travel: Greenspace and Psychiatric Medication Prescriptions in Japan — Analysis Code and Aggregate Data |
| **Creators** | Saito, Haruki (ORCID: 0009-0009-7890-6068); Ohira, Tetsuya (ORCID: 0000-0003-4532-7165) |
| **Description** | Analysis code and prefecture-level aggregate data (N = 47) for a spatial ecological study examining whether greenspace coverage predicts psychiatric medication prescription rates in Japan. |
| **Keywords** | greenspace; mental health; psychiatric medication; spatial epidemiology; proxy validation; NDB Open Data; Japan |
| **License** | Creative Commons Attribution 4.0 International |
| **Communities** | `zenodo` |
| **Related identifiers** | Published IJEHR article DOI (add after acceptance) |
| **Method** | Spatial Durbin Model, Global Moran's I, LISA |
| **Notes** | Prefecture-level aggregate data only (N = 47). NDB raw data not included; see DATA_SOURCES.md. |

---

## 5. Data Availability Statement update / データ可用性記述の更新

After DOI is confirmed, update `04_Manuscripts/Manuscript_CMHJ.qmd` § Availability of Data:

```
The analysis code and prefecture-level aggregate data (N = 47) are openly
available at https://doi.org/10.5281/zenodo.20951145.
```

Then re-render and submit final DOCX to the journal.

---

## 6. v1.0.3 changelog / 変更点

- Correct NDB Open Data No.10 to **FY 2023** (fiscal year 2023) in README, `CITATION.cff`, and manuscript sources
- Add IJEHR submission package (`Manuscript_IJEHR.qmd`, `submission_package_IJEHR/`)
- Update journal target: *International Journal of Environmental Health Research* (submitted 2026-06-28)

---

*Last updated: 2026-06-28*
