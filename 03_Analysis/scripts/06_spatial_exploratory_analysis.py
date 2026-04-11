# -*- coding: utf-8 -*-
"""
スクリプト06: 空間的探索的分析

Phase 2bの内容：
1. 空間重み行列の構築（Queen contiguity）
2. Global Moran's I 計算（空間的自己相関の検定）
3. Local Moran's I 計算（LISA: Local Indicators of Spatial Association）
4. Choropleth map（段階区分図）の作成
5. LISA マップの作成

入力:
- data/processed/analysis_dataset_per100k.csv
- 都道府県ポリゴンデータ（N03-20240101_prefecture.geojson）

出力:
- results/spatial_weights.gal（空間重み行列）
- results/morans_i_results.txt（Moran's I 結果）
- results/figures/choropleth_greenspace.png
- results/figures/choropleth_prescription.png
- results/figures/lisa_map_prescription.png
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local
import seaborn as sns

# ============================================================
# パス設定
# ============================================================

GREENSPACE_PROJECT = Path(__file__).resolve().parents[2]
NDB_ROOT = GREENSPACE_PROJECT.parents[1]

DATA_DIR = GREENSPACE_PROJECT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = GREENSPACE_PROJECT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

# 入力ファイル
INPUT_FILE = PROCESSED_DIR / "analysis_dataset_per100k.csv"
PREFECTURE_GEOJSON = NDB_ROOT / "projects" / "NDB_XXX_slope_fracture" / "data" / "raw" / "MLIT_N03" / "N03-20240101_prefecture.geojson"

# 出力ファイル
MORANS_RESULTS = RESULTS_DIR / "morans_i_results.txt"
SPATIAL_DATA_GEOJSON = PROCESSED_DIR / "spatial_analysis_data.geojson"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 都道府県コードマッピング
PREFECTURE_CODES = {
    '01': '北海道', '02': '青森県', '03': '岩手県', '04': '宮城県',
    '05': '秋田県', '06': '山形県', '07': '福島県', '08': '茨城県',
    '09': '栃木県', '10': '群馬県', '11': '埼玉県', '12': '千葉県',
    '13': '東京都', '14': '神奈川県', '15': '新潟県', '16': '富山県',
    '17': '石川県', '18': '福井県', '19': '山梨県', '20': '長野県',
    '21': '岐阜県', '22': '静岡県', '23': '愛知県', '24': '三重県',
    '25': '滋賀県', '26': '京都府', '27': '大阪府', '28': '兵庫県',
    '29': '奈良県', '30': '和歌山県', '31': '鳥取県', '32': '島根県',
    '33': '岡山県', '34': '広島県', '35': '山口県', '36': '徳島県',
    '37': '香川県', '38': '愛媛県', '39': '高知県', '40': '福岡県',
    '41': '佐賀県', '42': '長崎県', '43': '熊本県', '44': '大分県',
    '45': '宮崎県', '46': '鹿児島県', '47': '沖縄県'
}

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
# データ読み込みと空間結合
# ============================================================

def load_and_merge_spatial_data():
    """データと都道府県ポリゴンを読み込み、空間結合"""

    print("=" * 80)
    print(" Phase 2b: 空間的探索的分析")
    print("=" * 80)

    print("\n[STEP 1] データ読み込み")
    df = pd.read_csv(INPUT_FILE, encoding='utf-8-sig')
    print(f"  データ読み込み完了: {len(df)}都道府県")

    # prefecture_codeをstr型に変換（ゼロ埋め2桁）
    df['prefecture_code'] = df['prefecture_code'].astype(str).str.zfill(2)

    print("\n[STEP 2] 都道府県ポリゴン読み込み")
    if not PREFECTURE_GEOJSON.exists():
        print(f"  [ERROR] ポリゴンファイルが見つかりません: {PREFECTURE_GEOJSON}")
        raise FileNotFoundError(f"ポリゴンファイルが見つかりません: {PREFECTURE_GEOJSON}")

    gdf_pref = gpd.read_file(PREFECTURE_GEOJSON)
    print(f"  ポリゴン読み込み完了: {len(gdf_pref)}ポリゴン")

    # 都道府県単位に統合（dissolve）
    print("\n[STEP 3] 都道府県単位に統合中...")
    gdf_pref = gdf_pref[['N03_001', 'N03_007', 'geometry']].dissolve(by='N03_001', aggfunc='first').reset_index()
    print(f"  統合完了: {len(gdf_pref)}都道府県")

    # 都道府県コードを標準化
    # N03_007が存在しない場合は、都道府県名からマッピング
    code_map_reversed = {v: k for k, v in PREFECTURE_CODES.items()}
    gdf_pref['prefecture_code'] = gdf_pref['N03_001'].map(code_map_reversed)

    # デバッグ: マージ前のprefecture_codeを確認
    print(f"\n  [デバッグ] gdf_prefのprefecture_code（先頭5件）:")
    print(f"    {gdf_pref['prefecture_code'].head(5).tolist()}")
    print(f"  [デバッグ] dfのprefecture_code（先頭5件）:")
    print(f"    {df['prefecture_code'].head(5).tolist()}")

    # データとポリゴンをマージ
    print("\n[STEP 4] データとポリゴンをマージ")
    gdf = gdf_pref.merge(df, on='prefecture_code', how='inner')
    print(f"  マージ完了: {len(gdf)}都道府県")

    # CRS確認・変換（日本測地系2011 EPSG:6668 → WGS84 EPSG:4326）
    print(f"\n[STEP 5] CRS確認")
    print(f"  現在のCRS: {gdf.crs}")
    if gdf.crs != 'EPSG:4326':
        print("  WGS84 (EPSG:4326)に変換中...")
        gdf = gdf.to_crs('EPSG:4326')
        print("  変換完了")

    # GeoJSONとして保存
    print(f"\n[STEP 6] 空間データ保存")
    gdf.to_file(SPATIAL_DATA_GEOJSON, driver='GeoJSON', encoding='utf-8')
    print(f"  保存完了: {SPATIAL_DATA_GEOJSON}")

    return gdf

# ============================================================
# 空間重み行列の構築
# ============================================================

def create_spatial_weights(gdf):
    """Queen contiguity空間重み行列の構築"""

    print("\n" + "=" * 80)
    print(" 空間重み行列の構築")
    print("=" * 80)

    # Queen contiguity（辺または頂点を共有する都道府県を隣接とみなす）
    print("\n[STEP 1] Queen contiguity空間重み行列を構築中...")
    w = Queen.from_dataframe(gdf, idVariable='prefecture_code')
    print(f"  構築完了: {w.n}ノード, {w.s0}エッジ")

    # 孤島（隣接なし）の確認
    islands = [i for i in w.islands if i in range(len(gdf))]
    if islands:
        island_prefs = gdf.iloc[islands]['prefecture_name'].tolist()
        print(f"\n  [警告] 孤島（隣接なし）が{len(islands)}件あります:")
        for pref in island_prefs:
            print(f"    - {pref}")
        print("  これらは空間的自己相関分析から除外されます。")

    # 行標準化（Row-standardized）
    w.transform = 'r'
    print(f"  行標準化完了")

    return w

# ============================================================
# Global Moran's I
# ============================================================

def calculate_global_morans_i(gdf, w):
    """Global Moran's I の計算"""

    print("\n" + "=" * 80)
    print(" Global Moran's I 計算")
    print("=" * 80)

    variables = [
        ('greenspace_ratio_percent', '緑地率'),
        ('prescription_per_100k', '処方薬量（人口10万人あたり）'),
        ('aging_rate', '高齢化率'),
        ('pop_density', '人口密度')
    ]

    results = []

    with open(MORANS_RESULTS, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(" Global Moran's I 検定結果 (N=47都道府県)\n")
        f.write("=" * 80 + "\n\n")

        for var, label in variables:
            print(f"\n[{var}] {label}")

            # Moran's I 計算
            mi = Moran(gdf[var], w)

            # 結果を保存
            results.append({
                'variable': var,
                'label': label,
                'moran_i': mi.I,
                'expected_i': mi.EI,
                'p_value': mi.p_sim,
                'z_score': mi.z_sim
            })

            # コンソール出力
            print(f"  Moran's I: {mi.I:.4f}")
            print(f"  期待値: {mi.EI:.4f}")
            print(f"  p値: {mi.p_sim:.4f}")
            print(f"  z値: {mi.z_sim:.4f}")

            if mi.p_sim < 0.05:
                if mi.I > 0:
                    print(f"  → 有意な正の空間的自己相関あり [p<0.05]")
                else:
                    print(f"  → 有意な負の空間的自己相関あり [p<0.05]")
            else:
                print(f"  → 空間的自己相関なし [n.s.]")

            # テキスト出力
            f.write(f"【{label}】\n")
            f.write(f"  Moran's I: {mi.I:.4f}\n")
            f.write(f"  期待値: {mi.EI:.4f}\n")
            f.write(f"  p値 (permutation): {mi.p_sim:.4f}\n")
            f.write(f"  z値: {mi.z_sim:.4f}\n")
            f.write(f"  解釈: ")
            if mi.p_sim < 0.05:
                if mi.I > 0:
                    f.write("有意な正の空間的自己相関 (類似した値が空間的にクラスター)\n")
                else:
                    f.write("有意な負の空間的自己相関 (異なる値が空間的に混在)\n")
            else:
                f.write("空間的自己相関なし (ランダム分布)\n")
            f.write("\n")

    print(f"\n[OK] Moran's I結果を保存: {MORANS_RESULTS}")

    return pd.DataFrame(results)

# ============================================================
# Local Moran's I (LISA)
# ============================================================

def calculate_local_morans_i(gdf, w):
    """Local Moran's I (LISA) の計算"""

    print("\n" + "=" * 80)
    print(" Local Moran's I (LISA) 計算")
    print("=" * 80)

    print("\n[処方薬量のLISA計算中...]")

    # prescription_per_100k のLISA
    lisa = Moran_Local(gdf['prescription_per_100k'], w)

    # GeoDataFrameに結果を追加
    gdf['lisa_cluster'] = lisa.q  # 1=HH, 2=LH, 3=LL, 4=HL
    gdf['lisa_p_value'] = lisa.p_sim
    gdf['lisa_significant'] = gdf['lisa_p_value'] < 0.05

    # クラスターラベル
    cluster_labels = {
        1: 'High-High',
        2: 'Low-High',
        3: 'Low-Low',
        4: 'High-Low',
        0: '非有意'
    }

    # 有意でないものは0にラベル変更
    gdf['lisa_cluster_label'] = gdf.apply(
        lambda row: cluster_labels.get(row['lisa_cluster'], '非有意') if row['lisa_significant'] else '非有意',
        axis=1
    )

    # クラスター集計
    print("\n[LISA クラスター集計]")
    cluster_counts = gdf['lisa_cluster_label'].value_counts()
    for label, count in cluster_counts.items():
        print(f"  {label}: {count}都道府県")

    # 有意なクラスターの都道府県リスト
    print("\n[有意なクラスター（p<0.05）]")
    for cluster_type in ['High-High', 'Low-Low', 'Low-High', 'High-Low']:
        cluster_prefs = gdf[gdf['lisa_cluster_label'] == cluster_type]['prefecture_name'].tolist()
        if cluster_prefs:
            print(f"\n  【{cluster_type}】")
            for pref in cluster_prefs:
                print(f"    - {pref}")

    return gdf

# ============================================================
# Choropleth Map（段階区分図）
# ============================================================

def create_choropleth_maps(gdf):
    """Choropleth mapの作成"""

    print("\n" + "=" * 80)
    print(" Choropleth Map 作成")
    print("=" * 80)

    set_japanese_font()

    # 1. 緑地率のChoropleth map
    print("\n[1/2] 緑地率のChoropleth map作成中...")
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    gdf.plot(column='greenspace_ratio_percent',
             cmap='YlGn',
             legend=True,
             ax=ax,
             edgecolor='black',
             linewidth=0.5,
             legend_kwds={'label': '緑地率 (%)', 'shrink': 0.5})

    ax.set_title('都道府県別緑地率 (N=47)', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "choropleth_greenspace.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存完了: {FIGURES_DIR / 'choropleth_greenspace.png'}")

    # 2. 処方薬量のChoropleth map
    print("\n[2/2] 処方薬量のChoropleth map作成中...")
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    gdf.plot(column='prescription_per_100k',
             cmap='RdPu',
             legend=True,
             ax=ax,
             edgecolor='black',
             linewidth=0.5,
             legend_kwds={'label': '処方薬量（人口10万人あたり）', 'shrink': 0.5})

    ax.set_title('都道府県別精神科処方薬量 (N=47)', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "choropleth_prescription.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存完了: {FIGURES_DIR / 'choropleth_prescription.png'}")

# ============================================================
# LISA Map
# ============================================================

def create_lisa_map(gdf):
    """LISA mapの作成"""

    print("\n" + "=" * 80)
    print(" LISA Map 作成")
    print("=" * 80)

    set_japanese_font()

    print("\n[LISA map作成中...]")

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # カラーマップ定義
    colors = {
        'High-High': '#d7191c',   # 赤（高-高クラスター）
        'Low-Low': '#2b83ba',     # 青（低-低クラスター）
        'Low-High': '#abdda4',    # 緑（低-高：外れ値）
        'High-Low': '#fdae61',    # オレンジ（高-低：外れ値）
        '非有意': '#f0f0f0'       # グレー（非有意）
    }

    gdf['color'] = gdf['lisa_cluster_label'].map(colors)

    gdf.plot(color=gdf['color'],
             ax=ax,
             edgecolor='black',
             linewidth=0.5)

    ax.set_title('LISA Map: 処方薬量の空間的クラスター (p<0.05)', fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')

    # 凡例作成
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#d7191c', edgecolor='black', label='High-High（高値クラスター）'),
        Patch(facecolor='#2b83ba', edgecolor='black', label='Low-Low（低値クラスター）'),
        Patch(facecolor='#abdda4', edgecolor='black', label='Low-High（低値外れ値）'),
        Patch(facecolor='#fdae61', edgecolor='black', label='High-Low（高値外れ値）'),
        Patch(facecolor='#f0f0f0', edgecolor='black', label='非有意')
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "lisa_map_prescription.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存完了: {FIGURES_DIR / 'lisa_map_prescription.png'}")

# ============================================================
# メイン実行
# ============================================================

if __name__ == "__main__":

    # データ読み込みと空間結合
    gdf = load_and_merge_spatial_data()

    # 空間重み行列の構築
    w = create_spatial_weights(gdf)

    # Global Moran's I
    morans_results = calculate_global_morans_i(gdf, w)

    # Local Moran's I (LISA)
    gdf = calculate_local_morans_i(gdf, w)

    # Choropleth maps
    create_choropleth_maps(gdf)

    # LISA map
    create_lisa_map(gdf)

    # 更新されたGeoDataFrameを保存
    gdf.to_file(SPATIAL_DATA_GEOJSON, driver='GeoJSON', encoding='utf-8')
    print(f"\n[OK] LISA結果を含む空間データを更新保存: {SPATIAL_DATA_GEOJSON}")

    print("\n" + "=" * 80)
    print(" Phase 2b 完了")
    print("=" * 80)
    print(f"\n出力ファイル:")
    print(f"  1. {MORANS_RESULTS}")
    print(f"  2. {SPATIAL_DATA_GEOJSON}")
    print(f"  3. {FIGURES_DIR / 'choropleth_greenspace.png'}")
    print(f"  4. {FIGURES_DIR / 'choropleth_prescription.png'}")
    print(f"  5. {FIGURES_DIR / 'lisa_map_prescription.png'}")
    print("\n次のステップ: Phase 3（空間回帰分析）")
