# IJEHR 投稿ワークフロー・チェックリスト

**論文:** Not All Environmental Indicators Travel: Lessons from Greenspace and Mental Health Service Use in Japan  
**投稿先:** International Journal of Environmental Health Research (Taylor & Francis)  
**前投稿:** Community Mental Health Journal — Reject（2026-06-28、査読なし）  
**投稿日目標:** 2026-06-28  
**作成日:** 2026-06-28

---

## 1. ジャーナル基本情報

| 項目 | 内容 |
|------|------|
| ジャーナル名 | International Journal of Environmental Health Research |
| 出版社 | Taylor & Francis |
| ISSN | 0960-3123 (print) / 1369-1619 (online) |
| 投稿システム | Taylor & Francis Submission Portal |
| 審査方式 | **Single anonymous peer review**（著者名は原稿タイトルページに記載可） |
| 引用スタイル | **CSE (T&F standard)** |
| 論文種別 | Research Article |
| 本文語数上限 | 3,500 語（abstract・keywords・表・図・謝辞・参考文献除く） |
| Abstract | 非構造化 **200 語** |
| Keywords | **3–5 語** |
| 表＋図 | 本文 **≤6** |
| References | **≤35** |

---

## 2. CMHJ からの主な変更点

| 項目 | CMHJ | IJEHR |
|------|------|-------|
| 引用 | APA 7 | CSE |
| 審査 | Double blind | Single anonymous（著者情報可） |
| Abstract | 構造化 238 語 | 非構造化 159 語 |
| Keywords | 6 語 | 5 語 |
| 表 | 5（本文） | 3（本文）+ 2（Supplementary） |
| Biographical note | なし | **必須**（各著者 ≤200 語） |
| Methods 見出し | Methods | Materials and methods |

---

## 3. 投稿ファイル一覧

| ファイル名 | 用途 | 状態 |
|-----------|------|------|
| `Manuscript_IJEHR_20260628.docx` | **主原稿（CSE・著者付き）** | ✅ |
| `Supplementary_Tables_IJEHR_20260628.docx` | 補足表 S1–S2 | ✅ |
| `CoverLetter_IJEHR_20260628.docx` | カバーレター | ✅ |
| `TitlePage_IJEHR_20260628.docx` | タイトルページ・語数 | ✅ |
| `Author_Bios_IJEHR_20260628.docx` | Biographical notes | ✅ |
| `Declarations_IJEHR_20260628.docx` | 各種宣言（ポータル入力用） | ✅ |
| `Fig1.png` / `Fig2.png` / `Fig3.png` | 図 1–3 | ✅ |
| `Submit to International Journal of Environmental Health Research.pdf` | 投稿規定 | ✅ |

### ソースファイル（フォルダ外）

| ファイル | 用途 |
|----------|------|
| `../Manuscript_IJEHR.qmd` | IJEHR 準拠 Quarto ソース（CSE） |
| `../Supplementary_Tables_IJEHR.qmd` | 補足表ソース |
| `../prepare_submission_IJEHR.py` | DOCX 一括生成 |
| `../validate_IJEHR_limits.py` | 語数・件数検証 |
| `../cse.csl` | CSE 引用スタイル |

---

## 4. 投稿前チェックリスト

### 4-1. コンテンツ

- [x] タイトルページに著者名・所属・ORCID・通信著者メール
- [x] Abstract 非構造化、200 語以内（約 159 語）
- [x] Keywords 3–5 語（5 語）
- [x] 本文 ≤3,500 語（約 2,490 語）
- [x] 本文 表 3 + 図 3 = 6
- [x] 参考文献 28 件（≤35）
- [x] 本文に日本語なし

### 4-2. IJEHR 必須記載事項

- [x] **CRediT** — 実名（Haruki Saito / Tetsuya Ohira）
- [x] **Funding** — no specific grant
- [x] **Disclosure statement** — no competing interests
- [x] **AI 声明** — 記載済み
- [x] **Data availability statement** — GitHub + Zenodo DOI `10.5281/zenodo.20951145`
- [x] **Biographical note** — `Author_Bios_IJEHR_20260628.docx`
- [x] **Ethics** — Materials and methods 内

### 4-3. 図ファイル

- [ ] 解像度 300 dpi（カラー図）
- [x] フォーマット JPEG/PNG/TIFF 可
- [ ] 必要に応じ alt text を著者側で確認（T&F AI 生成も可）

### 4-4. 前投稿開示

- [x] カバーレターに CMHJ 拒否（2026-06-28、査読なし）を記載

---

## 5. Taylor & Francis Submission Portal 手順

1. **ログイン / アカウント**
   - <https://rp.tandfonline.com/> またはジャーナルページの "Go to submission site"

2. **Start a new submission**
   - Journal: International Journal of Environmental Health Research
   - Article type: **Research Article**

3. **著者情報**
   - `TitlePage_IJEHR_20260628.docx` を参照
   - Corresponding Author: Haruki Saito
   - CRediT roles を入力

4. **Abstract & Keywords**
   - 原稿 Abstract セクションからコピー
   - Keywords: Greenspace; Mental health; Spatial epidemiology; Environmental epidemiology; Japan

5. **Biographical notes**
   - `Author_Bios_IJEHR_20260628.docx` から各著者分を入力

6. **ファイルアップロード**
   - Manuscript (with author details): `Manuscript_IJEHR_20260628.docx`
   - Supplementary material: `Supplementary_Tables_IJEHR_20260628.docx`
   - Figure 1: `Fig1.png`
   - Figure 2: `Fig2.png`
   - Figure 3: `Fig3.png`

7. **Declarations（ポータル各フォーム）**
   - `Declarations_IJEHR_20260628.docx` からコピー
   - Funding / Competing interests / AI / Data availability
   - Data set DOI: `10.5281/zenodo.20951145`

8. **Cover letter**
   - `CoverLetter_IJEHR_20260628.docx` を貼り付け

9. **最終確認 → Submit**

---

## 6. 再生成手順

```powershell
Set-Location projects\NDB_XXX_greenspace_mental_health\04_Manuscripts
quarto render Manuscript_IJEHR.qmd --to docx
quarto render Supplementary_Tables_IJEHR.qmd --to docx
python prepare_submission_IJEHR.py
python validate_IJEHR_limits.py
```

---

## 7. Data Availability（Zenodo）

- GitHub: <https://github.com/haruki00430/greenspace-mental-health-japan>
- Zenodo DOI: <https://doi.org/10.5281/zenodo.20951145> (release v1.0.2)
- 受理後にジャーナル DOI を Zenodo Related identifiers に追記

---

## 8. 参考：CMHJ Reject 記録

- 通知 PDF: `../submission_package_CMHJ/Gmail - Decision on your submission to Community Mental Health Journal.pdf`
- Submission ID: `851f7383-be4a-43b2-b636-6d415e93ef82`
- 査読コメント: なし（Editorial rejection）
