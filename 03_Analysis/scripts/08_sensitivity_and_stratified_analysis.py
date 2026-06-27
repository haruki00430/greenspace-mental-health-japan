# -*- coding: utf-8 -*-
"""
Script 08: Sensitivity and Stratified Analyses
===============================================
Evaluates robustness of main findings from Script 07 through multiple
sensitivity specifications and urban/rural stratified analyses.

Steps:
  1. Sensitivity analyses
       - Outlier diagnostics (residual plots, Cook's D)
       - Exclusion of geographically isolated prefectures (Hokkaido, Okinawa)
       - Identification of high-influence observations
  2. Stratified analyses
       - Urban vs. rural (split at median population density)
       - High vs. low aging rate (split at median)
       - High vs. low education level (split at median college rate)
  3. Interaction analyses
       - greenspace × aging_rate
       - greenspace × population density

Inputs:
  - data/processed/spatial_analysis_data.geojson

Outputs:
  - results/sensitivity_analysis_results.txt
  - results/stratified_analysis_results.txt
  - results/figures/residual_diagnostics.png
  - results/figures/stratified_coefficients.png
  - results/figures/interaction_plot.png

------------------------------------------------------------
スクリプト08: 感度分析と層別解析
Phase 4 — 外れ値診断・都市農村層別・交互作用検定
------------------------------------------------------------
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from libpysal.weights import Queen
from spreg import OLS, ML_Error
import seaborn as sns
from scipy import stats

# ============================================================
# パス設定
# ============================================================

GREENSPACE_PROJECT = Path(__file__).resolve().parents[2]

DATA_DIR = GREENSPACE_PROJECT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = GREENSPACE_PROJECT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

# 入力ファイル
SPATIAL_DATA_GEOJSON = PROCESSED_DIR / "spatial_analysis_data.geojson"

# 出力ファイル
SENSITIVITY_RESULTS = RESULTS_DIR / "sensitivity_analysis_results.txt"
STRATIFIED_RESULTS = RESULTS_DIR / "stratified_analysis_results.txt"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 日本語フォント設定
# ============================================================

def set_japanese_font():
    """日本語フォント設定（Windows環境）"""
    try:
        plt.rcParams['font.family'] = 'Meiryo'
    except:
        try:
            plt.rcParams['font.family'] = 'MS Gothic'
        except:
            print("[警告] 日本語フォントが見つかりません。")
    plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# データ読み込みと前処理
# ============================================================

def load_spatial_data():
    """空間データの読み込み"""
    print("=" * 80)
    print(" 感度分析と層別解析")
    print("=" * 80)

    print("\n[STEP 1] 空間データ読み込み")
    gdf = gpd.read_file(SPATIAL_DATA_GEOJSON)
    print(f"  読み込み完了: {len(gdf)}都道府県")

    return gdf

def prepare_regression_data(gdf):
    """回帰分析用のデータ準備"""
    outcome_var = 'prescription_per_100k'
    exposure_var = 'greenspace_ratio_percent'
    covariate_vars = ['aging_rate', 'unemployment_rate', 'income_per_capita', 'single_household_rate', 'psych_clinic_density']

    all_vars = [outcome_var, exposure_var] + covariate_vars

    # 欠損値除外
    gdf = gdf.dropna(subset=all_vars)

    y = gdf[outcome_var].values.reshape(-1, 1)
    X_vars = [exposure_var] + covariate_vars
    X = gdf[X_vars].values

    return y, X, X_vars, gdf, covariate_vars

# ============================================================
# 1. 感度分析: 外れ値診断
# ============================================================

def sensitivity_outlier_diagnostics(gdf, y, X, var_names):
    """外れ値診断と影響力分析"""

    print("\n" + "=" * 80)
    print(" 1. 外れ値診断")
    print("=" * 80)

    # OLS実行（空間重み行列なし、診断用）
    ols = OLS(y, X, name_y='prescription_per_100k', name_x=var_names)

    # 残差
    residuals = ols.u

    # 標準化残差
    std_residuals = residuals / np.std(residuals)

    # 外れ値候補（|標準化残差| > 2）
    outliers = np.where(np.abs(std_residuals) > 2)[0]

    print(f"\n[外れ値候補] 標準化残差 > 2: {len(outliers)}件")
    if len(outliers) > 0:
        for idx in outliers:
            pref = gdf.iloc[idx]['prefecture_name']
            std_res = std_residuals[idx][0]
            print(f"  {pref}: 標準化残差 = {std_res:.3f}")

    # 残差プロット作成
    create_residual_diagnostics_plot(gdf, residuals, std_residuals, var_names)

    return outliers

def create_residual_diagnostics_plot(gdf, residuals, std_residuals, var_names):
    """残差診断プロット"""

    print("\n[残差診断プロット作成中...]")

    set_japanese_font()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. 残差 vs 予測値
    fitted = gdf['prescription_per_100k'].values - residuals.flatten()
    axes[0, 0].scatter(fitted, residuals, alpha=0.6, edgecolor='black')
    axes[0, 0].axhline(0, color='red', linestyle='--', linewidth=1.5)
    axes[0, 0].set_xlabel('予測値', fontsize=11)
    axes[0, 0].set_ylabel('残差', fontsize=11)
    axes[0, 0].set_title('残差 vs 予測値', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Q-Qプロット
    stats.probplot(residuals.flatten(), dist="norm", plot=axes[0, 1])
    axes[0, 1].set_title('Q-Q プロット（正規性診断）', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)

    # 3. 標準化残差のヒストグラム
    axes[1, 0].hist(std_residuals, bins=15, edgecolor='black', alpha=0.7, color='skyblue')
    axes[1, 0].axvline(-2, color='red', linestyle='--', linewidth=1.5, label='±2 SD')
    axes[1, 0].axvline(2, color='red', linestyle='--', linewidth=1.5)
    axes[1, 0].set_xlabel('標準化残差', fontsize=11)
    axes[1, 0].set_ylabel('度数', fontsize=11)
    axes[1, 0].set_title('標準化残差の分布', fontsize=12, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # 4. 残差の空間分布（都道府県名付き）
    axes[1, 1].scatter(range(len(residuals)), residuals, alpha=0.6, edgecolor='black')
    axes[1, 1].axhline(0, color='red', linestyle='--', linewidth=1.5)
    axes[1, 1].set_xlabel('都道府県インデックス', fontsize=11)
    axes[1, 1].set_ylabel('残差', fontsize=11)
    axes[1, 1].set_title('残差の分布（都道府県順）', fontsize=12, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "residual_diagnostics.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存完了: {FIGURES_DIR / 'residual_diagnostics.png'}")

# ============================================================
# 2. 感度分析: 孤島除外
# ============================================================

def sensitivity_exclude_islands(gdf, var_names):
    """孤島（北海道・沖縄）を除外した分析"""

    print("\n" + "=" * 80)
    print(" 2. 孤島除外分析")
    print("=" * 80)

    # 孤島を除外
    gdf_no_islands = gdf[~gdf['prefecture_code'].isin(['01', '47'])].copy()
    print(f"\n[除外] 北海道、沖縄県")
    print(f"  サンプルサイズ: N={len(gdf_no_islands)}都道府県")

    # データ準備
    y_no_islands = gdf_no_islands['prescription_per_100k'].values.reshape(-1, 1)
    X_no_islands = gdf_no_islands[var_names].values

    # 空間重み行列構築
    w_no_islands = Queen.from_dataframe(gdf_no_islands, ids='prefecture_code')
    w_no_islands.transform = 'r'

    # SEM実行
    sem_no_islands = ML_Error(y_no_islands, X_no_islands, w=w_no_islands,
                               name_y='prescription_per_100k', name_x=var_names)

    print("\n[SEM結果（孤島除外）]")
    print(f"  Pseudo-R-squared: {sem_no_islands.pr2:.4f}")
    print(f"  AIC: {sem_no_islands.aic:.2f}")
    print(f"  Spatial error parameter (lambda): {sem_no_islands.lam:.4f}")

    print("\n[係数推定値]")
    for i, var in enumerate(var_names):
        coef = sem_no_islands.betas[i+1][0]
        z_stat = sem_no_islands.z_stat[i+1][0]
        p_val = sem_no_islands.z_stat[i+1][1]
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"  {var:30s}: beta={coef:8.4f}, z={z_stat:6.3f}, p={p_val:.4f} {sig}")

    return sem_no_islands

# ============================================================
# 2b. 感度分析: 緑地の種類別（公園 vs 森林）
# ============================================================

def sensitivity_greenspace_types(gdf, covariate_vars):
    """公園率と森林率をそれぞれ主要な暴露変数とした分析"""
    
    print("\n" + "=" * 80)
    print(" 2b. 緑地の種類（公園 vs 森林）別分析")
    print("=" * 80)
    
    print("\n[STEP 2b] 公園率と森林率の計算")
    gdf['park_ratio_percent'] = (gdf['park_area_km2'] / gdf['total_area_km2']) * 100
    gdf['forest_ratio_percent'] = (gdf['forest_area_km2'] / gdf['total_area_km2']) * 100

    # 欠損値除外（公園・森林率を含む）
    all_vars = ['prescription_per_100k', 'park_ratio_percent', 'forest_ratio_percent'] + covariate_vars
    gdf = gdf.dropna(subset=all_vars)
    
    y = gdf['prescription_per_100k'].values.reshape(-1, 1)
    
    # 公園
    X_park_vars = ['park_ratio_percent'] + covariate_vars
    X_park = gdf[X_park_vars].values
    ols_park = OLS(y, X_park, name_y='prescription_per_100k', name_x=X_park_vars)
    print(f"\n[公園率モデル]")
    print(f"  park_ratio_percent: beta={ols_park.betas[1][0]:8.4f}, p={ols_park.t_stat[1][1]:.4f}")
    
    # 森林
    X_forest_vars = ['forest_ratio_percent'] + covariate_vars
    X_forest = gdf[X_forest_vars].values
    ols_forest = OLS(y, X_forest, name_y='prescription_per_100k', name_x=X_forest_vars)
    print(f"\n[森林率モデル]")
    print(f"  forest_ratio_percent: beta={ols_forest.betas[1][0]:8.4f}, p={ols_forest.t_stat[1][1]:.4f}")
    
    return ols_park, ols_forest

# ============================================================
# 3. 層別解析
# ============================================================

def stratified_analysis(gdf, var_names):
    """層別解析（都市/農村、高齢化、教育水準）"""

    print("\n" + "=" * 80)
    print(" 3. 層別解析")
    print("=" * 80)

    results = []

    # 3a. 都市/農村層別（人口密度の中央値）
    print("\n[3a] 都市/農村層別（人口密度）")
    median_density = gdf['pop_density'].median()
    print(f"  人口密度の中央値: {median_density:.2f} 人/km2")

    gdf_urban = gdf[gdf['pop_density'] >= median_density].copy()
    gdf_rural = gdf[gdf['pop_density'] < median_density].copy()

    print(f"  都市部: N={len(gdf_urban)}都道府県")
    print(f"  農村部: N={len(gdf_rural)}都道府県")

    # 都市部
    if len(gdf_urban) >= 10:  # 最低サンプルサイズ
        y_urban = gdf_urban['prescription_per_100k'].values.reshape(-1, 1)
        X_urban = gdf_urban[var_names].values
        ols_urban = OLS(y_urban, X_urban, name_y='prescription_per_100k', name_x=var_names)

        greenspace_coef_urban = ols_urban.betas[1][0]
        greenspace_p_urban = ols_urban.t_stat[1][1]

        print(f"  都市部 greenspace_ratio_percent: beta={greenspace_coef_urban:.4f}, p={greenspace_p_urban:.4f}")
        results.append(('Urban', greenspace_coef_urban, greenspace_p_urban, len(gdf_urban)))

    # 農村部
    if len(gdf_rural) >= 10:
        y_rural = gdf_rural['prescription_per_100k'].values.reshape(-1, 1)
        X_rural = gdf_rural[var_names].values
        ols_rural = OLS(y_rural, X_rural, name_y='prescription_per_100k', name_x=var_names)

        greenspace_coef_rural = ols_rural.betas[1][0]
        greenspace_p_rural = ols_rural.t_stat[1][1]

        print(f"  農村部 greenspace_ratio_percent: beta={greenspace_coef_rural:.4f}, p={greenspace_p_rural:.4f}")
        results.append(('Rural', greenspace_coef_rural, greenspace_p_rural, len(gdf_rural)))

    # 3b. 高齢化層別
    print("\n[3b] 高齢化進行度層別")
    median_aging = gdf['aging_rate'].median()
    print(f"  高齢化率の中央値: {median_aging:.2f}%")

    gdf_high_aging = gdf[gdf['aging_rate'] >= median_aging].copy()
    gdf_low_aging = gdf[gdf['aging_rate'] < median_aging].copy()

    print(f"  高齢化進行地域: N={len(gdf_high_aging)}都道府県")
    print(f"  若年地域: N={len(gdf_low_aging)}都道府県")

    # 高齢化進行地域
    if len(gdf_high_aging) >= 10:
        y_high_aging = gdf_high_aging['prescription_per_100k'].values.reshape(-1, 1)
        X_high_aging = gdf_high_aging[var_names].values
        ols_high_aging = OLS(y_high_aging, X_high_aging, name_y='prescription_per_100k', name_x=var_names)

        greenspace_coef_high = ols_high_aging.betas[1][0]
        greenspace_p_high = ols_high_aging.t_stat[1][1]

        print(f"  高齢化進行 greenspace_ratio_percent: beta={greenspace_coef_high:.4f}, p={greenspace_p_high:.4f}")
        results.append(('High Aging', greenspace_coef_high, greenspace_p_high, len(gdf_high_aging)))

    # 若年地域
    if len(gdf_low_aging) >= 10:
        y_low_aging = gdf_low_aging['prescription_per_100k'].values.reshape(-1, 1)
        X_low_aging = gdf_low_aging[var_names].values
        ols_low_aging = OLS(y_low_aging, X_low_aging, name_y='prescription_per_100k', name_x=var_names)

        greenspace_coef_low = ols_low_aging.betas[1][0]
        greenspace_p_low = ols_low_aging.t_stat[1][1]

        print(f"  若年地域 greenspace_ratio_percent: beta={greenspace_coef_low:.4f}, p={greenspace_p_low:.4f}")
        results.append(('Low Aging', greenspace_coef_low, greenspace_p_low, len(gdf_low_aging)))

    # 3c. 教育水準層別
    print("\n[3c] 教育水準層別（大卒率）")
    median_education = gdf['college_graduate_rate'].median()
    print(f"  大卒率の中央値: {median_education:.2f}%")

    gdf_high_edu = gdf[gdf['college_graduate_rate'] >= median_education].copy()
    gdf_low_edu = gdf[gdf['college_graduate_rate'] < median_education].copy()

    print(f"  高教育水準: N={len(gdf_high_edu)}都道府県")
    print(f"  低教育水準: N={len(gdf_low_edu)}都道府県")

    # 高教育水準
    if len(gdf_high_edu) >= 10:
        y_high_edu = gdf_high_edu['prescription_per_100k'].values.reshape(-1, 1)
        X_high_edu = gdf_high_edu[var_names].values
        ols_high_edu = OLS(y_high_edu, X_high_edu, name_y='prescription_per_100k', name_x=var_names)

        greenspace_coef_high_edu = ols_high_edu.betas[1][0]
        greenspace_p_high_edu = ols_high_edu.t_stat[1][1]

        print(f"  高教育 greenspace_ratio_percent: beta={greenspace_coef_high_edu:.4f}, p={greenspace_p_high_edu:.4f}")
        results.append(('High Education', greenspace_coef_high_edu, greenspace_p_high_edu, len(gdf_high_edu)))

    # 低教育水準
    if len(gdf_low_edu) >= 10:
        y_low_edu = gdf_low_edu['prescription_per_100k'].values.reshape(-1, 1)
        X_low_edu = gdf_low_edu[var_names].values
        ols_low_edu = OLS(y_low_edu, X_low_edu, name_y='prescription_per_100k', name_x=var_names)

        greenspace_coef_low_edu = ols_low_edu.betas[1][0]
        greenspace_p_low_edu = ols_low_edu.t_stat[1][1]

        print(f"  低教育 greenspace_ratio_percent: beta={greenspace_coef_low_edu:.4f}, p={greenspace_p_low_edu:.4f}")
        results.append(('Low Education', greenspace_coef_low_edu, greenspace_p_low_edu, len(gdf_low_edu)))

    return results

def create_stratified_coefficients_plot(stratified_results):
    """層別解析の係数プロット"""

    print("\n[層別解析係数プロット作成中...]")

    set_japanese_font()

    df_strat = pd.DataFrame(stratified_results, columns=['Stratum', 'Coefficient', 'P-value', 'N'])

    # 日本語ラベルマッピング
    label_map = {
        'Urban': '都市部',
        'Rural': '農村部',
        'High Aging': '高齢化進行',
        'Low Aging': '若年地域',
        'High Education': '高教育水準',
        'Low Education': '低教育水準'
    }
    df_strat['Stratum_JP'] = df_strat['Stratum'].map(label_map)

    fig, ax = plt.subplots(figsize=(10, 8))

    # 有意性で色分け
    colors = ['red' if p < 0.05 else 'blue' if p < 0.1 else 'gray' for p in df_strat['P-value']]

    y_pos = np.arange(len(df_strat))
    ax.barh(y_pos, df_strat['Coefficient'], color=colors, edgecolor='black', alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{row['Stratum_JP']} (N={row['N']})" for _, row in df_strat.iterrows()])
    ax.set_xlabel('緑地率の係数推定値 (β)', fontsize=12)
    ax.set_title('層別解析：緑地率と処方薬量の関連', fontsize=14, fontweight='bold')
    ax.axvline(0, color='black', linewidth=1.5, linestyle='--')
    ax.grid(True, alpha=0.3, axis='x')

    # 凡例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='red', edgecolor='black', label='p<0.05'),
        Patch(facecolor='blue', edgecolor='black', label='p<0.10'),
        Patch(facecolor='gray', edgecolor='black', label='p≥0.10 (非有意)')
    ]
    ax.legend(handles=legend_elements, loc='lower right')

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "stratified_coefficients.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存完了: {FIGURES_DIR / 'stratified_coefficients.png'}")

# ============================================================
# 4. 交互作用分析
# ============================================================

def interaction_analysis(gdf, var_names):
    """交互作用項の追加分析"""

    print("\n" + "=" * 80)
    print(" 4. 交互作用分析")
    print("=" * 80)

    # greenspace × aging_rate 交互作用
    print("\n[4a] greenspace_ratio_percent × aging_rate")

    gdf['greenspace_x_aging'] = gdf['greenspace_ratio_percent'] * gdf['aging_rate']

    y = gdf['prescription_per_100k'].values.reshape(-1, 1)

    # 交互作用項を含む説明変数
    X_vars_interaction = var_names + ['greenspace_x_aging']
    X_interaction = gdf[X_vars_interaction].values

    ols_interaction = OLS(y, X_interaction, name_y='prescription_per_100k', name_x=X_vars_interaction)

    print(f"  交互作用項の係数:")
    interaction_idx = len(var_names) + 1  # インターセプト + 既存変数 + 交互作用
    interaction_coef = ols_interaction.betas[interaction_idx][0]
    interaction_se = ols_interaction.std_err[interaction_idx]
    interaction_t = ols_interaction.t_stat[interaction_idx][0]
    interaction_p = ols_interaction.t_stat[interaction_idx][1]
    sig = "***" if interaction_p < 0.001 else "**" if interaction_p < 0.01 else "*" if interaction_p < 0.05 else ""

    print(f"    greenspace_x_aging: beta={interaction_coef:.4f}, SE={interaction_se:.4f}, t={interaction_t:.3f}, p={interaction_p:.4f} {sig}")

    # greenspace × single_household_rate 交互作用
    print("\n[4b] greenspace_ratio_percent × single_household_rate")

    gdf['greenspace_x_single'] = gdf['greenspace_ratio_percent'] * gdf['single_household_rate']

    # 交互作用項を含む説明変数
    X_vars_interaction2 = var_names + ['greenspace_x_single']
    X_interaction2 = gdf[X_vars_interaction2].values

    ols_interaction2 = OLS(y, X_interaction2, name_y='prescription_per_100k', name_x=X_vars_interaction2)

    interaction_idx2 = len(var_names) + 1  # インターセプト + 既存変数 + 交互作用
    interaction_coef2 = ols_interaction2.betas[interaction_idx2][0]
    interaction_p2 = ols_interaction2.t_stat[interaction_idx2][1]
    sig2 = "***" if interaction_p2 < 0.001 else "**" if interaction_p2 < 0.01 else "*" if interaction_p2 < 0.05 else ""

    print(f"    greenspace_x_single: beta={interaction_coef2:.4f}, p={interaction_p2:.4f} {sig2}")

    # greenspace × urban_indicator 交互作用（都市/地方の二値変数）
    print("\n[4c] greenspace_ratio_percent × urban_indicator (Urban/Rural)")

    median_density = gdf['pop_density'].median()
    gdf['urban_indicator'] = (gdf['pop_density'] >= median_density).astype(int)
    gdf['greenspace_x_urban'] = gdf['greenspace_ratio_percent'] * gdf['urban_indicator']

    print(f"  人口密度の中央値: {median_density:.2f} 人/km2")
    print(f"  都市部（urban_indicator=1）: N={gdf['urban_indicator'].sum()}都道府県")
    print(f"  地方部（urban_indicator=0）: N={(1-gdf['urban_indicator']).sum()}都道府県")

    # 交互作用項を含む説明変数（urban_indicatorも独立変数として追加）
    X_vars_interaction3 = var_names + ['urban_indicator', 'greenspace_x_urban']
    X_interaction3 = gdf[X_vars_interaction3].values

    ols_interaction3 = OLS(y, X_interaction3, name_y='prescription_per_100k', name_x=X_vars_interaction3)

    interaction_idx3 = len(var_names) + 2  # インターセプト + 既存変数 + urban_indicator + 交互作用
    interaction_coef3 = ols_interaction3.betas[interaction_idx3][0]
    interaction_se3 = ols_interaction3.std_err[interaction_idx3]
    interaction_t3 = ols_interaction3.t_stat[interaction_idx3][0]
    interaction_p3 = ols_interaction3.t_stat[interaction_idx3][1]
    sig3 = "***" if interaction_p3 < 0.001 else "**" if interaction_p3 < 0.01 else "*" if interaction_p3 < 0.05 else ""

    print(f"  交互作用項の係数:")
    print(f"    greenspace_x_urban: beta={interaction_coef3:.4f}, SE={interaction_se3:.4f}, t={interaction_t3:.3f}, p={interaction_p3:.4f} {sig3}")

    # urban_indicator主効果も表示
    urban_main_idx = len(var_names) + 1
    urban_main_coef = ols_interaction3.betas[urban_main_idx][0]
    urban_main_p = ols_interaction3.t_stat[urban_main_idx][1]
    print(f"    urban_indicator (主効果): beta={urban_main_coef:.4f}, p={urban_main_p:.4f}")

    # greenspace × pop_density 交互作用（連続変数）
    print("\n[4d] greenspace_ratio_percent × pop_density (continuous)")

    gdf['greenspace_x_popdensity'] = gdf['greenspace_ratio_percent'] * gdf['pop_density']

    # 交互作用項を含む説明変数
    X_vars_interaction4 = var_names + ['greenspace_x_popdensity']
    X_interaction4 = gdf[X_vars_interaction4].values

    ols_interaction4 = OLS(y, X_interaction4, name_y='prescription_per_100k', name_x=X_vars_interaction4)

    interaction_idx4 = len(var_names) + 1  # インターセプト + 既存変数 + 交互作用
    interaction_coef4 = ols_interaction4.betas[interaction_idx4][0]
    interaction_se4 = ols_interaction4.std_err[interaction_idx4]
    interaction_t4 = ols_interaction4.t_stat[interaction_idx4][0]
    interaction_p4 = ols_interaction4.t_stat[interaction_idx4][1]
    sig4 = "***" if interaction_p4 < 0.001 else "**" if interaction_p4 < 0.01 else "*" if interaction_p4 < 0.05 else ""

    print(f"  交互作用項の係数:")
    print(f"    greenspace_x_popdensity: beta={interaction_coef4:.4f}, SE={interaction_se4:.4f}, t={interaction_t4:.3f}, p={interaction_p4:.4f} {sig4}")

    return ols_interaction, ols_interaction2, ols_interaction3, ols_interaction4

# ============================================================
# 結果の保存
# ============================================================

def save_results(outliers, sem_no_islands, ols_park, ols_forest, stratified_results, ols_interaction, ols_interaction2, ols_interaction3, ols_interaction4, gdf, var_names):
    """感度分析と層別解析の結果を保存"""

    print("\n[STEP 2] 結果保存")

    # 感度分析結果
    with open(SENSITIVITY_RESULTS, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(" 感度分析結果\n")
        f.write("=" * 80 + "\n\n")

        f.write("【1. 外れ値診断】\n")
        f.write(f"標準化残差 > 2 の都道府県: {len(outliers)}件\n")
        if len(outliers) > 0:
            for idx in outliers:
                pref = gdf.iloc[idx]['prefecture_name']
                f.write(f"  - {pref}\n")
        f.write("\n")

        f.write("【2. 孤島除外分析（北海道・沖縄を除く）】\n")
        f.write(f"サンプルサイズ: N={47-2}都道府県\n")
        f.write(f"Pseudo-R-squared: {sem_no_islands.pr2:.4f}\n")
        f.write(f"AIC: {sem_no_islands.aic:.2f}\n")
        f.write(f"Spatial error parameter (lambda): {sem_no_islands.lam:.4f}\n\n")

        f.write("係数推定値:\n")
        for i, var in enumerate(var_names):
            coef = sem_no_islands.betas[i+1][0]
            z_stat = sem_no_islands.z_stat[i+1][0]
            p_val = sem_no_islands.z_stat[i+1][1]
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            f.write(f"  {var}: beta={coef:.4f}, z={z_stat:.3f}, p={p_val:.4f} {sig}\n")
        f.write("\n")

        f.write("【3. 緑地の種類（公園 vs 森林）別モデル】\n")
        f.write("[公園率モデル]\n")
        idx = 1
        f.write(f"  park_ratio_percent: beta={ols_park.betas[idx][0]:.4f}, p={ols_park.t_stat[idx][1]:.4f}\n")
        f.write("[森林率モデル]\n")
        f.write(f"  forest_ratio_percent: beta={ols_forest.betas[idx][0]:.4f}, p={ols_forest.t_stat[idx][1]:.4f}\n\n")

    print(f"  保存完了: {SENSITIVITY_RESULTS}")

    # 層別解析結果
    with open(STRATIFIED_RESULTS, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(" 層別解析結果\n")
        f.write("=" * 80 + "\n\n")

        f.write("【greenspace_ratio_percentの係数（層別）】\n\n")
        for stratum, coef, p_val, n in stratified_results:
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            f.write(f"{stratum:20s} (N={n:2d}): beta={coef:8.4f}, p={p_val:.4f} {sig}\n")
        f.write("\n")

        f.write("【交互作用分析】\n")

        # 1. greenspace × aging_rate
        interaction_idx = len(var_names) + 1
        interaction_coef = ols_interaction.betas[interaction_idx][0]
        interaction_p = ols_interaction.t_stat[interaction_idx][1]
        sig = "***" if interaction_p < 0.001 else "**" if interaction_p < 0.01 else "*" if interaction_p < 0.05 else ""
        f.write(f"greenspace_ratio_percent × aging_rate: beta={interaction_coef:.4f}, p={interaction_p:.4f} {sig}\n")

        # 2. greenspace × single_household_rate
        interaction_coef2 = ols_interaction2.betas[interaction_idx][0]
        interaction_p2 = ols_interaction2.t_stat[interaction_idx][1]
        sig2 = "***" if interaction_p2 < 0.001 else "**" if interaction_p2 < 0.01 else "*" if interaction_p2 < 0.05 else ""
        f.write(f"greenspace_ratio_percent × single_household_rate: beta={interaction_coef2:.4f}, p={interaction_p2:.4f} {sig2}\n")

        # 3. greenspace × urban_indicator (NEW!)
        interaction_idx3 = len(var_names) + 2  # +urban_indicator +交互作用
        interaction_coef3 = ols_interaction3.betas[interaction_idx3][0]
        interaction_p3 = ols_interaction3.t_stat[interaction_idx3][1]
        sig3 = "***" if interaction_p3 < 0.001 else "**" if interaction_p3 < 0.01 else "*" if interaction_p3 < 0.05 else ""
        f.write(f"greenspace_ratio_percent × urban_indicator: beta={interaction_coef3:.4f}, p={interaction_p3:.4f} {sig3}\n")

        # 4. greenspace × pop_density (NEW!)
        interaction_idx4 = len(var_names) + 1
        interaction_coef4 = ols_interaction4.betas[interaction_idx4][0]
        interaction_p4 = ols_interaction4.t_stat[interaction_idx4][1]
        sig4 = "***" if interaction_p4 < 0.001 else "**" if interaction_p4 < 0.01 else "*" if interaction_p4 < 0.05 else ""
        f.write(f"greenspace_ratio_percent × pop_density: beta={interaction_coef4:.4f}, p={interaction_p4:.4f} {sig4}\n")

    print(f"  保存完了: {STRATIFIED_RESULTS}")

# ============================================================
# メイン実行
# ============================================================

if __name__ == "__main__":

    # データ読み込み
    gdf = load_spatial_data()

    # 回帰データ準備
    y, X, var_names, gdf, covariate_vars = prepare_regression_data(gdf)

    # 1. 外れ値診断
    outliers = sensitivity_outlier_diagnostics(gdf, y, X, var_names)

    # 2. 孤島除外分析
    sem_no_islands = sensitivity_exclude_islands(gdf, var_names)

    # 3. 層別解析
    stratified_results = stratified_analysis(gdf, var_names)

    # 層別解析プロット
    create_stratified_coefficients_plot(stratified_results)

    # 4. 交互作用分析
    ols_interaction, ols_interaction2, ols_interaction3, ols_interaction4 = interaction_analysis(gdf, var_names)

    # 5. 緑地の種類別モデル
    ols_park, ols_forest = sensitivity_greenspace_types(gdf, covariate_vars)

    # 結果保存
    save_results(outliers, sem_no_islands, ols_park, ols_forest, stratified_results, ols_interaction, ols_interaction2, ols_interaction3, ols_interaction4, gdf, var_names)

    print("\n" + "=" * 80)
    print(" 感度分析・層別解析 完了")
    print("=" * 80)
    print(f"\n出力ファイル:")
    print(f"  1. {SENSITIVITY_RESULTS}")
    print(f"  2. {STRATIFIED_RESULTS}")
    print(f"  3. {FIGURES_DIR / 'residual_diagnostics.png'}")
    print(f"  4. {FIGURES_DIR / 'stratified_coefficients.png'}")
    print("\n次のステップ: Phase 4（総合可視化と論文執筆）")
