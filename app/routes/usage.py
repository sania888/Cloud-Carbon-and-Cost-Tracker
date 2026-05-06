from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from app.services.usage_service import get_cost_by_service, get_summary, process_csv, get_filtered_usage
from app.database.connection import get_db
from app.services.usage_service import get_all_usage, export_usage_to_csv, export_usage_to_pdf
from typing import Optional
from fastapi.responses import StreamingResponse
from app.services.data_generator import generate_dynamic_data
from app.services.scheduler import history

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db = Depends(get_db)):
    try:
        contents = await file.read()
        # convert bytes -> pandas Dataframe
        result = process_csv(contents, db)
    
        return {
            "filename": file.filename,
            **result
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    # except Exception:
    #     raise HTTPException(status_code=500, detail="Internal server error")
    
    except Exception as e:
        print("ERROR: ", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/all")
# def get_usage_data(db = Depends(get_db)):
#     data = get_all_usage(db)
#     base_data = [
#         {
#                 "service": d.service,
#                 "region": d.region,
#                 "usage_hours": d.usage_hours,
#                 "usage_type": d.usage_type,
#                 "cost_usd": d.cost_usd,
#                 "emission_kg": d.emission_kg
#             }
#             for d in data
#     ]
    
#     # Applying dynamic generator
#     dynamic_data = generate_dynamic_data(base_data)
#     return {
#         "count": len(dynamic_data),
#         "data": dynamic_data
#     }

@router.get("/all")
def get_usage_data(db = Depends(get_db)):
    try:
        data = get_all_usage(db)

        base_data = [
            {
                "service": d.service,
                "region": d.region,
                "usage_hours": d.usage_hours,
                "usage_type": d.usage_type,
                "cost_usd": d.cost_usd,
                "emission_kg": d.emission_kg
            }
            for d in data
        ]

        dynamic_data = generate_dynamic_data(base_data)

        return {
            "count": len(dynamic_data),
            "data": dynamic_data
        }

    except Exception as e:
        import traceback

        error_message = traceback.format_exc()

        print("FULL ERROR:")
        print(error_message)

        return {
            "error": str(e),
            "traceback": error_message
        }

@router.get("/")
def get_usage_filtered(
    region: Optional[str] = Query(None),
    service: Optional[str] = Query(None),
    db = Depends(get_db)
):
    data = get_filtered_usage(db, region, service)
    
    filters = {}
    if region:
        filters["region"] = region
    if service:
        filters["service"] = service
    
    return {
        "count": len(data),
        "filters": filters,
        "data": [
            {
                "service": d.service,
                "region": d.region,
                "usage_hours": d.usage_hours,
                "usage_type": d.usage_type,
                "cost_usd": d.cost_usd,
                "emission_kg": d.emission_kg
            }
            for d in data
        ]
    }


@router.get("/summary")
def get_usage_summary(
    region: Optional[str] = None,
    service: Optional[str] = None,
    db = Depends(get_db)
):    
    return get_summary(db, region, service)


@router.get("/by-service")
def cost_by_service(
    region: Optional[str] = None,
    db = Depends(get_db)
):
    return get_cost_by_service(db, region)


@router.get("/export")
def export_csv(
    region: Optional[str] = None,
    service: Optional[str] = None,
    db = Depends(get_db)
):
    csv_file = export_usage_to_csv(db, region, service)
    
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=usage_report.csv"}
    )


@router.get("/export/pdf")
def export_pdf(
    region: Optional[str] = None,
    service: Optional[str] = None,
    db = Depends(get_db)
):
    pdf_file = export_usage_to_pdf(db, region, service)
    
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=usage_report.pdf"}
    )


@router.get("/history")
def get_history():
    return {
        "count": len(history),
        "data": history
    }
