import pandas as pd
from data_loader import load_mock_data
from calculator import calculate_metrics
from recommender import generate_recommendations
from visualizer import (
    total_cost_vs_emissions,
    service_wise_distribution,
    region_wise_comparison,
    stacked_service_contribution,
    display_all_plots,
    save_all_to_pdf,
    save_selected_plots,
    export_data_to_csv,
    generated_figures
)
from report_generator_reportlab import generate_pdf_report

# ---------------- LOAD & CALCULATE ----------------
print("\n Loading and calculating AWS cost & carbon data...")
df = load_mock_data()
metrics = calculate_metrics(df)  # <-- Pulls processed results from calculator.py

# ---------------- PLOT SELECTION ----------------
plot_options = {
    "1": ("Total Cost vs Emissions", total_cost_vs_emissions),
    "2": ("Service-wise Cost Distribution", lambda df: service_wise_distribution(df, "cost_usd")),
    "3": ("Service-wise Emission Distribution", lambda df: service_wise_distribution(df, "emission_kg")),
    "4": ("Region-wise Cost & Emissions Comparison", region_wise_comparison),
    "5": ("Stacked Cost per Region", lambda df: stacked_service_contribution(df, "cost_usd")),
    "6": ("Stacked Emissions per Region", lambda df: stacked_service_contribution(df, "emission_kg")),
}

print("\n Choose plots to generate (comma separated):")
for k, (name, _) in plot_options.items():
    print(f"  {k}. {name}")

choices = input("\nEnter plot numbers (e.g., 1,2,4): ").split(',')

for choice in choices:
    choice = choice.strip()
    if choice in plot_options:
        plot_options[choice][1](df)

# ---------------- DISPLAY PLOTS ----------------
print("\nDisplaying selected plots...")
display_all_plots()

# ---------------- SAVE PLOTS ----------------
save_choice = input("\n Do you want to save these plots? (yes/no): ").strip().lower()
if save_choice == "yes":
    format_choice = input("\nSave as PNG or PDF? ").strip().lower()
    if format_choice == "pdf":
        save_all_to_pdf()
    else:
        print("\nGenerated Plot Files:")
        for _, fname in generated_figures:
            print(f"  - {fname}")
        which_files = input("\nEnter filenames to save (comma separated) or type 'all': ").strip().lower()
        selected_files = [f.strip() for f in which_files.split(",")] if which_files != "all" else ["all"]
        save_selected_plots(selected_files, filetype="png")

# ---------------- EXPORT DATA ----------------
csv_choice = input("\n📤 Do you want to export the plot data to CSV? (yes/no): ").strip().lower()
if csv_choice == "yes":
    filename = input("Enter CSV filename (e.g., result.csv): ").strip()
    export_data_to_csv(df, filename)

# ---------------- GENERATE RECOMMENDATIONS ----------------
print("\n🤖 Generating cost & carbon optimization recommendations...")
recommendations = generate_recommendations(df)

print("\n=== Recommendations ===")
for rec in recommendations:
    print(f"- {rec}")

# Optionally export recommendations
rec_choice = input("\n📄 Do you want to save recommendations to CSV? (yes/no): ").strip().lower()
if rec_choice == "yes":
    rec_df = pd.DataFrame({"Recommendation": recommendations})
    rec_filename = input("Enter CSV filename (e.g., recommendations.csv): ").strip()
    rec_df.to_csv(rec_filename, index=False)
    print(f"✅ Recommendations saved to {rec_filename}")

summary = (
    "This report aggregates total cost and emissions by service and region, "
    "highlights carbon efficiency, and lists optimization opportunities."
)

outputs = generate_pdf_report(
    metrics=metrics,
    #generated_figures=generated_figures,   # from visualizer
    #recommendations=recommendations,       # from recommender
    organization="Your Org",
    report_title="Cloud Cost & Carbon Report",
    summary_text=summary,
    output_dir="reports",
    base_filename="run_report",
)
print("\nReport paths:", outputs)

print("\n✅ Dashboard run complete.")
