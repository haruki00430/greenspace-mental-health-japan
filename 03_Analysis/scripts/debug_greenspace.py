# -*- coding: utf-8 -*-
"""緑地率計算デバッグスクリプト"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import zipfile
import tempfile

# テストファイル
test_l03b = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\projects\NDB_XXX_greenspace_mental_health\data\raw\L03_b_Land_Use_All\L03-b-21_5339-jgd2011_GML.zip")
A38_DIR = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\A38_Medical_Area")

print("="*60)
print("緑地率計算デバッグ")
print("="*60)

# A38読み込み
print("\n[STEP 1] A38ポリゴン読み込み")
a38_file = list(A38_DIR.glob("**/*_2.geojson"))[0]
gdf_a38 = gpd.read_file(a38_file)
print(f"  A38行数: {len(gdf_a38)}")
print(f"  A38 CRS: {gdf_a38.crs}")
print(f"  A38カラム: {gdf_a38.columns.tolist()}")
print(f"  A38b_003サンプル: {gdf_a38['A38b_003'].head(3).tolist()}")

# 都道府県コード抽出
gdf_a38['pref_code'] = gdf_a38['A38b_003'].astype(str).str[:2]
print(f"  都道府県コードサンプル: {gdf_a38['pref_code'].head(3).tolist()}")

# L03-b読み込み
print("\n[STEP 2] L03-bメッシュ読み込み")
with tempfile.TemporaryDirectory() as temp_dir:
    with zipfile.ZipFile(test_l03b, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    geojson_files = list(Path(temp_dir).glob("**/*.geojson"))
    gdf_mesh = gpd.read_file(str(geojson_files[0]))

print(f"  L03-b行数: {len(gdf_mesh)}")
print(f"  L03-b CRS: {gdf_mesh.crs}")
print(f"  L03-bカラム: {gdf_mesh.columns.tolist()}")

# CRS変換
print("\n[STEP 3] CRS変換")
print(f"  変換前: {gdf_mesh.crs}")
gdf_mesh_transformed = gdf_mesh.to_crs(gdf_a38.crs)
print(f"  変換後: {gdf_mesh_transformed.crs}")

# 空間結合テスト（最初の100行のみ）
print("\n[STEP 4] 空間結合テスト（最初の100行）")
gdf_joined = gpd.sjoin(gdf_mesh_transformed.head(100), gdf_a38[['pref_code', 'geometry']],
                       how='inner', predicate='intersects')

print(f"  結合後行数: {len(gdf_joined)}")

if len(gdf_joined) > 0:
    print(f"  結合後カラム: {gdf_joined.columns.tolist()}")
    print(f"  都道府県コードサンプル: {gdf_joined['pref_code'].head(5).tolist()}")
    print(f"\n  先頭5行:")
    print(gdf_joined[['pref_code', '土地利用細分']].head(5))
else:
    print("  [ERROR] 空間結合が0件！")
    print(f"\n  A38範囲: {gdf_a38.total_bounds}")
    print(f"  L03-b範囲: {gdf_mesh_transformed.total_bounds}")
