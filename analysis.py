# Detailní analýza datového souboru shots_outcome_Final.csv
# Zaměření na vizualizace: kde se střílí, co branky předpovídá, kdo překonává xG

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch

sns.set_theme(style="whitegrid")
FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)


def save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"saved: {path}")
    plt.show()


# ----------------------------------------------------------------------
# 0. Načtení a čištění dat
# ----------------------------------------------------------------------
df = pd.read_csv("shots_outcome_Final.csv")

# Odlehlé / nesmyslné hodnoty:
#  - OwnGoal není pokus dát branku, xG = 0 -> ze střelecké analýzy vyřadíme
#  - minuta > 90+ (prodloužení) necháme, jen očíslujeme
shots = df[df["result"] != "OwnGoal"].copy()

# Převod souřadnic na rozměry hřiště 100 x 100 (dle README)
shots["X"] = shots["X"] * 100
shots["Y"] = shots["Y"] * 100

# Binární příznak gólu
shots["is_goal"] = (shots["result"] == "Goal").astype(int)

# Minuta v rozmezí 0-90 + nastavení
shots["min_bin"] = pd.cut(
    shots["minute"], bins=[0, 15, 30, 45, 60, 75, 90, 100],
    labels=["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "90+"],
    include_lowest=True,
)

print(f"Počet záznamů: {len(df)} (po odebrání vlastních branek: {len(shots)})")
print(f"Konverze: {shots['is_goal'].mean():.1%} | průměrné xG: {shots['xG'].mean():.3f}")

# ----------------------------------------------------------------------
# 1. Kvalita dat – chybějící hodnoty
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
missing = df.isna().sum().sort_values(ascending=False)
missing = missing[missing > 0]
bars = ax.barh(missing.index, missing.values, color=sns.color_palette("crest", len(missing)))
ax.set_xlabel("Počet chybějících hodnot")
ax.set_title("Chybějící hodnoty podle sloupců")
ax.invert_yaxis()
for b, v in zip(bars, missing.values):
    ax.text(v + 3, b.get_y() + b.get_height() / 2, f"{v} ({v/len(df):.0%})", va="center")
save(fig, "01_missing_values.png")

# ----------------------------------------------------------------------
# 2. Distribuce výsledků střel
# ----------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
order = shots["result"].value_counts().index
sns.countplot(data=shots, y="result", order=order, ax=axes[0], palette="crest")
axes[0].set_title("Výsledky střel (počet)")
axes[0].set_xlabel("")
for i, v in enumerate(shots["result"].value_counts()):
    axes[0].text(v + 3, i, str(v), va="center")

result_share = shots["result"].value_counts(normalize=True)
axes[1].pie(result_share, labels=result_share.index, autopct="%1.1f%%",
            colors=sns.color_palette("crest", len(result_share)))
axes[1].set_title("Výsledky střel (podíl)")
save(fig, "02_result_distribution.png")

# ----------------------------------------------------------------------
# 3. Mapa střel na hřišti – odkud se střílí
# ----------------------------------------------------------------------
pitch = Pitch(pitch_type="custom", pitch_length=100, pitch_width=100,
              pitch_color="#22312b", line_color="#c7d5cc")
fig, axes = pitch.draw(figsize=(12, 10), nrows=2, ncols=1)

# 3a. KDE – hustota všech střel (jen záznamy se souřadnicemi)
spatial = shots.dropna(subset=["X", "Y"])
pitch.kdeplot(spatial["X"], spatial["Y"], ax=axes[0], cmap="hot", fill=True,
              levels=10, thresh=0.05, alpha=0.7)
axes[0].set_title("Hustota střel (KDE)", color="white", fontsize=14)

# 3b. Góly vs. ostatní střely
goals = spatial[spatial["is_goal"] == 1]
pitch.scatter(spatial["X"], spatial["Y"], ax=axes[1], s=12, alpha=0.25,
              color="#c7d5cc", label="Střela")
pitch.scatter(goals["X"], goals["Y"], ax=axes[1], s=60,
              color="#f24f4f", edgecolors="white", label="Gól")
axes[1].set_title("Góly vs. ostatní střely", color="white", fontsize=14)
axes[1].legend(loc="upper left", facecolor="#22312b", labelcolor="white")
save(fig, "03_shot_map.png")

# ----------------------------------------------------------------------
# 4. xG podle výsledku střely
# ----------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.boxplot(data=shots, x="result", y="xG", order=order, ax=axes[0], palette="crest")
axes[0].set_title("xG podle výsledku střely")
axes[0].tick_params(axis="x", rotation=30)

sns.kdeplot(data=shots[shots["result"].isin(["Goal", "MissedShots", "SavedShot"])],
            x="xG", hue="result", fill=True, common_norm=False, ax=axes[1],
            palette="crest")
axes[1].set_title("Rozdělení xG: gól vs. neproměněná střela")
save(fig, "04_xg_by_result.png")

# ----------------------------------------------------------------------
# 5. Konverze podle situace, typu střely a poslední akce
# ----------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(17, 5))
for ax, col, title in [
    (axes[0], "situation", "Podle situace"),
    (axes[1], "shotType", "Podle části těla"),
    (axes[2], "h_a", "Doma vs. venku"),
]:
    grp = shots.groupby(col).agg(
        shots=("is_goal", "size"),
        goals=("is_goal", "sum"),
        conv=("is_goal", "mean"),
        xg=("xG", "mean"),
    ).sort_values("conv", ascending=False)
    x = np.arange(len(grp))
    ax.bar(x - 0.2, grp["conv"], width=0.4, label="Skutečná konverze", color="#2a9d8f")
    ax.bar(x + 0.2, grp["xg"], width=0.4, label="Průměrné xG", color="#e9c46a")
    ax.set_xticks(x)
    ax.set_xticklabels(grp.index, rotation=30, ha="right")
    ax.set_ylabel("Podíl gólů / xG")
    ax.set_title(f"Konverze vs. xG – {title}")
    for i, (c, s) in enumerate(zip(grp["conv"], grp["shots"])):
        ax.text(i - 0.2, c + 0.005, f"{c:.0%}", ha="center", fontsize=9)
        ax.text(i, -0.07, f"n={s}", ha="center", fontsize=8, color="gray")
    ax.legend()
save(fig, "05_conversion_by_context.png")

# ----------------------------------------------------------------------
# 6. Hráči: objem střel, góly vs. xG (překonávání očekávání)
# ----------------------------------------------------------------------
players = shots.groupby("player").agg(
    shots=("is_goal", "size"),
    goals=("is_goal", "sum"),
    xg=("xG", "sum"),
).sort_values("shots", ascending=False)
players["diff"] = players["goals"] - players["xg"]  # góly nad očekáváním

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
players[["shots", "goals"]].plot(kind="barh", ax=axes[0], color=["#adb5bd", "#2a9d8f"])
axes[0].set_title("Objem střel a gólů podle hráče")
axes[0].set_xlabel("Počet")

colors = ["#2a9d8f" if d >= 0 else "#e76f51" for d in players["diff"]]
axes[1].barh(players.index, players["diff"], color=colors)
axes[1].axvline(0, color="black", linewidth=1)
axes[1].set_title("Góly minus xG (kdo překonává očekávání)")
axes[1].set_xlabel("Góly − xG")
for i, v in enumerate(players["diff"]):
    axes[1].text(v + (0.15 if v >= 0 else -0.15), i, f"{v:+.1f}",
                 va="center", ha="left" if v >= 0 else "right", fontsize=9)
axes[1].invert_yaxis()
save(fig, "06_players.png")

# ----------------------------------------------------------------------
# 7. Vývoj v čase – minuta zápasu a sezóna
# ----------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
by_min = shots.groupby("min_bin", observed=True).agg(
    shots=("is_goal", "size"), conv=("is_goal", "mean"))
axes[0].bar(by_min.index.astype(str), by_min["shots"], color="#adb5bd", label="Střely")
ax2 = axes[0].twinx()
ax2.plot(by_min.index.astype(str), by_min["conv"], color="#e63946", marker="o", label="Konverze")
ax2.set_ylabel("Konverze", color="#e63946")
axes[0].set_ylabel("Počet střel")
axes[0].set_title("Střely a konverze podle minuty zápasu")
axes[0].tick_params(axis="x", rotation=30)

by_year = shots.groupby("year").agg(shots=("is_goal", "size"), goals=("is_goal", "sum"), xg=("xG", "sum"))
axes[1].plot(by_year.index, by_year["shots"], marker="o", label="Střely", color="#457b9d")
axes[1].plot(by_year.index, by_year["goals"], marker="o", label="Góly", color="#2a9d8f")
axes[1].plot(by_year.index, by_year["xg"], marker="o", label="Součet xG", color="#e9c46a")
axes[1].set_title("Vývoj podle sezóny")
axes[1].set_xticks(by_year.index)
axes[1].legend()
save(fig, "07_time_trends.png")

# ----------------------------------------------------------------------
# 8. Poslední akce před střelou – konverze
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6))
grp = (shots.groupby("lastAction")["is_goal"]
       .agg(["size", "mean"]).sort_values("size", ascending=False))
