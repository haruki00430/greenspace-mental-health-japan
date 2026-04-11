# -*- coding: utf-8 -*-
"""
e-Stat公式統計データから都道府県別緑地率を計算

データソース:
1. 林野庁「都道府県別森林率」（令和4年3月31日現在）
   URL: https://www.rinya.maff.go.jp/j/keikaku/genkyou/r4/1.html
2. 国土交通省「都市公園等整備現況」（令和3年3月31日現在）
   URL: https://uub.jp/pdr/h/park.html (Ministry of Land, Infrastructure, Transport and Tourism)

緑地率定義:
緑地面積 = 森林面積 + 都市公園面積
緑地率 = (緑地面積 / 国土面積) × 100
"""

import pandas as pd
from pathlib import Path

# ============================================================
# 定数定義
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
# 森林率データ（林野庁 令和4年3月31日現在）
# ============================================================

forest_data_csv = """都道府県名,森林率（%）,森林面積（ha）,国土面積（ha）
北海道,71,5536144,7842135
青森県,66,633209,964562
岩手県,77,1169302,1527501
宮城県,57,414436,728229
秋田県,72,839290,1163752
山形県,72,669218,932313
福島県,71,972062,1378414
茨城県,31,189271,609724
栃木県,54,347463,640809
群馬県,67,424860,636228
埼玉県,31,119223,379775
千葉県,29,148400,515731
東京都,36,78937,219405
神奈川県,39,94258,241611
新潟県,68,855084,1258395
富山県,67,284015,424754
石川県,68,285481,418620
福井県,74,311037,419052
山梨県,78,348283,446527
長野県,79,1066951,1356156
岐阜県,81,861169,1062129
静岡県,64,496315,777728
愛知県,42,217660,517315
三重県,64,371837,577447
滋賀県,51,203868,401738
京都府,74,342250,461220
大阪府,30,56738,190534
兵庫県,67,558750,840094
奈良県,77,283689,369094
和歌山県,77,361538,472468
鳥取県,74,259122,350714
島根県,78,524363,670790
岡山県,68,484745,711433
広島県,72,611576,847922
山口県,71,436732,611255
徳島県,76,314703,414699
香川県,47,87829,187692
愛媛県,71,400958,567612
高知県,84,594090,710360
福岡県,45,224136,498686
佐賀県,45,110783,244067
長崎県,59,242775,413098
熊本県,62,459008,740939
大分県,71,450891,634070
宮崎県,76,585257,773500
鹿児島県,65,593959,918642
沖縄県,45,103149,228215"""

# ============================================================
# 都市公園面積データ（国土交通省 令和3年3月31日現在）
# ============================================================

park_data_csv = """都道府県,面積(ha)
北海道,14223
秋田県,1887
宮崎県,1937
宮城県,4142
山形県,1883
青森県,2107
香川県,1617
島根県,1105
富山県,1639
福井県,1199
岡山県,2922
山口県,2025
栃木県,2819
新潟県,3128
石川県,1573
奈良県,1830
長野県,2817
群馬県,2653
福島県,2480
岩手県,1583
兵庫県,7122
鹿児島県,1953
鳥取県,658
長崎県,1556
愛媛県,1574
大分県,1281
佐賀県,913
高知県,761
広島県,2999
沖縄県,1535
岐阜県,2037
茨城県,2834
山梨県,798
三重県,1739
福岡県,4793
滋賀県,1279
熊本県,1545
静岡県,3173
和歌山県,759
徳島県,589
愛知県,5936
京都府,1996
埼玉県,5228
千葉県,4352
大阪府,5024
神奈川県,5185
東京都,5991"""

# ============================================================
# データ処理
# ============================================================

def create_greenspace_ratio():
    """緑地率データセットを作成"""

    print("=" * 80)
    print(" e-Stat公式統計から緑地率データセット作成")
    print("=" * 80)

    # 森林データ読み込み
    from io import StringIO
    df_forest = pd.read_csv(StringIO(forest_data_csv))
    print(f"\n[OK] 森林データ読み込み: {len(df_forest)}都道府県")

    # 都市公園データ読み込み
    df_park = pd.read_csv(StringIO(park_data_csv))
    print(f"[OK] 都市公園データ読み込み: {len(df_park)}都道府県")

    # データ統合（都道府県名でマージ）
    df_merged = df_forest.merge(
        df_park,
        left_on='都道府県名',
        right_on='都道府県',
        how='left'
    )

    # 都道府県コード追加
    code_map_reversed = {v: k for k, v in PREFECTURE_CODES.items()}
    df_merged['prefecture_code'] = df_merged['都道府県名'].map(code_map_reversed)

    # 緑地面積・緑地率計算
    # 1 ha = 0.01 km²
    df_merged['forest_area_km2'] = df_merged['森林面積（ha）'] * 0.01
    df_merged['park_area_km2'] = df_merged['面積(ha)'] * 0.01
    df_merged['total_area_km2'] = df_merged['国土面積（ha）'] * 0.01
    df_merged['greenspace_area_km2'] = df_merged['forest_area_km2'] + df_merged['park_area_km2']
    df_merged['greenspace_ratio_percent'] = (
        df_merged['greenspace_area_km2'] / df_merged['total_area_km2']
    ) * 100

    # 最終データセット作成
    df_output = df_merged[[
        'prefecture_code',
        '都道府県名',
        'total_area_km2',
        'forest_area_km2',
        'park_area_km2',
        'greenspace_area_km2',
        'greenspace_ratio_percent'
    ]].copy()

    df_output.columns = [
        'prefecture_code',
        'prefecture_name',
        'total_area_km2',
        'forest_area_km2',
        'park_area_km2',
        'greenspace_area_km2',
        'greenspace_ratio_percent'
    ]

    # 都道府県コード順にソート
    df_output = df_output.sort_values('prefecture_code').reset_index(drop=True)

    print(f"\n[OK] 緑地率計算完了: {len(df_output)}都道府県")
    print(f"\n統計サマリー:")
    print(f"  緑地率平均: {df_output['greenspace_ratio_percent'].mean():.2f}%")
    print(f"  緑地率最小: {df_output['greenspace_ratio_percent'].min():.2f}% ({df_output.loc[df_output['greenspace_ratio_percent'].idxmin(), 'prefecture_name']})")
    print(f"  緑地率最大: {df_output['greenspace_ratio_percent'].max():.2f}% ({df_output.loc[df_output['greenspace_ratio_percent'].idxmax(), 'prefecture_name']})")

    # CSV保存
    output_path = OUTPUT_DIR / "greenspace_ratio.csv"
    df_output.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n[保存完了] {output_path}")

    # サンプル表示
    print(f"\n[サンプル] 先頭5行:")
    print(df_output.head(5).to_string(index=False))
    print(f"\n[サンプル] 末尾5行:")
    print(df_output.tail(5).to_string(index=False))

    return df_output

# ============================================================
# メイン実行
# ============================================================

if __name__ == "__main__":
    df_result = create_greenspace_ratio()
    print("\n" + "=" * 80)
    print(" 処理完了")
    print("=" * 80)
