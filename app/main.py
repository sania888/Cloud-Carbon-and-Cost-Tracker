from fastapi import FastAPI
from app.routes import usage
# temporary test code
from app.database.connection import engine, Base
from app.models import usage_model_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(usage.router, prefix="/usage", tags=["Usage"])


@app.get("/")
def root():
    return {"message": "Cloud Carbon & Cost Tracker API is running"}
