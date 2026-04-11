# -*- coding: utf-8 -*-
"""
スクリプト04: 調整変数データ統合

以下のデータを統合して最終的な解析用データセットを作成：
1. 緑地率データ（greenspace_ratio.csv）
2. NDB処方薬データ（psychiatric_prescriptions.csv）
3. 社会経済指標データ（ses_data_comprehensive.csv）

出力:
- data/processed/analysis_dataset.csv（N=47都道府県 × 約15変数）
"""

import pandas as pd
from pathlib import Path
import sys

# ============================================================
# パス設定
# ============================================================

# プロジェクトフォルダ（NDB_XXX_greenspace_mental_health）
GREENSPACE_PROJECT = Path(__file__).resolve().parents[2]  # 03_Analysis/scripts/ → NDB_XXX_greenspace_mental_health
# NDB_Research_Hubルート
NDB_ROOT = GREENSPACE_PROJECT.parents[1]  # NDB_XXX_greenspace_mental_health → projects → NDB_Research_Hub

DATA_DIR = GREENSPACE_PROJECT / "data"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

# データソース
# 注意: greenspace_ratio.csvは projects/data/interim/ に保存されている（プランCで作成）
GREENSPACE_FILE = NDB_ROOT / "projects" / "data" / "interim" / "greenspace_ratio.csv"
PRESCRIPTION_FILE = INTERIM_DIR / "psychiatric_prescriptions.csv"
SES_FILE = NDB_ROOT / "projects" / "NDB_XXX_diabetes_ses" / "data" / "interim" / "ses_data_comprehensive.csv"

# 出力
OUTPUT_FILE = PROCESSED_DIR / "analysis_dataset.csv"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

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
# データ読み込み関数
# ============================================================

def load_greenspace_data():
    """緑地率データ読み込み"""
    print("\n[STEP 1] 緑地率データ読み込み")

    if not GREENSPACE_FILE.exists():
        print(f"[ERROR] ファイルが見つかりません: {GREENSPACE_FILE}")
        sys.exit(1)

    df = pd.read_csv(GREENSPACE_FILE, encoding='utf-8-sig')
    print(f"  読み込み完了: {len(df)}都道府県")
    print(f"  変数: {df.columns.tolist()}")

    return df

def load_prescription_data():
    """NDB処方薬データ読み込み"""
    print("\n[STEP 2] NDB処方薬データ読み込み")

    if not PRESCRIPTION_FILE.exists():
        print(f"[ERROR] ファイルが見つかりません: {PRESCRIPTION_FILE}")
        sys.exit(1)

    df = pd.read_csv(PRESCRIPTION_FILE, encoding='utf-8-sig')
    print(f"  読み込み完了: {len(df)}都道府県")
    print(f"  変数: {df.columns.tolist()}")

    return df

def load_ses_data():
    """社会経済指標データ読み込み"""
    print("\n[STEP 3] 社会経済指標データ読み込み")

    if not SES_FILE.exists():
        print(f"[ERROR] ファイルが見つかりません: {SES_FILE}")
        sys.exit(1)

    df = pd.read_csv(SES_FILE, encoding='utf-8-sig')
    print(f"  読み込み完了: {len(df)}都道府県")
    print(f"  変数: {df.columns.tolist()}")

    return df

# ============================================================
# データ統合
# ============================================================