grp = grp[grp["size"] >= 15]  # jen dostatečně zastoupené akce
norm = plt.Normalize(grp["mean"].min(), grp["mean"].max())
colors = plt.cm.RdYlGn(norm(grp["mean"]))
ax.bar(grp.index, grp["mean"], color=colors)
ax.set_title("Konverze podle poslední akce před střelou (n ≥ 15)")
ax.set_ylabel("Konverze")
ax.tick_params(axis="x", rotation=45)
for i, (c, n) in enumerate(zip(grp["mean"], grp["size"])):
    ax.text(i, c + 0.005, f"{c:.0%} (n={n})", ha="center", fontsize=8)
save(fig, "08_last_action.png")

# ----------------------------------------------------------------------
# 9. Korelace numerických příznaků
# ----------------------------------------------------------------------
num = shots[["minute", "X", "Y", "xG", "is_goal", "h_goals", "a_goals", "year"]].dropna()
fig, ax = plt.subplots(figsize=(8, 7))
sns.heatmap(num.corr(), annot=True, fmt=".2f", cmap="coolwarm",
            vmin=-1, vmax=1, square=True, ax=ax)
ax.set_title("Korelační matice numerických příznaků")
save(fig, "09_correlation.png")

# ----------------------------------------------------------------------
# 10. Interaktivní souhrn – statistiky
# ----------------------------------------------------------------------
print("\n=== Souhrn ===")
print(f"Celková konverze: {shots['is_goal'].mean():.1%}")
print(f"Součet xG: {shots['xG'].sum():.1f} vs. gólů: {shots['is_goal'].sum()}")
print("\nNejlepší střelci podle gólů nad xG:")
print(players[["shots", "goals", "xg", "diff"]].sort_values("diff", ascending=False).head(5))
print("\nKonverze podle situace:")
print(shots.groupby("situation")["is_goal"].agg(["size", "mean"]).sort_values("mean", ascending=False))
