# -*- coding: utf-8 -*-
"""
スクリプト05: 記述統計と人口調整

Phase 2の内容：
1. 人口10万人あたり処方量への変換
2. 記述統計（平均、標準偏差、最小値、最大値、四分位数）
3. 変数間の相関分析
4. 可視化（ヒストグラム、散布図、相関行列）

入力:
- data/processed/analysis_dataset.csv

出力:
- data/processed/analysis_dataset_per100k.csv（人口調整後）
- results/descriptive_stats.txt（記述統計）
- results/correlation_matrix.csv（相関行列）
- results/figures/histogram_greenspace.png
- results/figures/histogram_prescription.png
- results/figures/scatter_greenspace_prescription.png
- results/figures/correlation_heatmap.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

# ============================================================
# パス設定
# ============================================================

GREENSPACE_PROJECT = Path(__file__).resolve().parents[2]
DATA_DIR = GREENSPACE_PROJECT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = GREENSPACE_PROJECT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

# ディレクトリ作成
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 入出力ファイル
INPUT_FILE = PROCESSED_DIR / "analysis_dataset.csv"
OUTPUT_FILE = PROCESSED_DIR / "analysis_dataset_per100k.csv"
STATS_FILE = RESULTS_DIR / "descriptive_stats.txt"
CORR_FILE = RESULTS_DIR / "correlation_matrix.csv"

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

    plt.rcParams['axes.unicode_minus'] = False  # マイナス記号の文字化け対策

# ============================================================
# データ読み込みと人口調整
# ============================================================

def load_and_adjust_data():
    """データ読み込みと人口10万人あたり処方量の計算"""

    print("=" * 80)
    print(" Phase 2: 記述統計と人口調整")
    print("=" * 80)

    print("\n[STEP 1] データ読み込み")
    df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')
    print(f"  読み込み完了: {len(df)}都道府県 × {len(df.columns)}変数")

    print("\n[STEP 2] 派生変数の計算")
    df['prescription_per_100k'] = (df['total_quantity'] / df['total_pop']) * 100000
    print(f"  計算完了: prescription_per_100k列を追加")

    # 人口密度を計算（存在しない場合のみ）
    if 'pop_density' not in df.columns:
        df['pop_density'] = df['total_pop'] / df['total_area_km2']
        print(f"  計算完了: pop_density列を追加 (total_pop / total_area_km2)")

    # university_grad_rate を college_graduate_rate として統一（後方互換）
    if 'university_grad_rate' in df.columns and 'college_graduate_rate' not in df.columns:
        df['college_graduate_rate'] = df['university_grad_rate']
        print(f"  列名統一: university_grad_rate -> college_graduate_rate")

    # 基本統計量表示
    print(f"\n  prescription_per_100k の統計:")
    print(f"    平均: {df['prescription_per_100k'].mean():.2f}")
    print(f"    標準偏差: {df['prescription_per_100k'].std():.2f}")
    print(f"    最小値: {df['prescription_per_100k'].min():.2f} ({df.loc[df['prescription_per_100k'].idxmin(), 'prefecture_name']})")
    print(f"    最大値: {df['prescription_per_100k'].max():.2f} ({df.loc[df['prescription_per_100k'].idxmax(), 'prefecture_name']})")

    # 保存
    print(f"\n[STEP 3] データ保存")
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"  保存完了: {OUTPUT_FILE}")

    return df

# ============================================================
# 記述統計
# ============================================================

def calculate_descriptive_stats(df):
    """記述統計の計算と保存"""

    print("\n" + "=" * 80)
    print(" 記述統計")
    print("=" * 80)

    # 分析対象変数
    analysis_vars = [
        'greenspace_ratio_percent',
        'prescription_per_100k',
        'aging_rate',
        'pop_density',
        'income_per_capita',
        'unemployment_rate',
        'single_household_rate',
        'college_graduate_rate',
        'psych_clinic_density'
    ]

    # 記述統計計算
    desc_stats = df[analysis_vars].describe()

    # テキスト出力用
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(" 記述統計（N=47都道府県）\n")
        f.write("=" * 80 + "\n\n")

        for var in analysis_vars:
            f.write(f"【{var}】\n")
            f.write(f"  平均値: {df[var].mean():.4f}\n")
            f.write(f"  標準偏差: {df[var].std():.4f}\n")
            f.write(f"  中央値: {df[var].median():.4f}\n")
            f.write(f"  最小値: {df[var].min():.4f}\n")
            f.write(f"  最大値: {df[var].max():.4f}\n")
            f.write(f"  第1四分位: {df[var].quantile(0.25):.4f}\n")
            f.write(f"  第3四分位: {df[var].quantile(0.75):.4f}\n")

            # 正規性検定（Shapiro-Wilk検定）
            stat, p_value = stats.shapiro(df[var].dropna())
            f.write(f"  正規性検定 (Shapiro-Wilk): W={stat:.4f}, p={p_value:.4f}\n")

            f.write("\n")

    print(f"\n[OK] 記述統計を保存: {STATS_FILE}")

    # コンソール出力
    print("\n主要変数の記述統計:")
    print(desc_stats.to_string())

    return desc_stats

# ============================================================
# 相関分析
# ============================================================

def calculate_correlations(df):
    """相関分析の実施と保存"""

    print("\n" + "=" * 80)
    print(" 相関分析")
    print("=" * 80)

    # 分析対象変数
    analysis_vars = [
        'greenspace_ratio_percent',
        'prescription_per_100k',
        'aging_rate',
        'pop_density',
        'income_per_capita',
        'unemployment_rate',
        'single_household_rate',
        'college_graduate_rate',
        'psych_clinic_density'
    ]

    # Pearson相関係数計算
    corr_matrix = df[analysis_vars].corr()

    # 保存
    corr_matrix.to_csv(CORR_FILE, encoding='utf-8-sig')
    print(f"\n[OK] 相関行列を保存: {CORR_FILE}")

    # 主要な相関を表示
    print("\n主要な相関（prescription_per_100kとの相関）:")
    prescription_corr = corr_matrix['prescription_per_100k'].drop('prescription_per_100k').sort_values(ascending=False)
    for var, corr_val in prescription_corr.items():
        print(f"  {var}: r={corr_val:.4f}")

    return corr_matrix

# ============================================================
# 可視化
# ============================================================

def create_visualizations(df, corr_matrix):
    """記述統計の可視化"""

    print("\n" + "=" * 80)
    print(" 可視化")
    print("=" * 80)

    set_japanese_font()

    # 1. 緑地率のヒストグラム
    print("\n[1/4] 緑地率のヒストグラム作成中...")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['greenspace_ratio_percent'], bins=15, color='green', alpha=0.7, edgecolor='black')
    ax.set_xlabel('緑地率 (%)', fontsize=12)
    ax.set_ylabel('都道府県数', fontsize=12)
    ax.set_title('都道府県別緑地率の分布 (N=47)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # 統計量を追加
    mean_val = df['greenspace_ratio_percent'].mean()
    median_val = df['greenspace_ratio_percent'].median()
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'平均: {mean_val:.2f}%')
    ax.axvline(median_val, color='blue', linestyle='--', linewidth=2, label=f'中央値: {median_val:.2f}%')
    ax.legend()

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "histogram_greenspace.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存完了: {FIGURES_DIR / 'histogram_greenspace.png'}")

    # 2. 処方量のヒストグラム
    print("\n[2/4] 処方量のヒストグラム作成中...")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['prescription_per_100k'], bins=15, color='purple', alpha=0.7, edgecolor='black')
    ax.set_xlabel('精神科処方薬量（人口10万人あたり）', fontsize=12)
    ax.set_ylabel('都道府県数', fontsize=12)
    ax.set_title('都道府県別精神科処方薬量の分布 (N=47)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    mean_val = df['prescription_per_100k'].mean()
    median_val = df['prescription_per_100k'].median()
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'平均: {mean_val:.2f}')
    ax.axvline(median_val, color='blue', linestyle='--', linewidth=2, label=f'中央値: {median_val:.2f}')
    ax.legend()

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "histogram_prescription.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存完了: {FIGURES_DIR / 'histogram_prescription.png'}")

    print("\n[3/4] 散布図（緑地率 vs 処方量）作成中...")

    # NaN を除外した有効データのみ使用
    mask = df['greenspace_ratio_percent'].notna() & df['prescription_per_100k'].notna()
    df_valid = df[mask].copy()
    n_valid = len(df_valid)
    print(f"  有効データ数: {n_valid} / {len(df)} 都道府県")

    if df_valid['greenspace_ratio_percent'].std() == 0:
        print(f"  [警告] greenspace_ratio_percent の分散がゼロです。緑地率データが未計算の可能性があります。")
        print(f"  散布図をスキップします。03_calculate_greenspace_ratio*.py を先に実行してください。")
    else:
        fig, ax = plt.subplots(figsize=(10, 8))

        # 散布図
        scatter = ax.scatter(df_valid['greenspace_ratio_percent'], df_valid['prescription_per_100k'],
                            s=100, alpha=0.6, c=df_valid['aging_rate'],
                            cmap='viridis', edgecolors='black', linewidth=0.5)

        # 回帰線
        try:
            z = np.polyfit(df_valid['greenspace_ratio_percent'], df_valid['prescription_per_100k'], 1)
            p_poly = np.poly1d(z)
            x_sorted = df_valid['greenspace_ratio_percent'].sort_values()
            ax.plot(x_sorted, p_poly(x_sorted),
                    "r--", alpha=0.8, linewidth=2, label=f'回帰線 (y={z[0]:.2f}x+{z[1]:.2f})')
        except Exception as e:
            print(f"  [警告] 回帰線の計算に失敗しました: {e}")

        # 相関係数
        r_val = df_valid[['greenspace_ratio_percent', 'prescription_per_100k']].corr().iloc[0, 1]
        try:
            p_val = stats.pearsonr(df_valid['greenspace_ratio_percent'], df_valid['prescription_per_100k'])[1]
            title_str = f'緑地率と精神科処方薬量の関連 (N={n_valid})\nr={r_val:.4f}, p={p_val:.4f}'
        except Exception:
            title_str = f'緑地率と精神科処方薬量の関連 (N={n_valid})\nr={r_val:.4f}'

        ax.set_xlabel('緑地率 (%)', fontsize=12)
        ax.set_ylabel('精神科処方薬量（人口10万人あたり）', fontsize=12)
        ax.set_title(title_str, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # カラーバー（高齢化率）
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('高齢化率 (%)', fontsize=10)

        plt.tight_layout()
        fig.savefig(FIGURES_DIR / "scatter_greenspace_prescription.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  保存完了: {FIGURES_DIR / 'scatter_greenspace_prescription.png'}")

    # 4. 相関ヒートマップ
    print("\n[4/4] 相関ヒートマップ作成中...")
    fig, ax = plt.subplots(figsize=(12, 10))

    # 変数名を日本語に変換
    var_labels = {
        'greenspace_ratio_percent': '緑地率',
        'prescription_per_100k': '処方薬量',
        'aging_rate': '高齢化率',
        'pop_density': '人口密度',
        'income_per_capita': '一人当たり所得',
        'college_graduate_rate': '大卒率'
    }

    corr_renamed = corr_matrix.rename(index=var_labels, columns=var_labels)

    sns.heatmap(corr_renamed, annot=True, fmt='.3f', cmap='coolwarm',
                center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                vmin=-1, vmax=1, ax=ax)
    ax.set_title('変数間の相関行列 (N=47)', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "correlation_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存完了: {FIGURES_DIR / 'correlation_heatmap.png'}")

# ============================================================
# メイン実行
# ============================================================

if __name__ == "__main__":

    # データ読み込みと人口調整
    df = load_and_adjust_data()

    # 記述統計
    desc_stats = calculate_descriptive_stats(df)

    # 相関分析
    corr_matrix = calculate_correlations(df)

    # 可視化
    create_visualizations(df, corr_matrix)

    print("\n" + "=" * 80)
    print(" Phase 2 完了")
    print("=" * 80)
    print(f"\n出力ファイル:")
    print(f"  1. {OUTPUT_FILE}")
    print(f"  2. {STATS_FILE}")
    print(f"  3. {CORR_FILE}")
    print(f"  4. {FIGURES_DIR / 'histogram_greenspace.png'}")
    print(f"  5. {FIGURES_DIR / 'histogram_prescription.png'}")
    print(f"  6. {FIGURES_DIR / 'scatter_greenspace_prescription.png'}")
    print(f"  7. {FIGURES_DIR / 'correlation_heatmap.png'}")
    print("\n次のステップ: Phase 2b（空間的探索的分析）")
