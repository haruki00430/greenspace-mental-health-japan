# -*- coding: utf-8 -*-
"""NDBファイル構造確認スクリプト"""

import pandas as pd
from pathlib import Path

# NDBファイルパス
ndb_file = Path(r"C:\Users\user\SharedWorkspace\projects\NDB_Research_Hub\02_Data\raw\NDB_OpenData\No.10\05_処方薬\01_公費レセプトを含まないデータ\01_処方薬（内服／外用／注射）\【内服】外来（院外）_都道府県別薬効分類別数量.xlsx")

print("=" * 60)
print("NDBファイル構造確認")
print("=" * 60)

# ヘッダーなしで先頭10行を読み込み
print("\n[INFO] ヘッダーなしで先頭10行を読み込み")
df_raw = pd.read_excel(ndb_file, header=None, nrows=10)

print(f"形状: {df_raw.shape}")
print(f"\n先頭10行×10列:")
print(df_raw.iloc[:10, :10].to_string())

# header=2で読み込み
print("\n\n[INFO] header=2で読み込み（現在の方法）")
df_h2 = pd.read_excel(ndb_file, header=2, nrows=10)
print(f"形状: {df_h2.shape}")
print(f"\nカラム名（最初の10列）:")
for i, col in enumerate(df_h2.columns[:10]):
    print(f"  [{i}] {col}")

# header=[2,3]で読み込み（MultiIndex）
print("\n\n[INFO] header=[2,3]で読み込み（MultiIndex）")
df_h23 = pd.read_excel(ndb_file, header=[2, 3], nrows=10)
print(f"形状: {df_h23.shape}")
print(f"\nカラム名（最初の10列）:")
for i, col in enumerate(df_h23.columns[:10]):
    print(f"  [{i}] {col}")

# カラム名に都道府県が含まれるか確認
print("\n\n[INFO] '北海道'を含む列の検索")
hokkaido_cols = [col for col in df_h23.columns if '北海道' in str(col)]
print(f"検出数: {len(hokkaido_cols)}")
if hokkaido_cols:
    print(f"サンプル: {hokkaido_cols[:3]}")
