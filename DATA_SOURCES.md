# Data Sources / データソース

This repository does **not** include NDB raw Excel files or large geospatial rasters.  
All primary inputs are **publicly available** administrative or geospatial open data.

本リポジトリは NDB 生 Excel および大容量ラスターファイルを同梱しません。  
一次データはすべて公開情報です。

---

## 1. NDB Open Data / NDB オープンデータ（第10回）

| Item | Details |
|------|---------|
| Provider | Ministry of Health, Labour and Welfare (MHLW) / 厚生労働省 |
| Portal | https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html |
| Round used | **第10回 NDB オープンデータ**（FY 2023 / 令和5年度） |
| Format | Excel (`.xlsx`) |
| Redistribution | **Authors cannot redistribute raw files**; users must download from the portal |

### 1.1 Psychiatric medication prescriptions (outcome) / 精神科処方薬（アウトカム）

| Item | Value |
|------|-------|
| Category | `05_処方薬` → `01_処方薬（内服）` |
| Subfolder | `01_公費レセプトを含まないデータ` |
| Files | 【内服】外来（院外）_都道府県別薬効分類別数量.xlsx / 【内服】外来（院内）_都道府県別薬効分類別数量.xlsx |
| Drug classes | 催眠鎮静剤・抗不安剤（薬効コード 112）、精神神経用剤（薬効コード 117） |
| Unit | Prefecture × drug classification (aggregated volumes, DDD) |
| Manuscript use | Psychiatric medication prescription rate per 100,000 population (FY 2023; denominator: Population Census 2020) |

**Rate calculation:**  
`(sum of relevant prescription volumes) / (prefecture population) × 100,000`

---

## 2. Greenspace data / 緑地データ

### 2.1 National Land Use Statistics / 国土数値情報 土地利用細分メッシュ（L03-b）

| Item | Details |
|------|---------|
| Provider | Ministry of Land, Infrastructure, Transport and Tourism (MLIT) / 国土交通省 |
| Portal | https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L03-b.html |
| Dataset | L03-b 土地利用細分メッシュデータ (2018 or latest) |
| Format | Shapefile / GML |
| Target classes | 森林 (Forest) + 公園・緑地 (Parks and green space) |

**Greenspace ratio calculation:**  
`greenspace_ratio (%) = (forest area + park area) / total prefecture area × 100`

**Do not commit:** Multi-hundred MB mesh ZIP archives (see `.gitignore`).

---

## 3. Socioeconomic and healthcare covariates / 社会経済・医療変数

### 3.1 Population Census / 国勢調査 2020

| Item | Details |
|------|---------|
| Provider | Statistics Bureau of Japan (e-Stat) / 総務省統計局 |
| Portal | https://www.e-stat.go.jp/ |
| Dataset | 2020 Population Census (令和2年国勢調査) |
| Variables | `aging_rate` (≥65 / total), `unemployment_rate`, `single_household_rate`, total population |

### 3.2 Tax statistics / 市町村税課税状況等の調

| Item | Details |
|------|---------|
| Provider | e-Stat / 総務省 |
| Dataset | 市町村税課税状況等の調（令和2年） |
| Variables | `income_per_capita` (1人あたり課税対象所得, 万円) |

### 3.3 Medical facility survey / 医療施設調査・医師歯科医師薬剤師統計

| Item | Details |
|------|---------|
| Provider | MHLW / 厚生労働省 |
| Portal | https://www.mhlw.go.jp/toukei/list/79-1a.html |
| Dataset | 医療施設調査（令和2年）・医師歯科医師薬剤師統計（令和2年） |
| Variables | `psych_clinic_density` (精神科診療所 / 10万人), `psych_doctor_density` (精神科医師 / 10万人) |

---

## 4. Prefecture boundaries / 都道府県境界データ

| Item | Details |
|------|---------|
| Provider | MLIT / 国土交通省 |
| Dataset | 国土数値情報 行政区域データ (N03) — prefecture-level GeoJSON |
| Portal | https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v3_1.html |
| File committed | `data/processed/spatial_analysis_data.geojson` (N = 47 prefectures with analysis results) |

**This GeoJSON contains only prefecture-level aggregate values (N = 47) — no individual-level data.**

---

## 5. Variable summary / 変数一覧

| Variable | Description | Source | Unit |
|----------|-------------|--------|------|
| `prescription_per_100k` | Psychiatric medication prescriptions | NDB No.10 | per 100,000 pop. |
| `total_greenspace_ratio_percent` | Total greenspace coverage | MLIT L03-b | % |
| `aging_rate` | Population aged ≥65 | Census 2020 | % |
| `unemployment_rate` | Unemployment rate | Census 2020 | % |
| `income_per_capita` | Per-capita taxable income | Tax statistics | 万円 |
| `single_household_rate` | Single-person household rate | Census 2020 | % |
| `psych_clinic_density` | Psychiatric clinic density | Medical facility survey | per 100,000 |

---

*Last updated: 2026-06-28*
