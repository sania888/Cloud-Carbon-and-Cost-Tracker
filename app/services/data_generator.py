import random


def generate_dynamic_data(record):
    """"
        Takes a single record and return updated values
    """
    
    usage = record["usage_hours"]
    cost = record["cost_usd"]
    emission = record["emission_kg"]
    
    # simulate growth
    service = record["service"]
    
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
    

    usage_growth = usage * factor
    
    # cost proportional to usage
    cost_growth = cost * factor
    
    # emission proportional to usage
    emission_growth = emission * factor
    
    return {
        **record,
        "usage_hours": round(usage_growth, 2),
        "cost_usd": round(cost_growth, 2),
        "emission_kg": round(emission_growth, 2)
    }
