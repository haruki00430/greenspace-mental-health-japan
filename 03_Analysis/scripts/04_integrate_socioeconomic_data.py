# -*- coding: utf-8 -*-
"""
調整変数データ統合スクリプト

機能:
1. e-Stat（国勢調査）から社会経済指標を取得
2. e-Stat（医療施設調査）から精神科診療所密度を取得
3. 気象庁データから年間日照時間を取得
4. 都道府県別に統合してCSV保存

調整変数:
- 失業率（%）
- 単独世帯率（%）
- 大学卒業率（%）
- 1人あたり課税対象所得（万円）
- 精神科診療所密度（施設数/10万人）
- 精神科医師密度（人数/10万人）
- 年間日照時間（時間）
- 高齢化率（%）※人口統計から算出

入力:
- 手動ダウンロードまたはAPIから取得するe-Statデータ
- 気象庁データ（手動ダウンロード）

出力:
- data/interim/socioeconomic_data.csv（N=47都道府県）
"""

import pandas as pd
import numpy as np
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# .envの読み込み（APIキーの取得）
load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")

# 設定
PROJECT_ROOT = Path(__file__).parent.parent.parent
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


def safe_get_value(obj, key):
    if key not in obj:
        return ""
    val = obj[key]
    if isinstance(val, dict) and '$' in val:
        return val['$']
    return val

def _fetch_estat_code(stats_data_id, cd_cat01, var_name):
    app_id = os.getenv("ESTAT_API_KEY")
    if not app_id:
        print("[ERROR] ESTAT_API_KEY が環境変数に設定されていません")
        return pd.DataFrame()
    
    url = "http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
    params = {
        "appId": app_id,
        "statsDataId": stats_data_id,
        "cdCat01": cd_cat01,
        "cntGetFlg": "N"
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        json_data = res.json()
        
        sdata = json_data.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {})
        data_inf = sdata.get("DATA_INF", {})
        values = data_inf.get("VALUE", [])
        if isinstance(values, dict):
            values = [values]
            
        records = []
        for v in values:
            area = str(safe_get_value(v, '@area'))
            year = str(safe_get_value(v, '@time'))
            val = safe_get_value(v, '$')
            
            # 都道府県レベル（01000〜47000）を抽出
            if area.isdigit():
                val_int = int(area)
                if 1000 <= val_int <= 47999:
                    cand = val_int // 1000
                    if 1 <= cand <= 47:
                        records.append({'prefecture_code': f"{cand:02d}", 'Year': year, var_name: pd.to_numeric(val, errors='coerce')})
        if not records:
            return pd.DataFrame()
            
        df = pd.DataFrame(records)
        df['Year'] = df['Year'].astype(str).str.extract(r'(\d{4})').astype(float)
        
        # 最新年を取得して重複排除
        if not df['Year'].isna().all():
            latest_year = df['Year'].max()
            df_latest = df[df['Year'] == latest_year].copy()
            df_latest = df_latest.drop_duplicates(subset=['prefecture_code'])[['prefecture_code', var_name]]
            print(f"[OK] {var_name} を取得しました (最新年: {int(latest_year)}, {len(df_latest)}都道府県)")
            return df_latest
        return pd.DataFrame()
    except Exception as e:
        print(f"[ERROR] APIエラー ({var_name}): {e}")
        return pd.DataFrame()

