# GitHub / Zenodo 設定手順書

**プロジェクト:** NDB_XXX_greenspace_mental_health  
**論文:** Not All Environmental Indicators Travel (CMHJ投稿版)  
**作成日:** 2026-06-27

---

## 1. GitHub リポジトリの現状と方針

### 現在のリポジトリ

- **URL:** <https://github.com/haruki00430/greenspace-mental-health-japan>
- **名前:** `greenspace-mental-health-japan`
- **公開設定:** Public

### リポジトリ名の変更検討

| 案 | 長所 | 短所 |
|----|------|------|
| **現状維持**（`NDB_XXX_greenspace_mental_health`） | 既存URLを破壊しない | やや内部的すぎる名称 |
| `greenspace-mental-health-japan` | 国際読者に分かりやすい | 既存URLが変わる（GitHub は自動リダイレクトあり） |
| `greenspace-psychiatric-prescriptions-japan` | 内容を正確に反映 | 長い |
| `not-all-indicators-travel-japan` | 論文タイトルと対応 | 内容が推測しにくい |

**推奨:** Zenodo 登録前に名前を変更するのであれば `greenspace-mental-health-japan` が最も適切。すでに Zenodo に登録済みの場合は変更しない（DOI が壊れるリスクあり）。

---

## 2. GitHub 公開の手順

### 2-1. リポジトリの整備

以下のファイル・フォルダがリポジトリに含まれていることを確認してください。

```
NDB_XXX_greenspace_mental_health/
├── README.md                         ← 必須（英語）
├── LICENSE                           ← 必須（CC-BY 4.0 推奨）
├── 03_Analysis/
│   └── scripts/
│       ├── 01_data_preparation.py
│       ├── 02_spatial_analysis.py
│       ├── 03_visualization.py
│       └── README.md                 ← 実行手順
├── 04_Manuscripts/
│   └── Manuscript_CMHJ.qmd          ← ソース（NDBデータは除く）
├── results/
│   └── figures/                      ← 生成された図（Gitで管理可）
└── requirements.txt
```

**絶対に含めてはいけないもの:**
- `02_Data/raw/` 内の NDB Excel ファイル
- `02_Data/interim/` の Parquet / CSV（生成物は除外）

### 2-2. README.md の必須内容

```markdown
# Greenspace and Psychiatric Medication Prescriptions in Japan
## A Spatial Ecological Study Using NDB Open Data

### Citation
Saito H, Ohira T. Not all environmental indicators travel: lessons from
greenspace and mental health service use in Japan.
Community Mental Health Journal. [in review]

### Data Sources
- NDB Open Data: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html
- Biodiversity Center of Japan: http://www.biodic.go.jp/
- e-Stat: https://www.e-stat.go.jp/

### Requirements
Python 3.9+ / See requirements.txt

### Usage
python 03_Analysis/scripts/01_data_preparation.py
python 03_Analysis/scripts/02_spatial_analysis.py
python 03_Analysis/scripts/03_visualization.py

### License
CC-BY 4.0

### Zenodo DOI
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20986298.svg)](https://doi.org/10.5281/zenodo.20986298)
```

### 2-3. LICENSE ファイル

`CC-BY 4.0` の場合、<https://choosealicense.com/licenses/cc-by-4.0/> から LICENSE テキストをコピーして配置します。

### 2-4. .gitignore の確認

```gitignore
# NDB 生データ（絶対除外）
02_Data/raw/
02_Data/interim/*.parquet
02_Data/interim/*.csv

# 設定フォルダ（除外）
.claude/
.cursor/
.obsidian/
.gemini/
__pycache__/
*.pyc
.venv/
```

### 2-5. リポジトリを Public に変更

（現在 Private の場合）
1. GitHub → リポジトリ設定 → Danger Zone → `Change visibility` → `Make public`
2. 「I want to make this repository public」と入力して確認

**注意:** Public 化の前に NDB 実データが含まれていないことを必ず確認すること。

---

## 3. Zenodo との連携手順

### 3-1. GitHub → Zenodo 連携

1. <https://zenodo.org/> にログイン（GitHub アカウントで連携可）
2. 右上メニュー → `GitHub` タブを選択
3. `Sync` をクリックして GitHub リポジトリ一覧を更新
4. `greenspace-mental-health-japan` のトグルを `ON` にする

