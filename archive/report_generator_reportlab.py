from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(metrics, plots, summaries, base_filename="report"):
    """
    Generates a PDF report with metrics, plots, and summaries.
    
    Args:
        metrics (dict): Key-value metrics (e.g., total cost, emissions).
        plots (list): List of file paths to saved plots (PNG).
        summaries (dict): Explanations of each plot.
        base_filename (str): Base filename for the PDF.
    """
    filename = f"{base_filename}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("🌍 Cloud Carbon & Cost Tracker Report", styles["Title"]))
    story.append(Spacer(1, 20))

    # Metrics
    story.append(Paragraph("📊 Key Metrics", styles["Heading2"]))
    for key, value in metrics.items():
        story.append(Paragraph(f"<b>{key}:</b> {value}", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Plots + Summaries
    for i, plot_path in enumerate(plots):
        story.append(Paragraph(f"📈 Visualization {i+1}", styles["Heading2"]))
        story.append(Image(plot_path, width=400, height=250))
        story.append(Spacer(1, 12))

        if i < len(summaries):
            story.append(Paragraph(summaries[i], styles["Normal"]))
        story.append(PageBreak())

    # Closing
    story.append(Paragraph("✅ End of Report", styles["Heading2"]))

    # Build PDF
    doc.build(story)
    return filename

