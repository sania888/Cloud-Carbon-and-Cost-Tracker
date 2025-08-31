""" 1st Module
Objective:
Compute core financial and environmental metrics from raw AWS billing or usage data.

How it helps:
Converts raw numbers (costs, usage hours, service-level details) into interpretable insights like carbon emissions, efficiency ratios, and service-wise breakdowns.

Key Features:

Cost-to-Carbon conversion (based on emission factors).

Service-wise and region-wise cost/emission aggregation.

Support for both default and custom emission factors.

Plug-and-play for API or CSV data inputs.
"""

import pandas as pd

def calculate_metrics(df: pd.DataFrame):
    required_cols = {'service', 'region', 'usage_hours', 'usage_type', 'cost_usd', 'emission_kg'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns. Found: {df.columns.tolist()}")

    results = {}

    # 1. total cost and emissions by service
    by_service = df.groupby('service').agg(
        total_cost_usd=('cost_usd', 'sum'),
        total_emission_kg=('emission_kg', 'sum')
    ).reset_index()
    results['by_service'] = by_service

    # 2. total cost and emissions by region
    by_region = df.groupby('region').agg(
        total_cost_usd=('cost_usd', 'sum'),
        total_emission_kg=('emission_kg', 'sum')
    ).reset_index()
    results['by_region'] = by_region

    # 3. carbon efficiency (kg CO₂ per dollar) per service
    efficiency = by_service.copy()
    efficiency['emission_per_dollar'] = efficiency['total_emission_kg'] / efficiency['total_cost_usd']
    results['carbon_efficiency'] = efficiency.sort_values(by='emission_per_dollar', ascending=False)

    # 4. carbon intensity per hour (kg CO₂ per hour)
    df['carbon_per_hour'] = df['emission_kg'] / df['usage_hours']
    by_type = df.groupby('usage_type').agg(
        avg_carbon_per_hour=('carbon_per_hour', 'mean'),
        total_usage_hours=('usage_hours', 'sum')
    ).reset_index()
    results['carbon_intensity'] = by_type.sort_values(by='avg_carbon_per_hour', ascending=False)

    # 5. top emitter service and region 
    top_service = by_service.sort_values(by='total_emission_kg', ascending=False).iloc[0]
    top_region = by_region.sort_values(by='total_emission_kg', ascending=False).iloc[0]
    results['top_emitters'] = {
        'service': {
            'name': top_service['service'],
            'emission_kg': top_service['total_emission_kg']
        },
        'region': {
            'name': top_region['region'],
            'emission_kg': top_region['total_emission_kg']
        }
    }

    # ✅ Return both the DataFrame and computed results
    return df, results


if __name__ == "__main__":
    df = pd.read_csv('mock_data/aws_billing_mock.csv')
    pd.set_option('display.max_columns', None)

    print("Available columns:", df.columns.tolist())
    print(df.head())

    df, results = calculate_metrics(df)

    print("\n📊 Total Cost & Emissions by Service:")
    print(results['by_service'].to_string(index=False))

    print("\n📈 Carbon Efficiency (kg CO2 per $):")
    print(results['carbon_efficiency'].to_string(index=False))

    print("\n🔥 Top Emitters:")
    print(results['top_emitters'])

    print("\n⚡ Carbon Intensity per Usage Type:")
    print(results['carbon_intensity'].to_string(index=False))

    print("\n🌍 Total Cost & Emissions by Region:")
    print(results['by_region'].to_string(index=False))
