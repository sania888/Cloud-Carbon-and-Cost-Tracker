import pandas as pd
import os
def load_mock_data(file_path="mock_data/aws_billing_mock.csv"):
    """
    Lock mock AWS billing data from CSV file.

    Parameters:
    file_path(str): Path to the mock data file

    Returns:
        pd.DateFrame: Loaded data as a pandas DataFrame
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='latin1')
        
    print(f"Data Loaded {len(df)} records from {file_path}")
    return df

if __name__== "__main__":
    df = load_mock_data()
    print(df.head())