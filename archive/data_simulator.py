import pandas as pd
import random
import time

def simulate_monthly_data():
    services = ['EC2', 'S3', 'Lambda', 'RDS']
    months = pd.date_range(start='2025-01-01', periods=6, freq='MS')

    data = []
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


class MockDataStreamer:
    """
    Streams per-second mock data for Phase 1 dashboard.
    """
    def __init__(self):
        self.services = ['EC2', 'S3', 'Lambda', 'RDS']

    def stream_per_second(self):
        while True:
            data_point = {}
            for service in self.services:
                # Random per-second cost and carbon
                cost = round(random.uniform(0.01, 0.05), 3)
                carbon = round(random.uniform(0.05, 0.2), 3)
                data_point[service] = {'cost_usd': cost, 'emission_kg_co2': carbon}
            yield data_point
            time.sleep(1)


# Example usage
if __name__ == "__main__":
    streamer = MockDataStreamer()
    for item in streamer.stream_per_second():
        print(item)
