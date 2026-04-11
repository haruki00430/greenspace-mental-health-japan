"""
国土数値情報A38（二次医療圏データ）自動ダウンロードスクリプト

機能:
1. 全47都道府県のA38-20データをダウンロード
2. ZIPファイルを解凍
3. GMLをGeoJSONに変換（geopandas使用）
4. 全都道府県のGeoJSONを統合
5. 都道府県ポリゴンを作成（dissolve）

使用データ:
- 国土数値情報A38（二次医療圏）令和2年版
- URL: https://nlftp.mlit.go.jp/ksj/gml/data/A38/A38-20/A38-20_{NN}_GML.zip

出力:
- data/raw/A38_secondary_areas/{NN}/ - 都道府県別GeoJSON
- data/interim/national_secondary_areas.geojson - 全国統合データ
- data/interim/prefecture_boundaries.geojson - 都道府県ポリゴン
"""

import os
import sys
import requests
import zipfile
from pathlib import Path
from typing import List, Tuple
import time

# プログレスバー（オプション）
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("警告: tqdmがインストールされていません。進捗バーは表示されません。")
    print("インストール: pip install tqdm")

# geopandas（GML→GeoJSON変換用）
try:
    import geopandas as gpd
    import pandas as pd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("エラー: geopandasがインストールされていません。")
    print("インストール: pip install geopandas")
    sys.exit(1)


# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "A38_secondary_areas"
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"

# 国土数値情報A38ダウンロードURL
BASE_URL = "https://nlftp.mlit.go.jp/ksj/gml/data/A38/A38-20/A38-20_{pref_code:02d}_GML.zip"

# 都道府県コードと名称のマッピング
PREFECTURES = {
    1: "北海道", 2: "青森県", 3: "岩手県", 4: "宮城県", 5: "秋田県",
    6: "山形県", 7: "福島県", 8: "茨城県", 9: "栃木県", 10: "群馬県",
    11: "埼玉県", 12: "千葉県", 13: "東京都", 14: "神奈川県", 15: "新潟県",
    16: "富山県", 17: "石川県", 18: "福井県", 19: "山梨県", 20: "長野県",
    21: "岐阜県", 22: "静岡県", 23: "愛知県", 24: "三重県", 25: "滋賀県",
    26: "京都府", 27: "大阪府", 28: "兵庫県", 29: "奈良県", 30: "和歌山県",
    31: "鳥取県", 32: "島根県", 33: "岡山県", 34: "広島県", 35: "山口県",
    36: "徳島県", 37: "香川県", 38: "愛媛県", 39: "高知県", 40: "福岡県",
    41: "佐賀県", 42: "長崎県", 43: "熊本県", 44: "大分県", 45: "宮崎県",
    46: "鹿児島県", 47: "沖縄県"
}


def create_directories():
    """必要なディレクトリを作成"""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ ディレクトリ作成完了: {RAW_DATA_DIR}")
    print(f"✅ ディレクトリ作成完了: {INTERIM_DATA_DIR}")


def download_file(url: str, output_path: Path, pref_name: str) -> bool:
    """
    ファイルをダウンロード

    Args:
        url: ダウンロードURL
        output_path: 保存先パス
        pref_name: 都道府県名（ログ用）

    Returns:
        bool: 成功ならTrue
    """
    try:
        # ダウンロード済みチェック
        if output_path.exists():
            print(f"⏭️  スキップ（既存）: {pref_name} - {output_path.name}")
            return True

        print(f"📥 ダウンロード中: {pref_name}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        # ファイルサイズ取得
        total_size = int(response.headers.get('content-length', 0))

        # ダウンロード
        if HAS_TQDM and total_size > 0:
            with open(output_path, 'wb') as f, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=pref_name
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
        else:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f"✅ ダウンロード完了: {pref_name} ({total_size / 1024 / 1024:.2f} MB)")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ ダウンロード失敗: {pref_name} - {e}")
        return False


