# data/release — Prefecture-Level Aggregate Data

This directory contains **public release** aggregate data files (N = 47 Japanese prefectures)
for use in reproducing the analysis without downloading NDB raw files.

## Files

| File | Rows | Description |
|------|------|-------------|
| *(populated at v1.0.0 release)* | | |

## Primary data file

The main analysis dataset is at:  
**`data/processed/analysis_dataset_per100k.csv`** (N = 47 prefectures × ~15 variables)

The GeoJSON with LISA results is at:  
**`data/processed/spatial_analysis_data.geojson`** (already committed)

## Column dictionary

| Column | Description | Unit |
|--------|-------------|------|
| `prefecture` | Prefecture name | string |
| `prescription_per_100k` | Psychiatric medication prescriptions | per 100,000 population |
| `total_greenspace_ratio_percent` | Greenspace coverage | % |
| `aging_rate` | Population aged ≥65 | % |
| `unemployment_rate` | Unemployment rate | % |
| `income_per_capita` | Per-capita taxable income | 万円 (10,000 JPY) |
| `single_household_rate` | Single-person household rate | % |
| `psych_clinic_density` | Psychiatric clinic density | per 100,000 |
| `population` | Total prefecture population | persons |

## Data provenance

- Prescription data: NDB Open Data No.10 (FY 2023) — MHLW
- Greenspace: National Land Numerical Information L03-b — MLIT
- Covariates: Population Census 2020, Tax statistics, Medical Facility Survey — e-Stat / MHLW

See [`../../DATA_SOURCES.md`](../../DATA_SOURCES.md) for official download URLs.

## License

CC-BY 4.0 — see [`../../LICENSE-DATA`](../../LICENSE-DATA).  
Cite: Saito H, Ohira T. *Community Mental Health Journal* 2026 + Zenodo DOI in CITATION.cff.
