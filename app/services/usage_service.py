import pandas as pd
import io
from app.models.usage_model import REQUIRED_COLUMS
from app.models.usage_model_db import Usage
from sqlalchemy import func
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def load_data_from_bytes(contents: bytes):
    try:
        # Try UTF-8 first
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except UnicodeDecodeError:
        # Fallback encoding
        df = pd.read_csv(io.StringIO(contents.decode("latin1")))
    
    return df


def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMS if col not in df.columns]
    
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def save_to_db(df, db):
    records = []
    
    for _, row in df.iterrows():
        record = Usage(
            service=row["service"],
            region=row["region"],
            usage_hours=row["usage_hours"],
            usage_type=row["usage_type"],
            cost_usd=row["cost_usd"],
            emission_kg=row["emission_kg"] 
        )
        records.append(record)
    
    db.add_all(records)
    db.commit()
    
    return len(records)


def process_csv(contents: bytes, db):
    df = load_data_from_bytes(contents)
    
    validate_columns(df)
    
    inserted = save_to_db(df, db)

    return {
        "rows": len(df),
        "inserted": inserted,
        "columns": list(df.columns)        
    }


def get_all_usage(db):
    return db.query(Usage).all()


def get_filtered_usage(db, region=None, service=None):
    query = db.query(Usage)
    
    if region:
        query = query.filter(Usage.region == region)
    
    if service:
        query = query.filter(Usage.service == service)
    
    return query.all()


def get_summary(db, region=None, service=None):
    query = db.query(
        func.sum(Usage.cost_usd),
        func.sum(Usage.emission_kg)
    )
    
    if region:
        query = query.filter(Usage.region == region)
    
    if service:
        query = query.filter(Usage.service == service)
        
    result = query.first()
    
    filters = {}
    if region:
        filters["region"] = region
    if service:
        filters["service"] = service
        
    return {
        "total_cost": float(result[0] or 0),
        "total_emissions": float(result[1] or 0),
        "filters": filters
    }


def get_cost_by_service(db, region=None):
    query = db.query(
        Usage.service,
        func.sum(Usage.cost_usd)
    )
    
    if region:
        query = query.filter(Usage.region == region)
        
    results = query.group_by(Usage.service).all()
    
    return [
        {"service": r[0], "total_cost": float(r[1])}
        for r in results
    ]


def export_usage_to_csv(db, region=None, service=None):
    data = get_filtered_usage(db, region, service)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    #Header
    writer.writerow([
        "service",
        "region",
        "usage_hours",
        "usage_type",
        "cost_usd",
        "emission_kg"
    ])
    
    #Rows
    for d in data:
        writer.writerow([
            d.service,
            d.region,
            d.usage_hours,
            d.usage_type,
            d.cost_usd,
            d.emission_kg
        ])
        
    output.seek(0)
    return output


def export_usage_to_pdf(db, region=None, service=None):
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # title
    elements.append(Paragraph("Cloud Cost & Carbon Report", styles["Title"]))
    
    # Summary
    summary = get_summary(db, region, service)
    elements.append(Paragraph(f"Total Cost: ${summary['total_cost']}", styles["Normal"]))
    elements.append(Paragraph(f"Total Emissions: {summary['total_emissions']} kg", styles["Normal"]))
    
    # Table Data
    data = get_filtered_usage(db, region, service)
    
    table_data = [["Service", "Region", "Usage Hours", "Usage Type", "Cost", "Emissions"]]
    
    for d in data:
        table_data.append([
            d.service,
            d.region,
            d.usage_hours,
            d.usage_type,
            d.cost_usd,
            d.emission_kg
        ])
        
    table = Table(table_data)
    
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
    