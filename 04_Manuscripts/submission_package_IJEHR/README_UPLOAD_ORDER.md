# IJEHR 投稿ファイル一覧（アップロード順）

**フォルダ:** `submission_package_IJEHR/`  
**最終更新:** 2026-06-28

## DOCX（テキスト資料）

| 順序 | ファイル | 用途 |
|------|----------|------|
| 1 | `Manuscript_IJEHR_20260628.docx` | **主原稿**（CSE引用・著者情報付きタイトルページ） |
| 2 | `Supplementary_Tables_IJEHR_20260628.docx` | **補足表**（Table S1 相関行列、Table S2 層別・交互作用） |
| — | `CoverLetter_IJEHR_20260628.docx` | カバーレター（Submission Portal テキスト欄に貼り付け） |
| — | `TitlePage_IJEHR_20260628.docx` | 著者情報・語数（ポータル入力参照用） |
| — | `Author_Bios_IJEHR_20260628.docx` | **Biographical note**（各著者 ≤200 語、IJEHR 必須） |
| — | `Declarations_IJEHR_20260628.docx` | Declarations 各項目（ポータルフォームへのコピー用） |

## 図（PNG、300 dpi カラー）

| 順序 | ファイル | 用途 |
|------|----------|------|
| 3 | `Fig1.png` | Figure 1 — Greenspace ratio choropleth |
| 4 | `Fig2.png` | Figure 2 — Prescription rate choropleth |
| 5 | `Fig3.png` | Figure 3 — LISA cluster map |

## 参照 PDF

| ファイル | 用途 |
|----------|------|
| `Submit to International Journal of Environmental Health Research.pdf` | IJEHR 投稿規定（Taylor & Francis） |

## 再生成コマンド（DOCX 直接修正）

```powershell
Set-Location 04_Manuscripts
python edit_manuscript_IJEHR_docx.py
python fix_IJEHR_docx_cleanup.py
python validate_IJEHR_limits.py
```

**ベースファイル:** `Not_All_Environmental_Indicators_Travel_20260627.docx`  
**編集スクリプト:** `edit_manuscript_IJEHR_docx.py`（IJEHR 向け一括修正）、`fix_IJEHR_docx_cleanup.py`（残存段落の除去）

> QMD レンダリングではなく、上記ベース DOCX を直接修正して `Manuscript_IJEHR_20260628.docx` を生成します。

詳細チェックリスト: `IJEHR_Submission_Workflow_20260628.md`

## 制限適合（検証済み 2026-06-28）

| 項目 | 要件 | 現状 |
|------|------|------|
| 本文語数 | ≤3,500 | 約 2,490 ✅ |
| Abstract | 非構造化 200 語 | 約 159 ✅ |
| Keywords | 3–5 | 5 ✅ |
| 表＋図（本文） | ≤6 | 6（3表+3図）✅ |
| References | ≤35 | 28 ✅ |
| 引用スタイル | CSE (T&F) | `cse.csl` ✅ |
| 日本語 | なし | 0 ✅ |
