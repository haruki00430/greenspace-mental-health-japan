# 生成AI・エージェント利用開示（論文別）

> 本ファイルは [00_Docs/templates/AI_USE_DISCLOSURE.template.md](../../../00_Docs/templates/AI_USE_DISCLOSURE.template.md) に基づく。運用は [CIRCS_NDB_MANUSCRIPT_AI_RULEBOOK.md](../../../00_Docs/07_Setup/CIRCS_NDB_MANUSCRIPT_AI_RULEBOOK.md) を参照。

---

## メタデータ

| 項目 | 内容 |
|------|------|
| 論文仮題 | 緑地環境と精神科処方薬の地域分布に関する空間疫学研究（都市緑地の逆説の検証） |
| 論文仮題（英語） | Urban greenspace paradox: ecological and spatial analysis of greenspace and psychotropic prescribing |
| プロジェクトパス | `projects/NDB_XXX_greenspace_mental_health/` |
| 対象誌（候補） | （README・原稿に準拠し追記） |
| 最終更新日 | 2026-04-08 |
| 記録責任者 | 通信著者（`Manuscript_greenspace_mental_health.qmd` の YAML `author` と同一。投稿前に実名へ） |

**原稿の正本**: `04_Manuscripts/Manuscript_greenspace_mental_health.qmd`（旧版 `_old` 等がある場合は投稿用1本に整理）

---

## 使用ツール一覧

| ツール・サービス | 区分 | モデル・バージョン（分かる範囲） | 主な用途 |
|------------------|------|----------------------------------|----------|
| Cursor | クラウドエージェント（設定依存） | 利用時点のエージェントモデル | 二次医療圏パネル・空間回帰・Quarto の支援 |
| LM Studio 等 | ローカル | — | 使用時は追記 |

**注**: AIを著者にしない。

---

## 研究段階別の利用

### 1. データ整備・ETL・スクリプト生成

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| （追記） | Cursor 等 | 緑地・処方・SES・GIS 結合、空間重み | [README.md](../README.md) |

### 2. 探索的スクリーニング／ローカルLLM

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| — | — | **該当なし**（用いた場合は追記） |  |

### 3. 確証的分析・可視化（空間回帰等）

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| （追記） | Cursor 等 | OLS・SLM・SEM 等 | `03_Analysis/` 等 |

### 4. 原稿

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| （追記） | Cursor 等 | Quarto 推敲 |  |

### 5. 参考文献

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| （追記） | Cursor 等 | `references.bib` |  |

---

## データ境界

### 外部クラウドLLMに**送らなかった**もの

- [x] NDB 生データの実数値・スクリーンショット
- [x] 二次医療圏の細集計の無制限な貼付

### 送ったもの（機微度が低い範囲）

| 種別 | 例 |
|------|-----|
| メタデータ・コード | 列名、スクリプト、パス |

### ローカルLLMに入力したもの

| 種別 | 例 |
|------|-----|
| （追記） |  |

---

## 人間による検証

| 段階 | 確認内容 | 実施者 | 日付 |
|------|----------|--------|------|
| コード・数値・引用・解釈 | 空間モデル選択・逆説の解釈の妥当性 | 著者 | （追記） |

---

## 投稿用短文ドラフト

### 日本語（案）

本研究の原稿作成および解析に生成AI支援ツールを用いた。空間モデル・解釈・結論は著者が検証した。AIは著者としていない。

### English (draft)

The authors used AI-assisted tools, verified spatial analysis and interpretation, and accept full responsibility. AI was not listed as an author.

---

## 変更履歴

| 日付 | 変更内容 |
|------|----------|
| 2026-04-08 | 初版（プロジェクト一括整備） |