def extract_zip(zip_path: Path, extract_dir: Path) -> bool:
    """
    ZIPファイルを解凍

    Args:
        zip_path: ZIPファイルパス
        extract_dir: 解凍先ディレクトリ

    Returns:
        bool: 成功ならTrue
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return True
    except Exception as e:
        print(f"❌ 解凍失敗: {zip_path} - {e}")
        return False


def convert_gml_to_geojson(gml_path: Path, output_path: Path, layer: str = None) -> bool:
    """
    GMLをGeoJSONに変換

    Args:
        gml_path: GMLファイルパス
        output_path: GeoJSON出力パス
        layer: レイヤー名（Noneなら自動検出）

    Returns:
        bool: 成功ならTrue
    """
    try:
        # GMLファイルの検索
        gml_files = list(gml_path.parent.glob("*.gml"))

        if not gml_files:
            print(f"❌ GMLファイルが見つかりません: {gml_path.parent}")
            return False

        gml_file = gml_files[0]  # 最初のGMLファイルを使用

        # Layer 2（二次医療圏）を読み込み
        # fiona.listlayers()で確認可能だが、通常は Layer 2 = "_2"
        try:
            # まずレイヤー名を推定
            import fiona
            layers = fiona.listlayers(str(gml_file))

            # "_2" を含むレイヤーを探す（二次医療圏データ）
            target_layer = None
            for layer_name in layers:
                if "_2" in layer_name or "二次医療圏" in layer_name:
                    target_layer = layer_name
                    break

            if target_layer is None:
                # デフォルトで2番目のレイヤーを使用
                target_layer = layers[1] if len(layers) > 1 else layers[0]

            gdf = gpd.read_file(gml_file, layer=target_layer)

        except Exception as e:
            print(f"⚠️  レイヤー指定なしで読み込み試行: {e}")
            gdf = gpd.read_file(gml_file)

        # GeoJSONとして保存
        gdf.to_file(output_path, driver='GeoJSON', encoding='utf-8')

        print(f"✅ GeoJSON変換完了: {output_path.name} ({len(gdf)} features)")
        return True

    except Exception as e:
        print(f"❌ GeoJSON変換失敗: {gml_path} - {e}")
        return False


def download_all_prefectures() -> List[Tuple[int, Path]]:
    """
    全都道府県のA38データをダウンロード・変換

    Returns:
        List[Tuple[int, Path]]: (都道府県コード, GeoJSONパス)のリスト
    """
    success_list = []

    print("\n" + "="*60)
    print("国土数値情報A38（二次医療圏）ダウンロード開始")
    print("="*60 + "\n")

    for pref_code, pref_name in PREFECTURES.items():
        # ダウンロードURL
        url = BASE_URL.format(pref_code=pref_code)

        # 保存先ディレクトリ
        pref_dir = RAW_DATA_DIR / f"{pref_code:02d}_{pref_name}"
        pref_dir.mkdir(parents=True, exist_ok=True)

        # ZIPファイルパス
        zip_path = pref_dir / f"A38-20_{pref_code:02d}_GML.zip"

        # ダウンロード
        if not download_file(url, zip_path, pref_name):
            continue

        # 解凍
        extract_dir = pref_dir / "extracted"
        if not extract_dir.exists():
            if not extract_zip(zip_path, extract_dir):
                continue

        # GML→GeoJSON変換
        geojson_path = pref_dir / f"secondary_areas_{pref_code:02d}.geojson"
        if not geojson_path.exists():
            gml_dir = extract_dir
            if not convert_gml_to_geojson(gml_dir, geojson_path):
                continue

        success_list.append((pref_code, geojson_path))

        # サーバー負荷軽減のため少し待機
        time.sleep(0.5)

    print(f"\n✅ ダウンロード・変換完了: {len(success_list)}/47都道府県\n")
    return success_list


def merge_geojson_files(geojson_paths: List[Tuple[int, Path]], output_path: Path):
    """
    全都道府県のGeoJSONを統合

    Args:
        geojson_paths: (都道府県コード, GeoJSONパス)のリスト
        output_path: 統合GeoJSONの出力パス
    """
    print("\n" + "="*60)
    print("全国二次医療圏データの統合")
    print("="*60 + "\n")

    try:
        gdf_list = []

        for pref_code, geojson_path in geojson_paths:
            gdf = gpd.read_file(geojson_path)
            # 都道府県コードを追加
            gdf['pref_code'] = f"{pref_code:02d}"
            gdf_list.append(gdf)

        # 統合
        gdf_national = pd.concat(gdf_list, ignore_index=True)

        # 保存
        gdf_national.to_file(output_path, driver='GeoJSON', encoding='utf-8')

        print(f"✅ 全国統合完了: {len(gdf_national)} 二次医療圏")
        print(f"   出力: {output_path}")

        # 統計情報
        print(f"\n📊 データ統計:")
        print(f"   - 総レコード数: {len(gdf_national)}")
        print(f"   - カラム数: {len(gdf_national.columns)}")
        print(f"   - CRS: {gdf_national.crs}")

        # 重要カラムの確認
        important_cols = ['A38b_003', 'A38b_007', 'A38b_011']
        for col in important_cols:
            if col in gdf_national.columns:
                print(f"   - {col}: ✅ 存在")
            else:
                print(f"   - {col}: ❌ 不在")

        return gdf_national

    except Exception as e:
        print(f"❌ 統合失敗: {e}")
        return None


def create_prefecture_boundaries(national_gdf: gpd.GeoDataFrame, output_path: Path):
    """
    都道府県ポリゴンを作成（二次医療圏をdissolve）

    Args:
        national_gdf: 全国二次医療圏GeoDataFrame
        output_path: 都道府県ポリゴンの出力パス
    """
    print("\n" + "="*60)
    print("都道府県ポリゴンの作成")
    print("="*60 + "\n")

    try:
        # pref_codeでdissolve
        gdf_pref = national_gdf.dissolve(by='pref_code', aggfunc='first')

        # インデックスをリセット
        gdf_pref = gdf_pref.reset_index()

        # 保存
        gdf_pref.to_file(output_path, driver='GeoJSON', encoding='utf-8')

        print(f"✅ 都道府県ポリゴン作成完了: {len(gdf_pref)} 都道府県")
        print(f"   出力: {output_path}")

        return gdf_pref

    except Exception as e:
        print(f"❌ 都道府県ポリゴン作成失敗: {e}")
        return None


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print(" 国土数値情報A38（二次医療圏データ）自動ダウンロードスクリプト")
    print("="*80 + "\n")

    # ディレクトリ作成
    create_directories()

    # 全都道府県ダウンロード
    success_list = download_all_prefectures()

    if not success_list:
        print("❌ ダウンロードに成功した都道府県がありません。")
        sys.exit(1)

    # 全国統合
    national_output = INTERIM_DATA_DIR / "national_secondary_areas.geojson"
    national_gdf = merge_geojson_files(success_list, national_output)

    if national_gdf is None:
        print("❌ 全国統合に失敗しました。")
        sys.exit(1)

    # 都道府県ポリゴン作成
    prefecture_output = INTERIM_DATA_DIR / "prefecture_boundaries.geojson"
    pref_gdf = create_prefecture_boundaries(national_gdf, prefecture_output)

    if pref_gdf is None:
        print("⚠️  都道府県ポリゴン作成に失敗しましたが、処理は続行します。")

    print("\n" + "="*80)
    print("✅ 全処理完了！")
    print("="*80 + "\n")

    print("📁 出力ファイル:")
    print(f"   1. {national_output}")
    print(f"   2. {prefecture_output}")
    print("\n次のステップ: 緑地率計算スクリプト（01_greenspace_calculation.py）の実行\n")


if __name__ == "__main__":
    main()
