import time
from fastapi import Depends
from threading import Thread
from app.services.data_generator import generate_dynamic_data
from app.routes.usage import get_all_usage
from app.models.usage_model import REQUIRED_COLUMS
from app.database.connection import get_db

history = []

def start_schelduler():
    
    def run():
        print("Scheduler thread running...")
        while True:
            db = next(get_db())
            db_records = get_all_usage(db)
            raw_data = [
                {
                    "service": r.service,
                    "region": r.region,
                    "usage_hours": r.usage_hours,
                    "usage_type": r.usage_type,
                    "cost_usd": r.cost_usd,
                    "emission_kg": r.emission_kg
                }
                for r in db_records
            ]
            data = generate_dynamic_data(raw_data)
            
            total_cost = sum(d["cost_usd"] for d in data)
            total_emission = sum(d["emission_kg"] for d in data)
            
            snapshot = {
                "timestamp": time.time(),
                "total_cost": total_cost,
                "total_emission": total_emission
            }
            
            history.append(snapshot)
            
            print(f"History stored: {snapshot}")
            time.sleep(15)
        
    thread = Thread(target=run)
    thread.daemon=True
    thread.start()
    
    print("Scheduler started (thread launched)") 
