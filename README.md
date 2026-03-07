# NDB_XXX_greenspace_mental_health

**緑地環境と精神保健の空間疫学研究**

## プロジェクト概要

### 研究タイトル
**「緑地環境と精神科処方薬の地域分布に関する空間疫学研究：都市緑地の逆説（Urban Greenspace Paradox）の検証」**

**"The Urban Greenspace Paradox: An Ecological and Spatial Analysis of Natural Environments and Psychotropic Drug Prescriptions in Japan"**

### 研究の目的
二次医療圏別の緑地率（公園・森林等）と精神科処方薬（抗うつ薬・抗不安薬・睡眠薬）の処方動向との関連を、医療提供体制・社会経済要因を調整した上で、空間統計手法（SDM等）を用いて評価し、逆説的関連の有無を検証する。

### 研究デザイン
- **研究タイプ**: 横断的空間疫学研究（Ecological study）
- **分析単位**: 二次医療圏（N=335）
- **対象期間**: 2020年度（令和2年度）
- **統計手法**: 空間回帰分析（OLS、空間ラグモデル、空間誤差モデル）

---

## データソース

| カテゴリ | データ名 | 提供機関 | 用途 |
|---------|---------|---------|------|
| **アウトカム** | NDB処方薬データ | 厚生労働省 | 精神科処方薬処方量 |
| **曝露** | 国土数値情報（土地利用） | 国土交通省 | 緑地率計算 |
| **調整変数** | 国勢調査 | 総務省 | 失業率、高齢化率、単身世帯割合 |
| | 市町村税課税状況等の調 | 総務省 | 1人あたり課税対象所得 |
| | 医療施設調査・医師数統計 | 厚生労働省 | 精神科診療所密度、精神科医師数 |
| | 過去の気象データ | 気象庁 | 年間日照時間 |
| **空間データ** | 二次医療圏データ（A38） | 国土交通省 | ポリゴン、人口 |

---

## ディレクトリ構造

```
NDB_XXX_greenspace_mental_health/
├── README.md                    # このファイル
├── config/
│   └── config.yaml              # プロジェクト設定
├── data/
│   ├── raw/                     # 生データ（ダウンロードしたまま）
│   ├── interim/                 # 前処理済み中間データ
│   └── processed/               # 解析用最終データセット
├── 03_Analysis/
│   └── scripts/                 # 解析スクリプト（番号順）
│       ├── 01_ndb_data_extraction.py
│       ├── 02_greenspace_calculation.py
│       ├── 03_socioeconomic_integration.py
│       ├── 04_dataset_merge.py
│       ├── 05_descriptive_stats.py
│       ├── 06_spatial_autocorrelation.py
│       ├── 07_ols_regression.py
│       ├── 08_spatial_regression.py
│       ├── 09_sensitivity_analysis.py
│       └── 10_figure_generation.py
├── results/
│   ├── figures/                 # 図（PNG, PDF）
│   └── tables/                  # 表（CSV, TEX）
├── docs/
│   ├── research_protocol.md     # 研究計画書（詳細版）
│   ├── phase_summary_report.md  # フェーズ要約レポート
│   └── execution_guide.md       # 実行手順書
└── 04_Manuscripts/
    ├── Manuscript_greenspace_mental_health.qmd  # Quarto原稿
    ├── references.bib           # 文献管理（BibTeX）
    └── vancouver.csl            # 引用スタイル

```

---

## 研究の進捗状況

### Phase 1: データ収集・前処理（Week 1-2）
- [ ] NDB処方薬データ抽出
- [ ] 緑地率データ作成（GIS処理）
- [ ] 社会経済データ統合（e-Stat）
- [ ] 気象データ統合（気象庁）
- [ ] 最終データセット作成 → `data/processed/analysis_dataset.csv`

### Phase 2: 記述統計・空間探索的分析（Week 3）
- [ ] 記述統計（平均、SD、範囲）
- [ ] コロプレスマップ作成（緑地率、処方薬）
- [ ] Global Moran's I 計算
- [ ] Local Moran's I（ホットスポット検出）

### Phase 3: 空間回帰分析（Week 4-5）
- [ ] OLS回帰
- [ ] 空間診断（LM tests）
- [ ] 空間ラグモデル（SLM）
- [ ] 空間誤差モデル（SEM）
- [ ] 空間ダービンモデル（SDM）
- [ ] モデル比較（AIC/BIC/LR test）

### Phase 4: 感度分析（Week 6）
- [ ] 緑地の質による層別解析（公園 vs 森林）
- [ ] 交互作用検討（単身世帯率、医療アクセス）
- [ ] 層別解析（都市vs地方）
- [ ] ロバスト性チェック

### Phase 5: 可視化・レポート（Week 7）
- [ ] 全図表作成
- [ ] 要約レポート執筆

### Phase 6: 論文執筆（Week 8-10）
- [ ] Quarto原稿作成
- [ ] 文献収集・引用
- [ ] HTML/DOCX出力

**目標投稿日**: 2026年5月31日

---

## 主要な仮説

