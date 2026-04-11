"""
Figure creation script for greenspace-mental health manuscript
Creates three maps:
1. Choropleth map of greenspace ratio
2. Choropleth map of psychiatric prescription rate
3. LISA map of prescription rate
"""

import geopandas as gpd
import matplotlib.pyplot as plt
from libpysal.weights import Queen
from esda.moran import Moran_Local
import sys
import os

# Add ndb_library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'src'))
from ndb_library.viz import set_japanese_font

# Set Japanese font
set_japanese_font()

# Paths
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'spatial_analysis_data.geojson')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'results', 'figures')

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading spatial data...")
gdf = gpd.read_file(DATA_PATH)

print(f"Loaded {len(gdf)} prefectures")
print(f"Columns: {list(gdf.columns)}")

# Check if required columns exist
required_cols = ['prefecture_name', 'greenspace_ratio_percent', 'prescription_per_100k']
missing_cols = [col for col in required_cols if col not in gdf.columns]
if missing_cols:
    print(f"ERROR: Missing columns: {missing_cols}")
    print(f"Available columns: {list(gdf.columns)}")
    sys.exit(1)

# ============================================
# Figure 1: Choropleth map of greenspace ratio
# ============================================
print("\nCreating Figure 1: Greenspace ratio choropleth...")

fig, ax = plt.subplots(1, 1, figsize=(10, 8))

gdf.plot(
    column='greenspace_ratio_percent',
    cmap='Greens',
    legend=True,
    ax=ax,
    edgecolor='black',
    linewidth=0.5,
    legend_kwds={'label': '緑地率 (%)', 'orientation': 'horizontal', 'shrink': 0.8}
)

ax.set_title('都道府県別緑地率', fontsize=16, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'choropleth_greenspace.png'), dpi=300, bbox_inches='tight')
print(f"[OK] Saved: {os.path.join(OUTPUT_DIR, 'choropleth_greenspace.png')}")
plt.close()

# ============================================
# Figure 2: Choropleth map of prescription rate
# ============================================
print("\nCreating Figure 2: Prescription rate choropleth...")

fig, ax = plt.subplots(1, 1, figsize=(10, 8))

gdf.plot(
    column='prescription_per_100k',
    cmap='Reds',
    legend=True,
    ax=ax,
    edgecolor='black',
    linewidth=0.5,
    legend_kwds={'label': '精神科薬処方量（人口10万人あたり）', 'orientation': 'horizontal', 'shrink': 0.8}
)

ax.set_title('都道府県別精神科薬処方量（人口10万人あたり）', fontsize=16, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'choropleth_prescription.png'), dpi=300, bbox_inches='tight')
print(f"[OK] Saved: {os.path.join(OUTPUT_DIR, 'choropleth_prescription.png')}")
plt.close()

# ============================================
# Figure 3: LISA map of prescription rate
# ============================================
print("\nCreating Figure 3: LISA map...")

# Create spatial weights matrix
print("  Building Queen contiguity matrix...")
w = Queen.from_dataframe(gdf)

# Calculate Local Moran's I
print("  Calculating Local Moran's I...")
lisa = Moran_Local(gdf['prescription_per_100k'].values, w, permutations=999)

# Classify into quadrants
# 1 = High-High, 2 = Low-Low, 3 = Low-High, 4 = High-Low, 0 = Not significant
sig = lisa.p_sim < 0.05
hotspot = sig * lisa.q

# Create labels
labels = {
    0: '有意差なし',
    1: 'High-High (ホットスポット)',
    2: 'Low-Low (コールドスポット)',
    3: 'Low-High (外れ値)',
    4: 'High-Low (外れ値)'
}

# Map colors
colors = {
    0: '#e0e0e0',  # Gray (not significant)
    1: '#d7191c',  # Red (High-High)
    2: '#2b83ba',  # Blue (Low-Low)
    3: '#abdda4',  # Light green (Low-High)
    4: '#fdae61'   # Orange (High-Low)
}

# Create color map
gdf['lisa_category'] = hotspot

fig, ax = plt.subplots(1, 1, figsize=(10, 8))

for category in [0, 1, 2, 3, 4]:
    subset = gdf[gdf['lisa_category'] == category]
    if len(subset) > 0:
        subset.plot(
            ax=ax,
            color=colors[category],
            edgecolor='black',
            linewidth=0.5,
            label=labels[category]
        )

ax.set_title('LISA Map: 精神科薬処方量の空間的集積パターン', fontsize=16, fontweight='bold', pad=20)
ax.axis('off')
ax.legend(loc='lower left', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'lisa_map_prescription.png'), dpi=300, bbox_inches='tight')
print(f"[OK] Saved: {os.path.join(OUTPUT_DIR, 'lisa_map_prescription.png')}")
plt.close()

print("\n" + "="*50)
print("All figures created successfully!")
print("="*50)

# Summary statistics
print("\n=== Summary Statistics ===")
print(f"Greenspace ratio: Mean={gdf['greenspace_ratio_percent'].mean():.2f}%, SD={gdf['greenspace_ratio_percent'].std():.2f}%")
print(f"Prescription rate: Mean={gdf['prescription_per_100k'].mean():.0f}, SD={gdf['prescription_per_100k'].std():.0f}")
print(f"\nLISA categories:")
for cat in [0, 1, 2, 3, 4]:
    count = (hotspot == cat).sum()
    print(f"  {labels[cat]}: {count} prefectures")
