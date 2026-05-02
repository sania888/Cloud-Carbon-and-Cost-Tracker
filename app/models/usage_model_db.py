from sqlalchemy import Column, Integer, String, Float
from app.database.connection import Base


class Usage(Base):
    __tablename__ = "usage"
    
    id = Column(Integer, primary_key=True, index=True)
    
    service = Column(String, nullable=False)
    region = Column(String, nullable=False)
    usage_hours = Column(Float, nullable=False)
    usage_type = Column(String, nullable=False)
    cost_usd = Column(Float, nullable=False)
    emission_kg = Column(Float, nullable=False)