1. **主仮説**: 緑地率が高い二次医療圏では、医療提供体制および社会経済要因の交絡を調整した後においても、精神科処方薬の処方動向に逆説的な増加（あるいは質のによる異質性）が観察される（The Urban Greenspace Paradox）

2. **副次仮説**:
   - 精神科処方薬の分布には正の空間的自己相関が存在する（Moran's I > 0, p < 0.05）
   - 緑地の性質（整備された都市公園 vs 未整備の森林）によって処方動向への影響が異なる
   - 隣接圏域の緑地や医療資源の豊富さが、当該圏域の処方量に波及効果をもたらす（SDMによる検証）

---

## 期待される成果

### 学術的貢献
- 環境疫学と精神保健の融合領域における新規エビデンス
- 日本初の二次医療圏単位×空間統計×NDBデータの統合研究
- 都市計画（緑地整備）のエビデンスベース強化

### 政策的インパクト
- **厚生労働省**: 精神保健施策における環境介入の重要性を示唆
- **国土交通省**: 都市緑地法・都市公園法の改正根拠
- **地方自治体**: 公園整備・緑地保全の優先順位決定

### 投稿候補ジャーナル
- Environmental Research（IF: 8.3, Q1）
- Health & Place（IF: 4.8, Q1）
- Preventive Medicine（IF: 4.4, Q1）
- Journal of Epidemiology（IF: 3.0, Q2）

---

## 環境構築

### 必要なPythonパッケージ

```bash
# 仮想環境作成・有効化
python -m venv .venv
.venv\Scripts\activate  # Windows

# パッケージインストール
pip install pandas geopandas numpy scipy statsmodels \
            libpysal esda spreg matplotlib seaborn folium \
            openpyxl requests pyyaml
```

### 詳細な依存関係
`requirements.txt` を参照

---

## 使用方法

### 1. データ取得
```bash
# NDBデータ: 厚労省サイトから手動ダウンロード
# 国土数値情報: スクリプトで自動ダウンロード（予定）
python 03_Analysis/scripts/00_download_gsi_data.py
```

### 2. データ前処理
```bash
# 順番に実行
python 03_Analysis/scripts/01_ndb_data_extraction.py
python 03_Analysis/scripts/02_greenspace_calculation.py
python 03_Analysis/scripts/03_socioeconomic_integration.py
python 03_Analysis/scripts/04_dataset_merge.py
```

### 3. 解析実行
```bash
python 03_Analysis/scripts/05_descriptive_stats.py
python 03_Analysis/scripts/06_spatial_autocorrelation.py
python 03_Analysis/scripts/07_ols_regression.py
python 03_Analysis/scripts/08_spatial_regression.py
```

### 4. 図表生成
```bash
python 03_Analysis/scripts/10_figure_generation.py
```

### 5. 論文レンダリング
```bash
cd 04_Manuscripts
quarto render Manuscript_greenspace_mental_health.qmd --to html
quarto render Manuscript_greenspace_mental_health.qmd --to docx
```

---

## 重要なファイル

| ファイル | 説明 |
|---------|------|
| `docs/research_protocol.md` | 詳細な研究計画書（11章構成） |
| `config/config.yaml` | プロジェクト設定（データパス、変数定義） |
| `data/processed/analysis_dataset.csv` | 最終解析データセット（N=335） |
| `results/tables/table2_spatial_regression_results.csv` | 主要結果（OLS/SLM/SEM） |
| `04_Manuscripts/Manuscript_greenspace_mental_health.qmd` | 論文原稿 |

---

## 既存プロジェクトからの応用

本プロジェクトは以下の既存研究の手法を応用しています：

| 既存プロジェクト | 応用した手法 |
|----------------|-------------|
| **NDB_XXX_slope_fracture** | DEM加重平均計算、OLS回帰、結果可視化 |
| **NDB_AF_Anticoagulation_Spatial** | Queen contiguity空間重み行列、SLM/SEM、Moran's I |
| **NDB_XXX_metabo_cascade** | Mediation分析、交互作用検討 |

---

## ライセンス

本プロジェクトは研究目的で作成されています。
データソースのライセンスに従い、適切に引用してください。

---

## 連絡先

**研究責任者**: TBD
**作成日**: 2026年2月22日
**最終更新**: 2026年2月22日

---

## 参考文献

### 先行研究（緑地と精神保健）
1. Gascon M, et al. (2015). Mental health benefits of long-term exposure to residential green and blue spaces. *International Journal of Environmental Research and Public Health*, 12(4), 4354-4379.
2. Houlden V, et al. (2018). The relationship between greenspace and the mental wellbeing of adults: A systematic review. *PLoS ONE*, 13(9), e0203000.

### 空間疫学手法
3. Anselin L. (1988). Spatial Econometrics: Methods and Models. Springer.
4. Ward MD, Gleditsch KS. (2008). Spatial Regression Models. Sage Publications.

### NDB関連論文
5. [既存のNDB論文を追加予定]

---

**次のアクション**: Phase 1開始 → NDB薬剤コード特定
