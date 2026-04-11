"""
国土数値情報L03-b（土地利用細分メッシュ）自動ダウンロードスクリプト

機能:
1. 全47都道府県のL03-b-18データをダウンロード
2. ZIPファイルを解凍
3. 緑地率計算用データの準備

使用データ:
- 国土数値情報L03-b（土地利用細分メッシュ）平成30年版（2018年）
- URL: https://nlftp.mlit.go.jp/ksj/gml/data/L03-b/L03-b-18/L03-b-18_{NN}_GML.zip

緑地の定義:
- 0100: 田
- 0200: 畑
- 0500: 森林
- 1400: 公園・緑地

出力:
- data/raw/L03-b_land_use/{NN}/ - 都道府県別データ
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


# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "L03-b_land_use"

# 国土数値情報L03-bダウンロードURL（平成30年版）
BASE_URL = "https://nlftp.mlit.go.jp/ksj/gml/data/L03-b/L03-b-18/L03-b-18_{pref_code:02d}_GML.zip"

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

# 土地利用区分コード
LAND_USE_CODES = {
    "0100": "田",
    "0200": "畑",
    "0500": "森林",
    "0600": "荒地",
    "0700": "建物用地",
    "0801": "道路",
    "0802": "鉄道",
    "0901": "その他の用地",
    "1000": "河川地及び湖沼",
    "1100": "海浜",
    "1400": "公園・緑地"
}

# 緑地として扱うコード
GREENSPACE_CODES = ["0100", "0200", "0500", "1400"]


def create_directories():
    """必要なディレクトリを作成"""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ ディレクトリ作成完了: {RAW_DATA_DIR}")


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

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"⚠️  データ未提供: {pref_name}（404 Not Found）")
        else:
            print(f"❌ ダウンロード失敗: {pref_name} - {e}")
        return False
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
        print(f"✅ 解凍完了: {zip_path.name}")
        return True
    except Exception as e:
        print(f"❌ 解凍失敗: {zip_path} - {e}")
        return False


def download_all_prefectures() -> List[Tuple[int, Path]]:
    """
    全都道府県のL03-bデータをダウンロード・解凍

    Returns:
        List[Tuple[int, Path]]: (都道府県コード, 解凍ディレクトリ)のリスト
    """
    success_list = []

    print("\n" + "="*60)
    print("国土数値情報L03-b（土地利用細分メッシュ）ダウンロード開始")
    print("="*60 + "\n")

    print("📝 緑地の定義:")
    for code in GREENSPACE_CODES:
        print(f"   - {code}: {LAND_USE_CODES[code]}")
    print()

    for pref_code, pref_name in PREFECTURES.items():
        # ダウンロードURL
        url = BASE_URL.format(pref_code=pref_code)

        # 保存先ディレクトリ
        pref_dir = RAW_DATA_DIR / f"{pref_code:02d}_{pref_name}"
        pref_dir.mkdir(parents=True, exist_ok=True)

        # ZIPファイルパス
        zip_path = pref_dir / f"L03-b-18_{pref_code:02d}_GML.zip"

        # ダウンロード
        if not download_file(url, zip_path, pref_name):
            continue

        # 解凍
        extract_dir = pref_dir / "extracted"
        if not extract_dir.exists():
            if not extract_zip(zip_path, extract_dir):
                continue
        else:
            print(f"⏭️  解凍スキップ（既存）: {pref_name}")

        success_list.append((pref_code, extract_dir))

        # サーバー負荷軽減のため少し待機
        time.sleep(0.5)

    print(f"\n✅ ダウンロード・解凍完了: {len(success_list)}/47都道府県\n")
    return success_list


def create_summary_report(success_list: List[Tuple[int, Path]]):
    """
    ダウンロード結果のサマリーレポートを作成

    Args:
        success_list: (都道府県コード, 解凍ディレクトリ)のリスト
    """
    print("\n" + "="*60)
    print("ダウンロード結果サマリー")
    print("="*60 + "\n")

    print(f"✅ 成功: {len(success_list)}/47都道府県\n")

    if len(success_list) < 47:
        failed_codes = set(PREFECTURES.keys()) - set([code for code, _ in success_list])
        print("❌ 失敗した都道府県:")
        for code in sorted(failed_codes):
            print(f"   - {code:02d}: {PREFECTURES[code]}")
        print()

    # ファイルサイズの合計計算
    total_size = 0
    for pref_code, extract_dir in success_list:
        pref_dir = extract_dir.parent
        zip_path = pref_dir / f"L03-b-18_{pref_code:02d}_GML.zip"
        if zip_path.exists():
            total_size += zip_path.stat().st_size

    print(f"💾 ダウンロード合計サイズ: {total_size / 1024 / 1024 / 1024:.2f} GB")
    print()

    # 次のステップ案内
    print("📌 次のステップ:")
    print("   1. 緑地率計算スクリプトの実行:")
    print("      python 03_Analysis/scripts/01_greenspace_calculation.py")
    print()
    print("   2. 都道府県別緑地率データの生成:")
    print("      → data/interim/greenspace_ratio.csv")
    print()


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print(" 国土数値情報L03-b（土地利用細分メッシュ）自動ダウンロードスクリプト")
    print("="*80 + "\n")

    # ディレクトリ作成
    create_directories()

    # 全都道府県ダウンロード
    success_list = download_all_prefectures()

    if not success_list:
        print("❌ ダウンロードに成功した都道府県がありません。")
        sys.exit(1)

    # サマリーレポート
    create_summary_report(success_list)

    print("="*80)
    print("✅ 全処理完了！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
