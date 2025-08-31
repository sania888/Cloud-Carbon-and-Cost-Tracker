"""3rd module
Objective:
Generate structured, readable, and downloadable reports summarizing the entire analysis.

How it helps:
Creates organization-ready reports with visualizations, summaries, and recommendations for FinOps and sustainability teams.

Key Features:

PDF report generation (with charts, tables, summaries).

Option to include recommendations and trends.

Sectioned format (Overview, Emissions, Cost, Services, etc.).

Auto-generated titles, dates, and organization branding.
"""

from __future__ import annotations
import os 
import io
import base64 
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Optional PDF dependency — we gracefully degrade if missing.
try:
    from weasyprint import HTML
    _WEASY_AVAILABLE = True
except Exception:
    _WEASY_AVAILABLE = False

# ------------------------------
# HTML BUILDERS
# ------------------------------

def _img_file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _fig_to_png_b64(fig) -> str:
    """Fallback: render a Matplotlib figure in-memory and return base64 PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def dataframes_to_html_tables(metrics: Dict[str, Any]) -> Dict[str, str]:
    """Convert DataFrames in the metrics dict to styled HTML tables."""
    tables = {}
    for key, val in metrics.items():
        if isinstance(val, pd.DataFrame):
            tables[key] = (
                val.to_html(index=False, classes="table",
                            border=0, justify="center")
            )
        else:
            # For non-DF entries (e.g., dicts like top_emitters), show JSON pretty
            tables[key] = (
                f"<pre class='pre-json'>{json.dumps(val, indent=2)}</pre>"
            )
    return tables


def collect_plot_images(
    generated_figures: List[Tuple[object, str]],
    plot_dir: str = "output/plots",
    tmp_assets_dir: str = "reports/assets",
) -> List[Dict[str, str]]:
    """
    Build a list of images {title, image_base64} from visualizer.generated_figures.
    If a file already exists in plot_dir, embed that; otherwise render figure to a
    temp assets directory and embed.
    """
    _ensure_dir(tmp_assets_dir)

    images = []
    for fig, filename in generated_figures:
        title = os.path.splitext(filename.replace("_", " "))[0].title()
        existing_path = os.path.join(plot_dir, filename)

        if os.path.exists(existing_path):
            img_b64 = _img_file_to_base64(existing_path)
        else:
            # Save to temp assets
            tmp_path = os.path.join(tmp_assets_dir, filename)
            fig.savefig(tmp_path, format="png", bbox_inches="tight")
            img_b64 = _img_file_to_base64(tmp_path)

        images.append({
            "title": title,
            "image_base64": img_b64,
        })
    return images


def build_report_html(
    organization: str,
    report_title: str,
    summary_text: str,
    metrics_tables: Dict[str, str],
    images: List[Dict[str, str]],
    recommendations: List[str] | None = None,
) -> str:
    """Compose a self-contained HTML report string with inline CSS + images."""
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Simple inline CSS (self-contained)
    css = """
    <style>
      body { font-family: Arial, Helvetica, sans-serif; margin: 24px; color: #0f172a; }
      .header { display:flex; justify-content: space-between; align-items: center; }
      .brand { font-size: 22px; font-weight: 700; }
      .title { font-size: 26px; margin-top: 8px; }
      .subtle { color: #475569; font-size: 14px; }
      .section { margin-top: 28px; }
      h2 { font-size: 20px; margin-bottom: 8px; }
      p { line-height: 1.5; }
      .grid { display: grid; grid-template-columns: 1fr; gap: 16px; }
      .card { border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; background: #ffffff; }
      .table { width: 100%; border-collapse: collapse; }
      .table th, .table td { border: 1px solid #e2e8f0; padding: 8px; text-align: center; }
      .table th { background: #f8fafc; }
      .img { width: 100%; max-width: 720px; display:block; margin: 8px auto; }
      .caption { text-align:center; font-size: 14px; color:#64748b; margin-bottom: 8px;}
      .pre-json { background:#0b1220; color:#e2e8f0; padding:12px; border-radius:10px; overflow:auto; }
      .badge { background:#eef2ff; color:#3730a3; padding:2px 8px; border-radius:9999px; font-size:12px; }
      .footnote { margin-top: 24px; font-size: 12px; color: #64748b; }
    </style>
    """

    # Build sections
    parts = []
    parts.append(f"""
      <div class='header'>
        <div>
          <div class='brand'>{organization}</div>
          <div class='title'>{report_title}</div>
          <div class='subtle'>Generated: {today}</div>
        </div>
        <div class='badge'>Cloud Carbon Cost Tracker</div>
      </div>
    """)

    parts.append(f"""
      <div class='section'>
        <h2>Executive Summary</h2>
        <div class='card'><p>{summary_text}</p></div>
      </div>
    """)

    # Metrics / Tables
    parts.append("<div class='section'><h2>Key Metrics & Tables</h2><div class='grid'>")
    for name, html_table in metrics_tables.items():
        section_title = name.replace("_", " ").title()
        parts.append(f"<div class='card'><h3>{section_title}</h3>{html_table}</div>")
    parts.append("</div></div>")

    # Visuals
    if images:
        parts.append("<div class='section'><h2>Visualizations</h2><div class='grid'>")
        for img in images:
            parts.append(
                f"<div class='card'>"
                f"  <div class='caption'>{img['title']}</div>"
                f"  <img class='img' src='data:image/png;base64,{img['image_base64']}' alt='{img['title']}' />"
                f"</div>"
            )
        parts.append("</div></div>")

    # Recommendations
    if recommendations:
        parts.append("<div class='section'><h2>Optimization Recommendations</h2>")
        parts.append("<div class='card'><ul>")
        for rec in recommendations:
            parts.append(f"<li>{rec}</li>")
        parts.append("</ul></div></div>")

    parts.append("""
      <div class='footnote'>
        This report is generated automatically. Values are based on provided billing & emissions data.
      </div>
    """)

    html = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
      <meta charset='utf-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1' />
      <title>{report_title}</title>
      {css}
    </head>
    <body>
      {''.join(parts)}
    </body>
    </html>
    """
    return html


# ------------------------------
# PUBLIC API
# ------------------------------

def generate_report(
    metrics: Dict[str, Any],
    generated_figures: List[Tuple[object, str]] | None = None,
    recommendations: List[str] | None = None,
    organization: str = "Your Org",
    report_title: str = "Cloud Cost & Carbon Report",
    summary_text: str = "This report summarizes costs, emissions and efficiency across services and regions.",
    output_dir: str = "reports",
    base_filename: str | None = None,
    plot_dir: str = "output/plots",
) -> Dict[str, str]:
    """
    Build HTML report (self-contained) and export PDF if WeasyPrint is installed.

    Returns a dict with output paths: { 'html_path': ..., 'pdf_path': (optional) }
    """
    _ensure_dir(output_dir)

    # Prepare names
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = base_filename or f"report_{ts}"

    html_path = os.path.join(output_dir, f"{base}.html")
    pdf_path = os.path.join(output_dir, f"{base}.pdf")

    # Convert metrics to tables
    metrics_tables = dataframes_to_html_tables(metrics)

    # Collect images
    images: List[Dict[str, str]] = []
    if generated_figures:
        images = collect_plot_images(generated_figures, plot_dir=plot_dir,
                                     tmp_assets_dir=os.path.join(output_dir, "assets"))

    # Build HTML
    html = build_report_html(
        organization=organization,
        report_title=report_title,
        summary_text=summary_text,
        metrics_tables=metrics_tables,
        images=images,
        recommendations=recommendations,
    )

    # Save HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    outputs = {"html_path": html_path}

    # Export PDF (if available)
    if _WEASY_AVAILABLE:
        try:
            HTML(string=html).write_pdf(pdf_path)
            outputs["pdf_path"] = pdf_path
        except Exception as e:
            # Keep going even if PDF generation fails
            outputs["pdf_error"] = f"PDF generation failed: {e}"
    else:
        outputs["pdf_error"] = "WeasyPrint not installed; PDF not generated."

    return outputs


# ------------------------------
# __main__ TEST HOOK
# ------------------------------
if __name__ == "__main__":
    # Local test run without Dashboard integration.
    # Uses your existing modules if available.
    try:
        from data_loader import load_mock_data
        from calculator import calculate_metrics
        from recommender import generate_recommendations
        from visualizer import (
            total_cost_vs_emissions,
            service_wise_distribution,
            region_wise_comparison,
            stacked_service_contribution,
            generated_figures,
        )
    except Exception as e:
        raise SystemExit(f"Import error — make sure modules exist: {e}")

    # 1) Load data & compute metrics
    df = load_mock_data()
    metrics = calculate_metrics(df)

    # 2) Create a few plots (so the report has visuals)
    total_cost_vs_emissions(df)
    service_wise_distribution(df, "cost_usd")
    region_wise_comparison(df)
    stacked_service_contribution(df, "emission_kg")

    # 3) Generate recommendations
    recs = generate_recommendations(df)

    # 4) Build report
    summary = (
        "This report aggregates total cost and emissions by service and region, "
        "highlights carbon efficiency, and lists optimization opportunities."
    )

    outputs = generate_report(
        metrics=metrics,
        generated_figures=generated_figures,
        recommendations=recs,
        organization="Demo Org",
        report_title="Cloud Cost & Carbon — Sample Report",
        summary_text=summary,
        output_dir="reports",
        base_filename="sample_report",
    )

    print("\nReport generated:")
    for k, v in outputs.items():
        print(f"  {k}: {v}")