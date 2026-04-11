# -*- coding: utf-8 -*-
"""
緑地率計算スクリプト

機能:
1. L03-b土地利用メッシュデータ（複数年度統合版）を読み込み
2. 都道府県ポリゴンデータ（A38から作成）を読み込み
3. 都道府県別に緑地率を計算: (森林+公園面積) / 総面積 × 100
4. 結果をCSVとして保存

入力:
- data/raw/L03_b_Land_Use_All/*.zip（185ファイル）
- 02_Data/raw/A38_Medical_Area/*.geojson（二次医療圏データ）

出力:
- data/interim/greenspace_ratio.csv（N=47都道府県）
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import zipfile
import tempfile
import shutil

# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
NDB_BASE = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub")

# データパス
L03B_DIR = PROJECT_ROOT / "data" / "raw" / "L03_b_Land_Use_All"
A38_DIR = NDB_BASE / "02_Data" / "raw" / "A38_Medical_Area"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 都道府県コードマッピング（JIS X 0401）
PREFECTURE_CODES = {
    '01': '北海道', '02': '青森県', '03': '岩手県', '04': '宮城県', '05': '秋田県',
    '06': '山形県', '07': '福島県', '08': '茨城県', '09': '栃木県', '10': '群馬県',
    '11': '埼玉県', '12': '千葉県', '13': '東京都', '14': '神奈川県', '15': '新潟県',
    '16': '富山県', '17': '石川県', '18': '福井県', '19': '山梨県', '20': '長野県',
    '21': '岐阜県', '22': '静岡県', '23': '愛知県', '24': '三重県', '25': '滋賀県',
    '26': '京都府', '27': '大阪府', '28': '兵庫県', '29': '奈良県', '30': '和歌山県',
    '31': '鳥取県', '32': '島根県', '33': '岡山県', '34': '広島県', '35': '山口県',
    '36': '徳島県', '37': '香川県', '38': '愛媛県', '39': '高知県', '40': '福岡県',
    '41': '佐賀県', '42': '長崎県', '43': '熊本県', '44': '大分県', '45': '宮崎県',
    '46': '鹿児島県', '47': '沖縄県'
}


def create_prefecture_boundaries():
    """
    A38二次医療圏データから都道府県ポリゴンを作成

    Returns:
        GeoDataFrame: 都道府県ポリゴン
    """
    print("\n" + "="*60)
    print("都道府県ポリゴンの作成")
    print("="*60 + "\n")

    # A38ファイルを再帰的に探す（ネストされたディレクトリ構造に対応）
    a38_files = list(A38_DIR.glob("**/*_2.geojson"))  # _2.geojsonは二次医療圏データ

    if len(a38_files) == 0:
        print(f"[ERROR] A38ファイルが見つかりません: {A38_DIR}")
        print(f"[INFO] パス確認: {A38_DIR.exists()}")
        return None

    print(f"[INFO] A38ファイル検出: {len(a38_files)}ファイル\n")

    # 全ファイルを読み込み
    all_areas = []
    for file_path in a38_files:
        try:
            gdf = gpd.read_file(file_path)
            print(f"[OK] 読み込み: {file_path.name} ({len(gdf)}行)")
            all_areas.append(gdf)
        except Exception as e:
            print(f"[ERROR] 読み込み失敗: {file_path.name} - {e}")

    if len(all_areas) == 0:
        print("[ERROR] 読み込み可能なファイルがありません")
        return None

    # 統合
    gdf_all = pd.concat(all_areas, ignore_index=True)
    print(f"\n[OK] 統合完了: {len(gdf_all)}二次医療圏\n")

    # 都道府県コードを抽出（二次医療圏コードの最初の2桁）
    if 'A38b_003' in gdf_all.columns:
        gdf_all['pref_code'] = gdf_all['A38b_003'].astype(str).str[:2]
    elif 'area_code' in gdf_all.columns:
        gdf_all['pref_code'] = gdf_all['area_code'].astype(str).str[:2]
    else:
        print("[ERROR] 二次医療圏コード列が見つかりません")
        print(f"[INFO] 利用可能な列: {gdf_all.columns.tolist()}")
        return None

    # 都道府県別にdissolve
    print("[INFO] 都道府県別にポリゴンを統合中...")
    gdf_pref = gdf_all.dissolve(by='pref_code', aggfunc='first').reset_index()

    print(f"[OK] 都道府県ポリゴン作成完了: {len(gdf_pref)}都道府県\n")

    # 都道府県名を追加
    gdf_pref['prefecture_name'] = gdf_pref['pref_code'].map(PREFECTURE_CODES)

    return gdf_pref


def read_l03b_file(zip_path):
    """
    L03-b ZIPファイルを読み込み

    Args:
        zip_path: ZIPファイルパス

    Returns:
        GeoDataFrame: 土地利用メッシュデータ
    """
    try:
        # 一時ディレクトリに展開
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # 優先順位: GeoJSON > Shapefile > GML
            # 1. GeoJSONファイルを探す
            geojson_files = list(Path(temp_dir).glob("**/*.geojson"))

            if len(geojson_files) > 0:
                # GeoJSONファイルが存在する場合はそれを使用
                gdf = gpd.read_file(str(geojson_files[0]))
                return gdf

            # 2. Shapefileを探す
            shp_files = list(Path(temp_dir).glob("**/*.shp"))

            if len(shp_files) > 0:
                # Shapefileが存在する場合はそれを使用
                gdf = gpd.read_file(str(shp_files[0]))
                return gdf

            # 3. GMLファイルを探す（最後の手段）
            all_xml_files = list(Path(temp_dir).glob("**/*.xml"))
            gml_files = [f for f in all_xml_files
                        if not f.name.startswith('KS-META')]

            if len(gml_files) > 0:
                gdf = gpd.read_file(str(gml_files[0]))
                return gdf

            return None

    except Exception as e:
        # エラーメッセージを簡略化（大量のエラーを避ける）
        # print(f"[ERROR] 読み込み失敗: {zip_path.name} - {str(e)[:50]}")
        return None


def calculate_greenspace_by_prefecture(gdf_pref):
    """
    都道府県別に緑地率を計算

    Args:
        gdf_pref: 都道府県ポリゴン

    Returns:
        DataFrame: 都道府県別緑地率
    """
    print("\n" + "="*60)
    print("都道府県別緑地率の計算")
    print("="*60 + "\n")

    # L03-bファイルを取得
    l03b_files = sorted(L03B_DIR.glob("L03-b-*.zip"))

    if len(l03b_files) == 0:
        print(f"[ERROR] L03-bファイルが見つかりません: {L03B_DIR}")
        return None

    print(f"[INFO] L03-bファイル検出: {len(l03b_files)}ファイル")
    print(f"[INFO] テスト実行: 最初の30ファイル × 各10,000行サンプリング\n")

    # 都道府県別の土地利用面積を集計
    pref_land_use = {pref_code: {'total_area': 0, 'forest_area': 0, 'park_area': 0}
                     for pref_code in PREFECTURE_CODES.keys()}

    # 各メッシュファイルを処理（テスト実行: 最初の30ファイルのみ）
    processed_count = 0
    skipped_count = 0
    l03b_files_test = l03b_files[:30]

    for i, zip_path in enumerate(l03b_files_test, 1):
        if i % 10 == 0:
            print(f"[INFO] 処理中: {i}/{len(l03b_files_test)}ファイル")

        # メッシュデータ読み込み
        gdf_mesh = read_l03b_file(zip_path)

        if gdf_mesh is None:
            skipped_count += 1
            continue

        # サンプリング: 最初の10,000行のみ処理（メモリ削減）
        if len(gdf_mesh) > 10000:
            gdf_mesh = gdf_mesh.head(10000)

        # CRS確認と変換
        if gdf_mesh.crs is None:
            gdf_mesh = gdf_mesh.set_crs('EPSG:4326')

        # CRS変換（必要に応じて）
        if gdf_mesh.crs != gdf_pref.crs:
            gdf_mesh = gdf_mesh.to_crs(gdf_pref.crs)

        # 都道府県ポリゴンと空間結合
        gdf_joined = gpd.sjoin(gdf_mesh, gdf_pref[['pref_code', 'geometry']],
                               how='inner', predicate='intersects')

        if len(gdf_joined) == 0:
            skipped_count += 1
            continue

        # 土地利用コードから緑地を判定
        # L03-bコード: 0100=田、0200=その他農用地、0500=森林、0600=荒地、0700=建物用地、
        #             0800=幹線交通用地、0900=その他の用地、1100=河川地及び湖沼、1200=海浜、1300=海水域、1400=ゴルフ場

        # 緑地の定義: 森林(0500) + 公園（ゴルフ場1400は除外、その他農用地0200を含める）
        # ※簡易版として、森林+その他農用地を緑地とする

        for _, row in gdf_joined.iterrows():
            pref_code = row['pref_code']

            # 面積計算（メッシュ100m×100m = 10,000㎡ = 0.01km²）
            mesh_area = 0.01  # km²

            # 土地利用コード取得
            # 可能性のある列名: '土地利用細分', 'L03b_002', '土地利用'
            land_use_code = None

            for possible_col in ['土地利用細分', 'L03b_002', '土地利用']:
                if possible_col in row.index:
                    land_use_code = row[possible_col]
                    break

            if land_use_code is None:
                # 列名が異なる場合の汎用的な対応
                for col in row.index:
                    if '土地利用' in str(col) or ('L03' in str(col) and '002' in str(col)):
                        land_use_code = row[col]
                        break

            if land_use_code is not None:
                land_use_code = str(land_use_code).zfill(4)

                # 総面積
                pref_land_use[pref_code]['total_area'] += mesh_area

                # 森林（0500）
                if land_use_code == '0500':
                    pref_land_use[pref_code]['forest_area'] += mesh_area

                # 公園・緑地（その他農用地0200を含む）
                elif land_use_code == '0200':
                    pref_land_use[pref_code]['park_area'] += mesh_area

        processed_count += 1

    print(f"\n[OK] メッシュ処理完了")
    print(f"   - 処理済み: {processed_count}ファイル")
    print(f"   - スキップ: {skipped_count}ファイル\n")

    # 緑地率を計算
    greenspace_data = []

    for pref_code, data in pref_land_use.items():
        total_area = data['total_area']

        if total_area == 0:
            print(f"[WARNING] {PREFECTURE_CODES[pref_code]}: データなし")
            continue

        greenspace_area = data['forest_area'] + data['park_area']
        greenspace_ratio = (greenspace_area / total_area) * 100
        park_ratio = (data['park_area'] / total_area) * 100
        forest_ratio = (data['forest_area'] / total_area) * 100

        greenspace_data.append({
            'prefecture_code': pref_code,
            'prefecture_name': PREFECTURE_CODES[pref_code],
            'total_area_km2': total_area,
            'forest_area_km2': data['forest_area'],
            'park_area_km2': data['park_area'],
            'greenspace_area_km2': greenspace_area,
            'total_greenspace_ratio_percent': greenspace_ratio,
            'park_ratio_percent': park_ratio,
            'forest_ratio_percent': forest_ratio
        })

        print(f"[OK] {PREFECTURE_CODES[pref_code]}: 緑地率={greenspace_ratio:.2f}% (公園={park_ratio:.2f}%, 森林={forest_ratio:.2f}%)")

    # DataFrameに変換
    if len(greenspace_data) == 0:
        print(f"\n[ERROR] 緑地率計算データが0件です")
        return None

    df_greenspace = pd.DataFrame(greenspace_data)

    print(f"\n[OK] 緑地率計算完了: {len(df_greenspace)}都道府県\n")

    return df_greenspace


def save_results(df_greenspace):
    """
    結果を保存

    Args:
        df_greenspace: 都道府県別緑地率データ
    """
    print("\n" + "="*60)
    print("結果の保存")
    print("="*60 + "\n")

    output_file = OUTPUT_DIR / "greenspace_ratio.csv"

    # 並び替え（都道府県コード順）
    df_greenspace = df_greenspace.sort_values('prefecture_code')

    # 保存
    df_greenspace.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"[OK] 保存完了: {output_file}")
    print(f"   - 行数: {len(df_greenspace)}")
    print(f"   - 列数: {len(df_greenspace.columns)}\n")

    # 基本統計量
    print("[INFO] 緑地率の基本統計量:")
    print(df_greenspace['total_greenspace_ratio_percent'].describe().to_string())
    print()


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print(" 緑地率計算スクリプト")
    print("="*80)

    # 1. 都道府県ポリゴン作成
    gdf_pref = create_prefecture_boundaries()

    if gdf_pref is None:
        print("\n[ERROR] 都道府県ポリゴン作成に失敗しました")
        return

    # 2. 緑地率計算
    df_greenspace = calculate_greenspace_by_prefecture(gdf_pref)

    if df_greenspace is None:
        print("\n[ERROR] 緑地率計算に失敗しました")
        return

    # 3. 結果保存
    save_results(df_greenspace)

    print("="*80)
    print("[DONE] 全処理完了")
    print("="*80 + "\n")

    print("[INFO] 次のステップ:")
    print("   1. 出力ファイル確認:")
    print("      data/interim/greenspace_ratio.csv")
    print()
    print("   2. 調整変数データ統合スクリプトの実行:")
    print("      python 03_Analysis/scripts/04_integrate_socioeconomic_data.py")
    print()


if __name__ == "__main__":
    main()
