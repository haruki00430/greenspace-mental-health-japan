# -*- coding: utf-8 -*-
"""L03-bファイル読み込みテストスクリプト"""

import geopandas as gpd
from pathlib import Path
import zipfile
import tempfile

# テスト用ファイル
test_file = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\projects\NDB_XXX_greenspace_mental_health\data\raw\L03_b_Land_Use_All\L03-b-21_5339-jgd2011_GML.zip")

print("="*60)
print("L03-bファイル読み込みテスト")
print("="*60)

if not test_file.exists():
    print(f"[ERROR] ファイルが見つかりません: {test_file}")
    exit(1)

print(f"\n[INFO] テストファイル: {test_file.name}\n")

# ZIPファイルを展開
with tempfile.TemporaryDirectory() as temp_dir:
    with zipfile.ZipFile(test_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 展開されたファイルを確認
    print("[INFO] 展開されたファイル:")
    all_files = list(Path(temp_dir).glob("**/*"))
    for f in all_files:
        if f.is_file():
            print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")

    # XMLファイルを探す
    all_xml_files = list(Path(temp_dir).glob("**/*.xml"))
    print(f"\n[INFO] XMLファイル数: {len(all_xml_files)}")

    for xml_file in all_xml_files:
        print(f"\n  - {xml_file.name}")
        print(f"    サイズ: {xml_file.stat().st_size / 1024:.1f} KB")

    # GeoJSONファイルを優先的に探す
    geojson_files = list(Path(temp_dir).glob("**/*.geojson"))

    print(f"\n[INFO] GeoJSONファイル: {len(geojson_files)}")

    if geojson_files:
        target_file = geojson_files[0]
        print(f"\n[INFO] 読み込み対象: {target_file.name}")

        try:
            gdf = gpd.read_file(str(target_file))
            print(f"\n[OK] 読み込み成功")
            print(f"  - 行数: {len(gdf)}")
            print(f"  - 列数: {len(gdf.columns)}")
            print(f"  - CRS: {gdf.crs}")
            print(f"\n[INFO] カラム名:")
            for col in gdf.columns:
                print(f"  - {col}")

            print(f"\n[INFO] 先頭5行（土地利用コード列）:")
            if 'L03b_002' in gdf.columns:
                print(gdf[['L03b_002', 'geometry']].head(5))
            else:
                print(gdf.head(5))

        except Exception as e:
            print(f"\n[ERROR] 読み込み失敗: {e}")
    else:
        print("\n[ERROR] GeoJSONファイルが見つかりません")
