import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import Pitch
from scipy.stats import zscore

# 1. Load the CSV file
file_path = "shots_outcome_Final.csv"
df = pd.read_csv(file_path)

# 2. Clean missing (NaN) values from X and Y columns
df_clean = df.dropna(subset=["X", "Y"]).copy()

# 3. Scale coordinates to StatsBomb pitch dimensions (120 x 80)
x_max = df_clean["X"].max()
y_max = df_clean["Y"].max()

if x_max <= 1.0 and y_max <= 1.0:
    df_clean["X_scaled"] = df_clean["X"] * 120
    df_clean["Y_scaled"] = df_clean["Y"] * 80
elif x_max <= 100 and y_max <= 100:
    df_clean["X_scaled"] = (df_clean["X"] / 100) * 120
    df_clean["Y_scaled"] = (df_clean["Y"] / 100) * 80
else:
    df_clean["X_scaled"] = df_clean["X"]
    df_clean["Y_scaled"] = df_clean["Y"]

# 4. Identify Outliers using Z-score on spatial coordinates
# Points with a Z-score > 2.5 away from the mean location are flagged as outliers
df_clean["x_zscore"] = zscore(df_clean["X_scaled"])
df_clean["y_zscore"] = zscore(df_clean["Y_scaled"])

# Distance from average spatial location in standard deviation units
df_clean["spatial_distance_z"] = np.sqrt(
    df_clean["x_zscore"] ** 2 + df_clean["y_zscore"] ** 2
)

# Set threshold (e.g., top ~5% furthest points relative to cluster density)
threshold = 2.2
outliers = df_clean[df_clean["spatial_distance_z"] > threshold]
inliers = df_clean[df_clean["spatial_distance_z"] <= threshold]

print(f"Total points: {len(df_clean)}")
print(f"Outliers detected: {len(outliers)}")

# 5. Set up the Pitch
pitch = Pitch(
    pitch_type="statsbomb",
    pitch_color="#22312b",
    line_color="#c7d5cc",
    line_zorder=2,
)

fig, ax = pitch.draw(figsize=(10, 7))

# 6. Plot Heatmap for standard shots (Inliers)
if len(inliers) > 10:
    pitch.kdeplot(
        inliers["X_scaled"],
        inliers["Y_scaled"],
        ax=ax,
        cmap="hot",
        fill=True,
        levels=10,
        bw_adjust=1.2,
        thresh=0.05,
        alpha=0.7,
        zorder=1,
    )

# 7. Scatter plot for Outliers
pitch.scatter(
    outliers["X_scaled"],
    outliers["Y_scaled"],
    ax=ax,
    color="#00ffff",  # Cyan color to stand out against 'hot' colormap
    edgecolors="black",
    s=70,
    marker="X",
    label="Outlier Shots",
    zorder=3,
)

plt.title("Shots Heatmap with Spatial Outliers Highlighted", color="white", fontsize=16, pad=12)
plt.legend(loc="upper left", facecolor="#22312b", edgecolor="white", labelcolor="white")

plt.tight_layout()
plt.show()