def integrate_datasets():
    """全データセットを統合"""

    print("=" * 80)
    print(" 調整変数データ統合")
    print("=" * 80)

    # データ読み込み
    df_greenspace = load_greenspace_data()
    df_prescription = load_prescription_data()
    df_ses = load_ses_data()

    # SESデータに都道府県コード追加
    print("\n[STEP 4] SESデータに都道府県コード追加")
    code_map_reversed = {v: k for k, v in PREFECTURE_CODES.items()}
    df_ses['prefecture_code'] = df_ses['prefecture'].map(code_map_reversed)
    print(f"  都道府県コード追加完了")

    # データ型を統一（prefecture_codeをstr型、ゼロ埋め2桁に）
    print("\n[STEP 4b] データ型統一（prefecture_code → str, ゼロ埋め2桁）")
    df_greenspace['prefecture_code'] = df_greenspace['prefecture_code'].astype(str).str.zfill(2)
    df_prescription['prefecture_code'] = df_prescription['prefecture_code'].astype(str).str.zfill(2)
    df_ses['prefecture_code'] = df_ses['prefecture_code'].astype(str).str.zfill(2)
    print(f"  データ型統一完了")

    # マージ1: 緑地率 + 処方薬
    print("\n[STEP 5] データ統合（緑地率 + 処方薬）")
    df_merged = df_greenspace.merge(
        df_prescription,
        on='prefecture_code',
        how='inner',
        suffixes=('_greenspace', '_prescription')
    )
    print(f"  統合後: {len(df_merged)}都道府県")

    # マージ2: + SES
    print("\n[STEP 6] データ統合（+ 社会経済指標）")
    df_final = df_merged.merge(
        df_ses,
        on='prefecture_code',
        how='inner',
        suffixes=('', '_ses')
    )
    print(f"  最終統合後: {len(df_final)}都道府県")

    # 列名整理
    print("\n[STEP 7] 列名整理")

    # 重複列の削除（prefecture列の選択）
    if 'prefecture_greenspace' in df_final.columns:
        df_final = df_final.drop(columns=['prefecture_greenspace'])
    if 'prefecture_prescription' in df_final.columns:
        df_final = df_final.drop(columns=['prefecture_prescription'])

    # 最終的な変数選択と並び順
    final_columns = [
        'prefecture_code',
        'prefecture',
        # 緑地指標
        'greenspace_ratio_percent',
        'forest_area_km2',
        'park_area_km2',
        'greenspace_area_km2',
        'total_area_km2',
        # アウトカム（処方薬）
        'total_quantity',
        # 社会経済指標（調整変数）
        'aging_rate',
        'pop_density',
        'income_per_capita',
        'college_graduate_rate',
        'total_pop',
        'elderly_pop',
        'area'
    ]

    # 存在する列のみ選択
    available_columns = [col for col in final_columns if col in df_final.columns]
    df_final = df_final[available_columns]

    print(f"  最終変数数: {len(available_columns)}変数")
    print(f"  変数リスト:")
    for i, col in enumerate(available_columns, 1):
        print(f"    {i}. {col}")

    # 欠損値確認
    print("\n[STEP 8] 欠損値確認")
    missing_counts = df_final.isnull().sum()
    if missing_counts.sum() > 0:
        print("  欠損値あり:")
        for col, count in missing_counts[missing_counts > 0].items():
            print(f"    {col}: {count}件")
    else:
        print("  欠損値なし [OK]")

    # 記述統計
    print("\n[STEP 9] 記述統計（主要変数）")
    key_vars = [
        'greenspace_ratio_percent',
        'total_quantity',
        'aging_rate',
        'pop_density',
        'income_per_capita'
    ]

    for var in key_vars:
        if var in df_final.columns:
            print(f"\n  {var}:")
            print(f"    平均: {df_final[var].mean():.2f}")
            print(f"    標準偏差: {df_final[var].std():.2f}")
            print(f"    最小値: {df_final[var].min():.2f}")
            print(f"    最大値: {df_final[var].max():.2f}")

    # 保存
    print(f"\n[STEP 10] 最終データセット保存")
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"  保存完了: {OUTPUT_FILE}")
    print(f"  データサイズ: {len(df_final)}行 × {len(df_final.columns)}列")

    # サンプル表示
    print(f"\n[サンプル] 先頭5行:")
    print(df_final.head(5).to_string(index=False))

    return df_final

# ============================================================
# メイン実行
# ============================================================

if __name__ == "__main__":
    df_result = integrate_datasets()

    print("\n" + "=" * 80)
    print(" 処理完了")
    print("=" * 80)
    print(f"\n最終データセット: {OUTPUT_FILE}")
    print(f"サンプルサイズ: N={len(df_result)}都道府県")
    print(f"変数数: {len(df_result.columns)}変数")
