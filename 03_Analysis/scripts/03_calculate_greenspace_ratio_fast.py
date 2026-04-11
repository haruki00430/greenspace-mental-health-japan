# -*- coding: utf-8 -*-
"""
緑地率計算スクリプト（高速版・サンプル数削減）

185ファイル全てではなく、最初の20ファイルのみ処理して概算値を算出
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import zipfile
import tempfile

# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
NDB_BASE = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub")

# データパス
L03B_DIR = PROJECT_ROOT / "data" / "raw" / "L03_b_Land_Use_All"
A38_DIR = NDB_BASE / "02_Data" / "raw" / "A38_Medical_Area"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 都道府県コードマッピング
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

print("="*60)
print("緑地率計算スクリプト（高速版）")
print("="*60)
print()
print("[INFO] 注意: 処理時間短縮のため、サンプルデータで概算値を算出します")
print()

# A38都道府県ポリゴン作成
print("[INFO] A38都道府県ポリゴン読み込み中...")
a38_files = list(A38_DIR.glob("**/*_2.geojson"))
all_areas = []
for f in a38_files[:10]:  # 最初の10ファイルのみ
    gdf = gpd.read_file(f)
    all_areas.append(gdf)

gdf_all = pd.concat(all_areas, ignore_index=True)
gdf_all['pref_code'] = gdf_all['A38b_003'].astype(str).str[:2]
gdf_pref = gdf_all.dissolve(by='pref_code', aggfunc='first').reset_index()
gdf_pref['prefecture_name'] = gdf_pref['pref_code'].map(PREFECTURE_CODES)

print(f"[OK] 都道府県ポリゴン作成: {len(gdf_pref)}都道府県\n")

# L03-bファイル処理（最初の30ファイルのみ）
print("[INFO] L03-bファイル処理中（最初の30ファイルのみ）...")
l03b_files = sorted(L03B_DIR.glob("L03-b-*.zip"))[:30]

pref_land_use = {pref_code: {'total_area': 0, 'forest_area': 0, 'park_area': 0}
                 for pref_code in PREFECTURE_CODES.keys()}

processed = 0
for i, zip_path in enumerate(l03b_files, 1):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            geojson_files = list(Path(temp_dir).glob("**/*.geojson"))
            if not geojson_files:
                continue

            gdf_mesh = gpd.read_file(str(geojson_files[0]))

            if gdf_mesh.crs != gdf_pref.crs:
                gdf_mesh = gdf_mesh.to_crs(gdf_pref.crs)

            # 空間結合（最初の1000行のみ処理して高速化）
            gdf_joined = gpd.sjoin(gdf_mesh.head(1000), gdf_pref[['pref_code', 'geometry']],
                                   how='inner', predicate='intersects')

            for _, row in gdf_joined.iterrows():
                pref_code = row['pref_code']
                mesh_area = 0.01  # km²

                land_use_code = None
                for col in ['土地利用細分', 'L03b_002']:
                    if col in row.index:
                        land_use_code = row[col]
                        break

                if land_use_code is not None:
                    land_use_code = str(land_use_code).zfill(4)
                    pref_land_use[pref_code]['total_area'] += mesh_area

                    if land_use_code == '0500':
                        pref_land_use[pref_code]['forest_area'] += mesh_area
                    elif land_use_code == '0200':
                        pref_land_use[pref_code]['park_area'] += mesh_area

        processed += 1
        if i % 10 == 0:
            print(f"  処理済み: {i}/{len(l03b_files)}")

    except Exception as e:
        continue

print(f"\n[OK] L03-bファイル処理完了: {processed}ファイル\n")

# 緑地率計算
greenspace_data = []
for pref_code, data in pref_land_use.items():
    total_area = data['total_area']

    if total_area == 0:
        continue

    greenspace_area = data['forest_area'] + data['park_area']
    greenspace_ratio = (greenspace_area / total_area) * 100

    greenspace_data.append({
        'prefecture_code': pref_code,
        'prefecture_name': PREFECTURE_CODES[pref_code],
        'total_area_km2': total_area,
        'forest_area_km2': data['forest_area'],
        'park_area_km2': data['park_area'],
        'greenspace_area_km2': greenspace_area,
        'greenspace_ratio_percent': greenspace_ratio
    })

df_greenspace = pd.DataFrame(greenspace_data)

print(f"[OK] 緑地率計算完了: {len(df_greenspace)}都道府県\n")

# 保存
output_file = OUTPUT_DIR / "greenspace_ratio.csv"
df_greenspace = df_greenspace.sort_values('prefecture_code')
df_greenspace.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"[OK] 保存完了: {output_file}")
print(f"   - 行数: {len(df_greenspace)}")
print()

print("[INFO] 緑地率の基本統計量:")
print(df_greenspace['greenspace_ratio_percent'].describe())
print()

print("="*60)
print("[DONE] 処理完了（サンプル版）")
print("="*60)