### 3-2. GitHub Release でDOIを取得

1. GitHub のリポジトリページ → `Releases` → `Create a new release`
2. Tag version: `v1.0.0`（論文受理後に作成する）
3. Release title: `CMHJ Submission — v1.0.0`
4. Description:

```
Initial public release accompanying manuscript submission to
Community Mental Health Journal (2026-06-27).

Includes analysis scripts, figure outputs, and Quarto source.
NDB raw data are not included (available from MHLW).
```

5. `Publish release` をクリック

→ Zenodo が自動でアーカイブを作成し、**DOI が発行される**

### 3-3. Zenodo メタデータの編集

Zenodo ダッシュボードでアーカイブのメタデータを編集：

| 項目 | 入力内容 |
|------|---------|
| Title | Not All Environmental Indicators Travel: Lessons from Greenspace and Mental Health Service Use in Japan — Analysis Code |
| Authors | Saito, Haruki; Ohira, Tetsuya |
| Description | Analysis code and result figures for the ecological study... |
| Keywords | greenspace; mental health; psychiatric medication; spatial epidemiology; NDB; Japan |
| License | CC-BY 4.0 |
| Communities | `zenodo` （+ `public-health` があれば追加） |
| Related identifiers | CMHJ DOI（受理後に追加） |

### 3-4. Data Availability Statement への DOI 追記

DOI が確定したら、`Manuscript_CMHJ.qmd` の Data Availability セクションを更新：

```markdown
## Availability of Data and Materials

All data used in this study are publicly available. NDB Open Data (Ministry of Health,
Labour and Welfare): https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html.
Biodiversity Center of Japan: http://www.biodic.go.jp/. e-Stat (Statistics Bureau of
Japan): https://www.e-stat.go.jp/. The analysis code and aggregate prefecture-level
data (N = 47) are openly available on Zenodo at https://doi.org/10.5281/zenodo.20986298.
```

その後 `quarto render Manuscript_CMHJ.qmd --to docx` で最終版 DOCX を再生成。

---

## 4. APA CSL のダウンロードと設定

QMD を APA 形式でレンダリングするには `apa.csl` が必要です。

1. <https://www.zotero.org/styles/apa> を開く
2. 「Download」をクリックして `apa.csl` を保存
3. `04_Manuscripts/apa.csl` として配置
4. `quarto render Manuscript_CMHJ.qmd --to docx` でレンダリング

---

## 5. 新規 BibTeX エントリの追加

`Manuscript_CMHJ.qmd` は以下の引用キーを使用しますが、`references.bib` に未登録のエントリがあります。`references_addendum.bib` の内容を `references.bib` に追記してください（追記前に確認すること）。

未登録キーの一覧:
- `@nieuwenhuijsen2015` — Nieuwenhuijsen (2015) Exposure Assessment in Environmental Epidemiology
- `@armstrong1990` — Armstrong (1990) Effect of measurement error
- `@openshaw1984` — Openshaw (1984) The Modifiable Areal Unit Problem
- `@kwan2012` — Kwan (2012) The uncertain geographic context problem
- `@diezroux2001` — Diez Roux (2001) Investigating neighborhood effects on health
- `@flowerdew2008` — Flowerdew et al. (2008) Neighbourhood effects on health
- `@zandbergen2008` — Zandbergen & Green (2008) Error and bias in determining exposure
- `@cliff1981` — Cliff & Ord (1981) Spatial Processes

---

## 6. チェックリスト（GitHub / Zenodo）

### 論文投稿前
- [ ] リポジトリ名を検討・確定
- [ ] NDB 実データが含まれていないことを確認
- [ ] README.md を英語で整備
- [ ] LICENSE ファイルを配置
- [ ] .gitignore を確認
- [ ] リポジトリを Public に変更（または確認）
- [ ] Zenodo 連携を有効化

### 論文受理後
- [ ] GitHub Release v1.0.0 を作成
- [ ] Zenodo で DOI を取得
- [ ] Zenodo メタデータを編集
- [ ] Data Availability に Zenodo DOI を追記
- [ ] Manuscript_CMHJ.qmd を再レンダリング
- [ ] 最終版 DOCX を出版社に提出
