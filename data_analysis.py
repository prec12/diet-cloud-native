"""
data_analysis.py
Task 1: Dataset Analysis and Insights for All_Diets.csv

What this script does:
1) Loads All_Diets.csv (local file path).
2) Cleans numeric columns (Protein/Carbs/Fat), handles missing values.
3) Computes:
   - Average macros by Diet_type
   - Top 5 protein recipes for each Diet_type
   - Diet_type with highest average protein
   - Most common cuisines per Diet_type
   - Protein-to-Carbs ratio and Carbs-to-Fat ratio per recipe
4) Creates visualizations:
   - Bar chart: average macros by diet
   - Heatmap: average macros by diet
   - Scatter: top protein recipes (colored by Cuisine_type)
5) Saves outputs to outputs/ folder (CSV + PNG charts).
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# -----------------------------
# Config
# -----------------------------
CSV_PATH = os.getenv("CSV_PATH", "data/All_Diets.csv")  # you can set CSV_PATH env var if needed

OUT_DIR = "outputs"
CHART_DIR = os.path.join(OUT_DIR, "charts")
RESULT_DIR = os.path.join(OUT_DIR, "results")

NUM_COLS = ["Protein(g)", "Carbs(g)", "Fat(g)"]
CAT_COLS = ["Diet_type", "Recipe_name", "Cuisine_type"]


# -----------------------------
# Helpers
# -----------------------------
def ensure_dirs() -> None:
    """Create output folders if they don't exist."""
    os.makedirs(CHART_DIR, exist_ok=True)
    os.makedirs(RESULT_DIR, exist_ok=True)


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """
    Divide while avoiding division-by-zero.
    Returns NaN where denominator is 0 or NaN.
    """
    denom = denominator.replace({0: np.nan})
    return numerator / denom


# -----------------------------
# Main processing
# -----------------------------
def main() -> None:
    ensure_dirs()

    # 1) Load dataset
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"Could not find CSV at '{CSV_PATH}'. Put All_Diets.csv there or set CSV_PATH env var."
        )

    df = pd.read_csv(CSV_PATH)

    # 2) Basic validation: ensure required columns exist
    required_cols = set(NUM_COLS + CAT_COLS)
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(list(missing))}")

    # 3) Clean numeric columns: coerce to numeric (handles weird strings)
    for col in NUM_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4) Handle missing numeric values by filling with mean of each column
    #    (mean is computed ignoring NaNs)
    means = df[NUM_COLS].mean(numeric_only=True)
    df[NUM_COLS] = df[NUM_COLS].fillna(means)

    # 5) Create new ratio metrics (safe division)
    df["Protein_to_Carbs_ratio"] = safe_divide(df["Protein(g)"], df["Carbs(g)"])
    df["Carbs_to_Fat_ratio"] = safe_divide(df["Carbs(g)"], df["Fat(g)"])

    # 6) Average macros per diet type
    avg_macros = df.groupby("Diet_type")[NUM_COLS].mean().sort_values(by="Protein(g)", ascending=False)
    avg_macros.to_csv(os.path.join(RESULT_DIR, "avg_macros_by_diet.csv"))

    # 7) Top 5 protein recipes per diet type
    #    Sort by protein descending first, then take head(5) per group.
    top_protein = (
        df.sort_values("Protein(g)", ascending=False)
          .groupby("Diet_type", as_index=False)
          .head(5)
          .loc[:, ["Diet_type", "Recipe_name", "Cuisine_type", "Protein(g)", "Carbs(g)", "Fat(g)"]]
    )
    top_protein.to_csv(os.path.join(RESULT_DIR, "top5_protein_recipes_by_diet.csv"), index=False)

    # 8) Diet type with highest average protein across all recipes
    highest_protein_diet = avg_macros["Protein(g)"].idxmax()
    highest_protein_value = float(avg_macros.loc[highest_protein_diet, "Protein(g)"])

    with open(os.path.join(RESULT_DIR, "highest_protein_diet.txt"), "w", encoding="utf-8") as f:
        f.write(f"Highest average protein diet: {highest_protein_diet} ({highest_protein_value:.2f} g)\n")

    # 9) Most common cuisines per diet type
    #    For each Diet_type, find top cuisine by count.
    cuisine_counts = (
        df.groupby(["Diet_type", "Cuisine_type"])
          .size()
          .reset_index(name="Count")
          .sort_values(["Diet_type", "Count"], ascending=[True, False])
    )
    most_common_cuisines = cuisine_counts.groupby("Diet_type", as_index=False).head(1)
    most_common_cuisines.to_csv(os.path.join(RESULT_DIR, "most_common_cuisine_by_diet.csv"), index=False)

    # -----------------------------
    # Visualizations
    # -----------------------------

    # A) Bar chart: average macros by diet
    #    Reshape for seaborn grouped bar chart
    avg_long = avg_macros.reset_index().melt(
        id_vars="Diet_type", value_vars=NUM_COLS, var_name="Macronutrient", value_name="Average(g)"
    )

    plt.figure()
    sns.barplot(data=avg_long, x="Diet_type", y="Average(g)", hue="Macronutrient")
    plt.title("Average Macronutrients by Diet Type")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "avg_macros_bar.png"), dpi=200)
    plt.close()

    # B) Heatmap: average macros by diet
    plt.figure()
    sns.heatmap(avg_macros, annot=False)
    plt.title("Heatmap: Average Macronutrients by Diet Type")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "avg_macros_heatmap.png"), dpi=200)
    plt.close()

    # C) Scatter plot: top protein recipes across diets (top 5 per diet)
    #    Show Protein vs Carbs, hue by Cuisine_type (can be many cuisines; still acceptable)
    plt.figure()
    sns.scatterplot(
        data=top_protein,
        x="Carbs(g)",
        y="Protein(g)",
        hue="Cuisine_type",
        style="Diet_type",
    )
    plt.title("Top Protein Recipes (Top 5 per Diet): Protein vs Carbs")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "top_protein_scatter.png"), dpi=200)
    plt.close()

    # Console summary (useful for screenshots)
    print("=== Task 1 Summary ===")
    print(f"Rows: {len(df)}")
    print("Saved results to:", RESULT_DIR)
    print("Saved charts to:", CHART_DIR)
    print(f"Highest average protein diet: {highest_protein_diet} ({highest_protein_value:.2f} g)")
    print("\nMost common cuisine per diet (sample):")
    print(most_common_cuisines.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
