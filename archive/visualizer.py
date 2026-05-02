import os
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch

# Ensure consistent theme
sns.set(style="whitegrid")

# Output directory for saved plots
OUTPUT_DIR = "output/plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List to hold (fig, filename) for all generated plots
generated_figures = []

# ------------ Helper Functions ------------

def display_all_plots():
    """Display all figures collected."""
    for fig, _ in generated_figures:
        fig.show()


def save_all_to_pdf(pdf_filename="all_plots.pdf"):
    """Save all collected figures to a multi-page PDF."""
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
    with PdfPages(pdf_path) as pdf:
        for fig, _ in generated_figures:
            pdf.savefig(fig)
    print(f"\n✅ All plots saved as PDF: {pdf_path}")


def save_selected_plots(selected_filenames: list[str], filetype="png"):
    """Save selected plots from the generated_figures list."""
    for fig, fname in generated_figures:
        if fname in selected_filenames or "all" in selected_filenames:
            path = os.path.join(OUTPUT_DIR, fname.replace(".png", f".{filetype}"))
            fig.savefig(path, bbox_inches="tight")
            print(f"✅ Saved: {path}")


def export_data_to_csv(df: pd.DataFrame, filename: str):
    """Export given dataframe to CSV in output directory."""
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    print(f"✅ Data exported to CSV: {path}")

# ------------ Plot Functions ------------

def total_cost_vs_emissions(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(["Cost (USD)", "Emissions (kgCO2)"],
           [df["cost_usd"].sum(), df["emission_kg"].sum()],
           color=["skyblue", "salmon"])
    ax.set_title("Total Cost vs Total Emissions")
    ax.set_ylabel("Amount (USD / kgCO2)")

    filename = "total_cost_vs_emissions.png"
    generated_figures.append((fig, filename))
    return fig

def service_wise_distribution(df: pd.DataFrame, metric="cost_usd"):
    data = df.groupby("service")[metric].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(data, labels=data.index, autopct="%1.1f%%", startangle=140)
    ax.set_title(f"{metric.replace('_', ' ').title()} Distribution by Service")

    filename = f"service_wise_{metric}_distribution.png"
    generated_figures.append((fig, filename))
    return fig

def region_wise_comparison(df: pd.DataFrame):
    region_data = df.groupby("region")[["cost_usd", "emission_kg"]].sum().reset_index()
    melted = region_data.melt(id_vars="region", var_name="Metric", value_name="Value")

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(data=melted, x="region", y="Value", hue="Metric", ax=ax)

    ax.set_title("Region-wise Cost & Emissions Comparison")
    ax.set_ylabel("Amount (USD / kgCO2)")
    ax.set_xlabel("Region")
    ax.legend(handles=[
        Patch(facecolor='skyblue', label='Cost (USD)'),
        Patch(facecolor='salmon', label='Emissions (kgCO2)')
    ], title="Metric", bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    fig.tight_layout()
    filename = "region_wise_comparison.png"
    generated_figures.append((fig, filename))
    return fig

def stacked_service_contribution(df: pd.DataFrame, metric="cost_usd"):
    pivot = df.pivot_table(values=metric, index="region", columns="service", aggfunc="sum", fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    pivot.plot(kind='bar', stacked=True, ax=ax)

    ax.set_title(f"Stacked {metric.replace('_', ' ').title()} per Region")
    ax.set_ylabel(f"{metric.replace('_', ' ').title()} (USD / kgCO2)")
    ax.set_xlabel("Region")
    ax.legend(title="Service", bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.)

    fig.tight_layout()
    filename = f"stacked_{metric}_per_region.png"
    generated_figures.append((fig, filename))
    return fig
