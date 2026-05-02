"""
2nd Module - Exporter

Objective:
Export processed insights and metrics into user-friendly formats.

How it helps:
Makes the insights portable for reporting, sharing, or analysis in external tools.

Key Features:
- Export dataframes as CSV/Excel.
- Export metrics as JSON (for APIs or integration).
- Export plots (when integrated) as PNG/PDF.
- User-selectable export format and location.
"""

import os
import json
import pandas as pd
from legacy.calculator import calculate_metrics

def ensure_export_folder(export_folder: str):
    """Create the export folder if it doesn't exist."""
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
        print(f"\U0001F4C1 Created export folder: {export_folder}")

def export_dataframe(df: pd.DataFrame, file_path_base: str):
    """Export a DataFrame to both CSV and Excel."""
    csv_path = file_path_base + ".csv"
    excel_path = file_path_base + ".xlsx"
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)
    print(f"✅ Exported → {csv_path}")
    print(f"✅ Exported → {excel_path}")

def export_dict_as_json(data: dict, file_path: str):
    """Export a dictionary as a JSON file."""
    with open(file_path + ".json", 'w') as f:
        json.dump(data, f, indent=4)
    print(f"✅ Exported JSON → {file_path}.json")
 
def export_results(results: dict, export_folder: str = "exports"):
    """
    Export calculated metrics to CSV, Excel, and JSON files.

    Parameters:
    - results (dict): Dictionary of DataFrames or dicts.
    - export_folder (str): Where to save the exported files.
    """
    ensure_export_folder(export_folder)

    for key, value in results.items():
        file_path_base = os.path.join(export_folder, key)

        if isinstance(value, pd.DataFrame):
            export_dataframe(value, file_path_base)

        elif isinstance(value, dict):
            export_dict_as_json(value, file_path_base)

        else:
            print(f"⚠️ Skipping {key}: Unsupported data type → {type(value)}")

if __name__ == "__main__":
    # Load mock data (temporary until real-time integration)
    df = pd.read_csv("mock_data/aws_billing_mock.csv")

    # Calculate metrics
    results = calculate_metrics(df)

    # Export all metrics
    export_results(results)
