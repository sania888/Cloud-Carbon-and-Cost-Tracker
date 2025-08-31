# carbon_cost_tracker.py

from data_loader import get_mock_usage, get_region_carbon_intensity, get_default_carbon_intensity
from calculator import calculate_results
from exporter import print_results, save_to_json

def main():
    usage_data = get_mock_usage()
    region_intensity = get_region_carbon_intensity()
    default_intensity = get_default_carbon_intensity()

    results = calculate_results(usage_data, region_intensity, default_intensity)

    print_results(results)
    save_to_json(results)

if __name__ == "__main__":
    main()
