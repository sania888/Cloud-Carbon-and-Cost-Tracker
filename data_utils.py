import json
import pandas as pd

def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    
def prepare_dataframe(data):
    df = pd.DataFrame(data)

    column_mapping = {
        'month' : 'Month',
        'cost' : 'Cost($)',
        'emission' : 'Emission (kgCO2e)',
        'emissions' : 'Emissions (kgCO2e)',
        'region' : 'Region',
        'service' : 'Service'
    }

    df.columns = [col.strip().title() for col in df.columns]
    df.rename(columns = column_mapping, inplace=True)

    required_columns = ['Month', 'Cost ($)', 'Emissions (kgCO2e)', 'Region', 'Service']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Expected column '{col}' is missing in dataset.")
        
    df['Month'] = pd.to_datetime(df['Month'], errors ='coerce')
    df['Cost ($)'] = pd.to_numeric(df['Cost ($)'], errors='coerce')
    df['Emissions (kgCO2e)'] = pd.to_numeric(df['Emissions (kgCO2e)'], errors='coerce')

    return df.dropna(subset=['Month'])