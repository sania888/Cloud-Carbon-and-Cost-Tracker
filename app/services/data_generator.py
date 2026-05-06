import random
import time

LAST_UPDATE = time.time()

SERVICE_RATES = {
    "EC2": 0.2,          # $ per hour
    "Lambda": 0.0000002, # per request (simulated)
    "S3": 0.02,
    "RDS": 0.25,
    "CloudFront": 0.15,
    "DynamoDB": 0.1
}

EMISSION_FACTOR = {
    "EC2": 0.05,
    "Lambda": 0.0000001,
    "S3": 0.01,
    "RDS": 0.04,
    "CloudFront": 0.03,
    "DynamoDB": 0.02
}

def generate_dynamic_data(records):
    """"
        Takes a single record and return updated values
    """
    global LAST_UPDATE
    
    current_time = time.time()
    time_diff = current_time - LAST_UPDATE
    
    # Normalize time factor (convert seconds -> growth multiplier)
    time_factor = time_diff / 60 
    
    updated_data = []
    
    for record in records:
        usage = record["usage_hours"]
        cost = record["cost_usd"]
        emission = record["emission_kg"]
        service = record["service"]
    
    # simulate growth
    
    
        # SERVICE-BASED GROWTH
        if service == "EC2":
            factor  = random.uniform(0.01, 0.03)
    
        elif service == "Lambda":
            factor = random.uniform(0.02, 0.08)
    
        elif service == "S3":
            factor = random.uniform(0.005, 0.02)
        
        elif service == "RDS":
            factor = random.uniform(0.01, 0.025)
    
        elif service == "CloudFront":
            factor = random.uniform(0.03, 0.1)
    
        elif service == "DynamoDB":
            factor = random.uniform(0.01, 0.04)
    
        else:
            factor = random.uniform(0.01, 0.05)
    

        usage_growth = usage * factor * time_factor
        new_usage = usage + usage_growth
    
        # Get service rate
        rate = SERVICE_RATES.get(service, 0.1)
        emission_factor = EMISSION_FACTOR.get(service, 0.02)
    
        # Calculate new values based on usage
        new_cost = new_cost = new_usage * rate
        new_emission = new_usage * emission_factor

        updated_record= {
            **record,
            "usage_hours": round(new_usage, 2),
            "cost_usd": round(new_cost, 2),
            "emission_kg": round(new_emission, 2)
        }

        updated_data.append(updated_record)
    
    LAST_UPDATE = current_time

    return updated_data
