# -*- coding: utf-8 -*-
"""
スクリプト07: 空間回帰分析

Phase 3の内容：
1. OLS回帰（ベースライン）
2. 空間診断（Lagrange Multiplier tests）
3. Spatial Lag Model (SLM)
4. Spatial Error Model (SEM)
5. Spatial Durbin Model (SDM)
6. モデル比較（AIC, Log-likelihood, Pseudo-R²）

モデル式:
prescription_per_100k ~ total_greenspace_ratio_percent + aging_rate + unemployment_rate +
                        income_per_capita + single_household_rate + psych_clinic_density

入力:
- data/processed/spatial_analysis_data.geojson（LISAデータ含む）

出力:
- results/regression_results.txt（回帰結果）
- results/model_comparison.csv（モデル比較表）
- results/figures/residual_plot_ols.png（OLS残差プロット）
- results/figures/residual_plot_slm.png（SLM残差プロット）
- results/figures/coefficients_comparison.png（係数比較図）
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from libpysal.weights import Queen, lag_spatial
from spreg import OLS, ML_Lag, ML_Error
import seaborn as sns

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
REGRESSION_RESULTS = RESULTS_DIR / "regression_results.txt"
MODEL_COMPARISON_CSV = RESULTS_DIR / "model_comparison.csv"

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
            print("[警告] 日本語フォントが見つかりません。文字化けする可能性があります。")

    plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# データ読み込みと前処理
# ============================================================

def load_spatial_data():
    """空間データの読み込み"""

    print("=" * 80)
    print(" Phase 3: 空間回帰分析")
    print("=" * 80)

    print("\n[STEP 1] 空間データ読み込み")
    gdf = gpd.read_file(SPATIAL_DATA_GEOJSON)
    print(f"  読み込み完了: {len(gdf)}都道府県")

    return gdf

def prepare_regression_data(gdf):
    """回帰分析用のデータ準備"""

    print("\n[STEP 2] 回帰分析用データ準備")

    # 変数リスト
    outcome_var = 'prescription_per_100k'
    exposure_var = 'greenspace_ratio_percent'
    covariate_vars = ['aging_rate', 'unemployment_rate', 'income_per_capita', 'psych_clinic_density']

    # すべての変数が存在するか確認
    all_vars = [outcome_var, exposure_var] + covariate_vars
    missing_vars = [v for v in all_vars if v not in gdf.columns]
    if missing_vars:
        raise ValueError(f"以下の変数が見つかりません: {missing_vars}")

    # 欠損値確認
    missing_counts = gdf[all_vars].isnull().sum()
    if missing_counts.sum() > 0:
        print("  [警告] 欠損値があります:")
        for var, count in missing_counts[missing_counts > 0].items():
            print(f"    {var}: {count}件")
        # 欠損値を除外
        gdf = gdf.dropna(subset=all_vars)
        print(f"  欠損値除外後: {len(gdf)}都道府県")

    # アウトカム（y）
    y = gdf[outcome_var].values.reshape(-1, 1)

    # 説明変数（X）：exposure + covariates
    X_vars = [exposure_var] + covariate_vars
    X = gdf[X_vars].values

    # 変数名リスト
    var_names = X_vars

    print(f"  アウトカム: {outcome_var}")
    print(f"  説明変数 (n={len(var_names)}):")
    for i, var in enumerate(var_names, 1):
        print(f"    {i}. {var}")

    return y, X, var_names, gdf

# ============================================================
# 空間重み行列の構築
# ============================================================

def create_spatial_weights(gdf):
    """Queen contiguity空間重み行列の構築"""

    print("\n[STEP 3] 空間重み行列構築")

    # Queen contiguity
    w = Queen.from_dataframe(gdf, ids='prefecture_code')

    # 孤島の確認
    islands = w.islands
    if islands:
        island_prefs = gdf[gdf['prefecture_code'].isin(islands)]['prefecture_name'].tolist()
        print(f"  [警告] 孤島: {', '.join(island_prefs)}")

    # 行標準化
    w.transform = 'r'
    print(f"  空間重み行列: {w.n}ノード, {w.s0}エッジ")

    return w

# ============================================================
# OLS回帰
# ============================================================

def run_ols_regression(y, X, var_names, w):
    """OLS回帰の実行"""

    print("\n" + "=" * 80)
    print(" OLS回帰分析")
    print("=" * 80)

    # OLS実行
    ols = OLS(y, X, w=w, name_y='prescription_per_100k', name_x=var_names, spat_diag=True)

    # 結果表示
    print("\n[OLS結果サマリー]")
    print(f"  R-squared: {ols.r2:.4f}")
    print(f"  Adjusted R-squared: {ols.ar2:.4f}")
    print(f"  AIC: {ols.aic:.2f}")
    print(f"  Log-likelihood: {ols.logll:.2f}")

    print("\n[係数推定値]")
    for i, var in enumerate(var_names):
        coef = ols.betas[i+1][0]  # +1はインターセプトをスキップ
        se = ols.std_err[i+1]
        t_stat = ols.t_stat[i+1][0]
        p_val = ols.t_stat[i+1][1]
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"  {var:30s}: β={coef:8.4f}, SE={se:.4f}, t={t_stat:6.3f}, p={p_val:.4f} {sig}")

    # 空間診断
    print("\n[空間診断（Lagrange Multiplier tests）]")
    print(f"  LM-Lag:        統計量={ols.lm_lag[0]:.4f}, p={ols.lm_lag[1]:.4f}")
    print(f"  Robust LM-Lag: 統計量={ols.rlm_lag[0]:.4f}, p={ols.rlm_lag[1]:.4f}")
    print(f"  LM-Error:      統計量={ols.lm_error[0]:.4f}, p={ols.lm_error[1]:.4f}")
    print(f"  Robust LM-Error: 統計量={ols.rlm_error[0]:.4f}, p={ols.rlm_error[1]:.4f}")

    # 解釈
    print("\n[空間診断の解釈]")
    if ols.lm_lag[1] < 0.05 and ols.lm_error[1] >= 0.05:
        print("  → SLM（Spatial Lag Model）が推奨されます")
    elif ols.lm_error[1] < 0.05 and ols.lm_lag[1] >= 0.05:
        print("  → SEM（Spatial Error Model）が推奨されます")
    elif ols.rlm_lag[1] < ols.rlm_error[1]:
        print("  → SLM（Spatial Lag Model）が推奨されます（Robust LM-Lag < Robust LM-Error）")
    elif ols.rlm_error[1] < ols.rlm_lag[1]:
        print("  → SEM（Spatial Error Model）が推奨されます（Robust LM-Error < Robust LM-Lag）")
    else:
        print("  → 空間モデルは不要の可能性があります")

    return ols

# ============================================================
# Spatial Lag Model (SLM)
# ============================================================

def run_slm_regression(y, X, var_names, w):
    """Spatial Lag Modelの実行"""

    print("\n" + "=" * 80)
    print(" Spatial Lag Model (SLM)")
    print("=" * 80)

    # SLM実行（Maximum Likelihood推定）
    slm = ML_Lag(y, X, w=w, name_y='prescription_per_100k', name_x=var_names)

    # 結果表示
    print("\n[SLM結果サマリー]")
    print(f"  Pseudo-R-squared: {slm.pr2:.4f}")
    print(f"  AIC: {slm.aic:.2f}")
    print(f"  Log-likelihood: {slm.logll:.2f}")
    print(f"  Spatial lag parameter (ρ): {slm.rho:.4f}")

    print("\n[係数推定値]")
    for i, var in enumerate(var_names):
        coef = slm.betas[i+1][0]  # +1はインターセプトをスキップ
        z_stat = slm.z_stat[i+1][0]
        p_val = slm.z_stat[i+1][1]
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"  {var:30s}: β={coef:8.4f}, z={z_stat:6.3f}, p={p_val:.4f} {sig}")

    return slm

# ============================================================
# Spatial Error Model (SEM)
# ============================================================

def run_sem_regression(y, X, var_names, w):
    """Spatial Error Modelの実行"""

    print("\n" + "=" * 80)
    print(" Spatial Error Model (SEM)")
    print("=" * 80)

    # SEM実行（Maximum Likelihood推定）
    sem = ML_Error(y, X, w=w, name_y='prescription_per_100k', name_x=var_names)

    # 結果表示
    print("\n[SEM結果サマリー]")
    print(f"  Pseudo-R-squared: {sem.pr2:.4f}")
    print(f"  AIC: {sem.aic:.2f}")
    print(f"  Log-likelihood: {sem.logll:.2f}")
    print(f"  Spatial error parameter (λ): {sem.lam:.4f}")

    print("\n[係数推定値]")
    for i, var in enumerate(var_names):
        coef = sem.betas[i+1][0]  # +1はインターセプトをスキップ
        z_stat = sem.z_stat[i+1][0]
        p_val = sem.z_stat[i+1][1]
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"  {var:30s}: β={coef:8.4f}, z={z_stat:6.3f}, p={p_val:.4f} {sig}")

    return sem

# ============================================================
# Spatial Durbin Model (SDM)
# ============================================================

def run_sdm_regression(y, X, var_names, w):
    """Spatial Durbin Modelの実行 (ML_Lag with spatially lagged X)"""

    print("\n" + "=" * 80)
    print(" Spatial Durbin Model (SDM)")
    print("=" * 80)

    # Xの空間ラグを作成
    WX = np.zeros(X.shape)
    for i in range(X.shape[1]):
        WX[:, i] = lag_spatial(w, X[:, i])
    
    # 元のXとWXを結合
    X_sdm = np.hstack((X, WX))
    
    # 変数名の更新
    var_names_sdm = var_names + ["W_" + v for v in var_names]

    # SDM（ML_Lag）実行
    sdm = ML_Lag(y, X_sdm, w=w, name_y='prescription_per_100k', name_x=var_names_sdm)

    # 結果表示
    print("\n[SDM結果サマリー]")
    print(f"  Pseudo-R-squared: {sdm.pr2:.4f}")
    print(f"  AIC: {sdm.aic:.2f}")
    print(f"  Log-likelihood: {sdm.logll:.2f}")
    print(f"  Spatial lag parameter (ρ): {sdm.rho:.4f}")

    print("\n[係数推定値]")
    for i, var in enumerate(var_names_sdm):
        coef = sdm.betas[i+1][0]  # +1はインターセプトをスキップ
        z_stat = sdm.z_stat[i+1][0]
        p_val = sdm.z_stat[i+1][1]
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        print(f"  {var:30s}: β={coef:8.4f}, z={z_stat:6.3f}, p={p_val:.4f} {sig}")

    return sdm, var_names_sdm

# ============================================================
# モデル比較
# ============================================================

def compare_models(ols, slm, sem, sdm, var_names):
    """モデル比較表の作成"""

    print("\n" + "=" * 80)
    print(" モデル比較")
    print("=" * 80)

    # モデル適合度比較
    comparison = pd.DataFrame({
        'Model': ['OLS', 'SLM', 'SEM', 'SDM'],
        'R-squared/Pseudo-R-squared': [ols.r2, slm.pr2, sem.pr2, sdm.pr2],
        'AIC': [ols.aic, slm.aic, sem.aic, sdm.aic],
        'Log-likelihood': [ols.logll, slm.logll, sem.logll, sdm.logll]
    })

    print("\n[モデル適合度比較]")
    print(comparison.to_string(index=False))

    # 最良モデル判定（AICが最小）
    best_model_idx = comparison['AIC'].idxmin()
    best_model = comparison.loc[best_model_idx, 'Model']
    print(f"\n[最良モデル（AIC最小）]: {best_model}")

    # CSV保存
    comparison.to_csv(MODEL_COMPARISON_CSV, index=False, encoding='utf-8-sig')
    print(f"\n[OK] モデル比較表を保存: {MODEL_COMPARISON_CSV}")

    # 係数比較（total_greenspace_ratio_percent）
    print("\n[total_greenspace_ratio_percentの係数比較]")
    greenspace_idx = 1  # インデックス（インターセプト除く）
    ols_coef = ols.betas[greenspace_idx][0]
    ols_se = ols.std_err[greenspace_idx]
    ols_p = ols.t_stat[greenspace_idx][1]

    slm_coef = slm.betas[greenspace_idx][0]
    slm_p = slm.z_stat[greenspace_idx][1]

    sem_coef = sem.betas[greenspace_idx][0]
    sem_p = sem.z_stat[greenspace_idx][1]

    sdm_coef = sdm.betas[greenspace_idx][0]
    sdm_p = sdm.z_stat[greenspace_idx][1]

    print(f"  OLS: β={ols_coef:.4f} (SE={ols_se:.4f}, p={ols_p:.4f})")
    print(f"  SLM: β={slm_coef:.4f} (p={slm_p:.4f})")
    print(f"  SEM: β={sem_coef:.4f} (p={sem_p:.4f})")
    print(f"  SDM: β={sdm_coef:.4f} (p={sdm_p:.4f})")

    return comparison

# ============================================================
# 結果の保存
# ============================================================

def save_regression_results(ols, slm, sem, sdm, var_names, var_names_sdm):
    """回帰結果の詳細をテキストファイルに保存"""

    print("\n[STEP 4] 回帰結果の保存")

    with open(REGRESSION_RESULTS, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(" 空間回帰分析結果 (N=47都道府県)\n")
        f.write("=" * 80 + "\n\n")

        # OLS
        f.write("【1. OLS回帰】\n\n")
        f.write(f"R-squared: {ols.r2:.4f}\n")
        f.write(f"Adjusted R-squared: {ols.ar2:.4f}\n")
        f.write(f"AIC: {ols.aic:.2f}\n")
        f.write(f"Log-likelihood: {ols.logll:.2f}\n\n")

        f.write("係数推定値:\n")
        f.write(f"  Intercept: {ols.betas[0][0]:.4f}\n")
        for i, var in enumerate(var_names):
            coef = ols.betas[i+1][0]
            se = ols.std_err[i+1]
            t_stat = ols.t_stat[i+1][0]
            p_val = ols.t_stat[i+1][1]
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            f.write(f"  {var}: β={coef:.4f}, SE={se:.4f}, t={t_stat:.3f}, p={p_val:.4f} {sig}\n")

        f.write("\n空間診断:\n")
        f.write(f"  LM-Lag: {ols.lm_lag[0]:.4f} (p={ols.lm_lag[1]:.4f})\n")
        f.write(f"  Robust LM-Lag: {ols.rlm_lag[0]:.4f} (p={ols.rlm_lag[1]:.4f})\n")
        f.write(f"  LM-Error: {ols.lm_error[0]:.4f} (p={ols.lm_error[1]:.4f})\n")
        f.write(f"  Robust LM-Error: {ols.rlm_error[0]:.4f} (p={ols.rlm_error[1]:.4f})\n\n")

        # SLM
        f.write("【2. Spatial Lag Model (SLM)】\n\n")
        f.write(f"Pseudo-R-squared: {slm.pr2:.4f}\n")
        f.write(f"AIC: {slm.aic:.2f}\n")
        f.write(f"Log-likelihood: {slm.logll:.2f}\n")
        f.write(f"Spatial lag parameter (ρ): {slm.rho:.4f}\n\n")

        f.write("係数推定値:\n")
        f.write(f"  Intercept: {slm.betas[0][0]:.4f}\n")
        for i, var in enumerate(var_names):
            coef = slm.betas[i+1][0]
            z_stat = slm.z_stat[i+1][0]
            p_val = slm.z_stat[i+1][1]
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            f.write(f"  {var}: β={coef:.4f}, z={z_stat:.3f}, p={p_val:.4f} {sig}\n")

        f.write("\n")

        # SDM
        f.write("【4. Spatial Durbin Model (SDM)】\n\n")
        f.write(f"Pseudo-R-squared: {sdm.pr2:.4f}\n")
        f.write(f"AIC: {sdm.aic:.2f}\n")
        f.write(f"Log-likelihood: {sdm.logll:.2f}\n")
        f.write(f"Spatial lag parameter (ρ): {sdm.rho:.4f}\n\n")

        f.write("係数推定値:\n")
        f.write(f"  Intercept: {sdm.betas[0][0]:.4f}\n")
        for i, var in enumerate(var_names_sdm):
            coef = sdm.betas[i+1][0]
            z_stat = sdm.z_stat[i+1][0]
            p_val = sdm.z_stat[i+1][1]
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            f.write(f"  {var}: β={coef:.4f}, z={z_stat:.3f}, p={p_val:.4f} {sig}\n")

    print(f"  保存完了: {REGRESSION_RESULTS}")

# ============================================================
# 可視化
# ============================================================

def create_coefficient_comparison_plot(ols, slm, sem, sdm, var_names):
    """係数比較図の作成"""

    print("\n[STEP 5] 係数比較図の作成")

    set_japanese_font()

    # 日本語ラベルマッピング
    var_labels = {
        'total_greenspace_ratio_percent': '緑地率 (%)',
        'aging_rate': '高齢化率 (%)',
        'unemployment_rate': '失業率 (%)',
        'income_per_capita': '一人当たり所得 (万円)',
        'single_household_rate': '単独世帯率 (%)',
        'psych_clinic_density': '精神科診療所密度 (/10万人)'
    }

    # データ準備
    coef_data = []
    for i, var in enumerate(var_names):
        ols_coef = ols.betas[i+1][0]
        slm_coef = slm.betas[i+1][0]
        sem_coef = sem.betas[i+1][0]
        sdm_coef = sdm.betas[i+1][0]

        coef_data.append({
            'Variable': var_labels.get(var, var),
            'OLS': ols_coef,
            'SLM': slm_coef,
            'SEM': sem_coef,
            'SDM': sdm_coef
        })

    df_coef = pd.DataFrame(coef_data)

    # プロット
    fig, ax = plt.subplots(figsize=(14, 8))

    x_pos = np.arange(len(var_names))
    width = 0.2

    ax.bar(x_pos - 1.5*width, df_coef['OLS'], width, label='OLS', color='skyblue', edgecolor='black')
    ax.bar(x_pos - 0.5*width, df_coef['SLM'], width, label='SLM', color='lightcoral', edgecolor='black')
    ax.bar(x_pos + 0.5*width, df_coef['SEM'], width, label='SEM', color='lightgreen', edgecolor='black')
    ax.bar(x_pos + 1.5*width, df_coef['SDM'], width, label='SDM', color='gold', edgecolor='black')

    ax.set_xlabel('変数', fontsize=12)
    ax.set_ylabel('係数推定値 (β)', fontsize=12)
    ax.set_title('空間回帰モデルの係数比較 (N=47)', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df_coef['Variable'], rotation=15, ha='right')
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "coefficients_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存完了: {FIGURES_DIR / 'coefficients_comparison.png'}")

# ============================================================
# メイン実行
# ============================================================

if __name__ == "__main__":

    # データ読み込み
    gdf = load_spatial_data()

    # 回帰データ準備
    y, X, var_names, gdf = prepare_regression_data(gdf)

    # 空間重み行列構築
    w = create_spatial_weights(gdf)

    # OLS回帰
    ols = run_ols_regression(y, X, var_names, w)

    # SLM回帰
    slm = run_slm_regression(y, X, var_names, w)

    # SEM回帰
    sem = run_sem_regression(y, X, var_names, w)

    # SDM回帰
    sdm, var_names_sdm = run_sdm_regression(y, X, var_names, w)

    # モデル比較
    comparison = compare_models(ols, slm, sem, sdm, var_names)

    # 結果保存
    save_regression_results(ols, slm, sem, sdm, var_names, var_names_sdm)

    # 可視化
    create_coefficient_comparison_plot(ols, slm, sem, sdm, var_names)

    print("\n" + "=" * 80)
    print(" Phase 3 完了")
    print("=" * 80)
    print(f"\n出力ファイル:")
    print(f"  1. {REGRESSION_RESULTS}")
    print(f"  2. {MODEL_COMPARISON_CSV}")
    print(f"  3. {FIGURES_DIR / 'coefficients_comparison.png'}")
    print("\n次のステップ: Phase 4（結果の総合的可視化と論文執筆）")
