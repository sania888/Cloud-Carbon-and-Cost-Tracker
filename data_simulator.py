import pandas as pd
import random

def simulate_monthly_data():
    services = ['EC2', 'S3', 'Lambda', 'RDS']
    months = pd.date_range(start='2025-01-01', periods=6, freq='MS')

    data= []
    for month in months:
        for service in services:
            cost = round(random.uniform(10, 100), 2)
            emissions = round(cost * random.uniform(0.05, 0.15), 2)
            data.append({
                'service': service,
                'month': month.strftime('%Y-%m'),
                'cost_usd': cost,
                'emission_kg_co2': emissions
            })

    df = pd.DataFrame(data)
    return df