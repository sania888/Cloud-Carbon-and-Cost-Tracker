from fastapi import FastAPI
from app.routes import usage
from app.database.connection import engine, Base
from app.models import usage_model_db
from fastapi.middleware.cors import CORSMiddleware
from app.services.scheduler import start_schelduler

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sania888.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(usage.router, prefix="/usage", tags=["Usage"])


@app.get("/")
def root():
    return {"message": "Cloud Carbon & Cost Tracker API is running"}


@app.on_event("startup")
def start_background_tasks():
    print("Starting scheduler...")
    # start_schelduler()