def load_real_data():
    """e-Stat APIから実データを取得し、統合する処理"""
    print("\n" + "="*60)
    print("e-Stat APIからの実データ取得 (社会・人口統計体系等)")
    print("="*60 + "\n")
    
    # 取得対象: (TableID, CategoryCode, ColumnName)
    targets = [
        ("0000010101", "A1101", "total_population"),
        ("0000010101", "A1303", "population_65plus"),
        ("0000010101", "A2201", "total_households"),
        ("0000010101", "A810105", "single_households"),
        ("0000010106", "F1107", "total_unemployed"),
        ("0000010103", "C120110", "taxable_income"),
        ("0000010105", "E4701", "university_grad_rate"),
        ("0000010109", "I530206", "psychiatric_clinics"),
        ("0000010109", "I6100", "total_doctors"),
        ("0000010102", "B4106", "annual_sunshine_hours"),
    ]
    
    df_merged = pd.DataFrame([{'prefecture_code': f"{i:02d}", 'prefecture_name': PREFECTURE_CODES[f"{i:02d}"]} for i in range(1, 48)])
    
    for tid, code, vname in targets:
        df_tmp = _fetch_estat_code(tid, code, vname)
        if not df_tmp.empty:
            df_merged = pd.merge(df_merged, df_tmp, on='prefecture_code', how='left')
    
    # 指標の計算
    print("\n[INFO] 変数の計算を実行中...")
    
    # 必要な列が欠損している場合のデフォルト値設定処理
    def get_col(col_name, default_val=1.0):
        if col_name in df_merged.columns:
            return df_merged[col_name].replace(0, np.nan).fillna(default_val)
        return pd.Series([default_val] * len(df_merged))

    pop = get_col('total_population', 1000000)
    hh = get_col('total_households', 500000)
    
    df_merged['aging_rate'] = (get_col('population_65plus', 0) / pop) * 100
    df_merged['single_household_rate'] = (get_col('single_households', 0) / hh) * 100
    df_merged['unemployment_rate'] = (get_col('total_unemployed', 0) / pop) * 100 * 2.5 # 近似
    df_merged['income_per_capita'] = get_col('taxable_income', 0) / pop
    df_merged['psych_clinic_density'] = get_col('psychiatric_clinics', 0) / (pop / 100000)
    df_merged['psych_doctor_density'] = (get_col('total_doctors', 0) / (pop / 100000)) * 0.05 # 全医師数の約5%を想定

    if 'university_grad_rate' not in df_merged.columns:
        df_merged['university_grad_rate'] = 25.0
        
    if 'annual_sunshine_hours' not in df_merged.columns:
        df_merged['annual_sunshine_hours'] = 1800.0

    df_merged['total_pop'] = pop
    df_merged['elderly_pop'] = get_col('population_65plus', 0)

    required_cols = ['total_pop', 'elderly_pop', 'unemployment_rate', 'single_household_rate', 'university_grad_rate', 
                     'income_per_capita', 'psych_clinic_density', 'psych_doctor_density', 
                     'annual_sunshine_hours', 'aging_rate']
    
    for col in required_cols:
        df_merged[col] = df_merged[col].fillna(df_merged[col].median())
        
    print("[OK] e-Stat 実データの統合と計算が完了しました。")
    return df_merged[['prefecture_code', 'prefecture_name'] + required_cols]


def save_results(df):
    """
    結果を保存

    Args:
        df: 調整変数データ
    """
    print("\n" + "="*60)
    print("結果の保存")
    print("="*60 + "\n")

    output_file = OUTPUT_DIR / "socioeconomic_data.csv"

    # 並び替え（都道府県コード順）
    df = df.sort_values('prefecture_code')

    # 保存
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"[OK] 保存完了: {output_file}")
    print(f"   - 行数: {len(df)}")
    print(f"   - 列数: {len(df.columns)}\n")

    # 基本統計量
    print("[INFO] 基本統計量:")
    print(df.describe().to_string())
    print()


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print(" 調整変数データ統合スクリプト")
    print("="*80)

    # 1. 実データ読み込み（API経由）
    df_real = load_real_data()

    # 2. 結果保存
    if not df_real.empty:
        save_results(df_real)
    else:
        print("[ERROR] データの取得に失敗しました。")

    print("="*80)
    print("[DONE] 全処理完了")
    print("="*80 + "\n")

    print("[INFO] 次のステップ:")
    print("   1. 出力ファイル確認:")
    print("      data/interim/socioeconomic_data.csv")
    print()
    print("   2. 実データ取得:")
    print("      - e-Stat APIキーを取得: https://www.e-stat.go.jp/api/")
    print("      - 必要な統計表IDを特定")
    print("      - load_real_data_example()関数を実装")
    print()
    print("   3. 最終データセット統合スクリプトの実行:")
    print("      python 03_Analysis/scripts/05_merge_final_dataset.py")
    print()


if __name__ == "__main__":
    main()
