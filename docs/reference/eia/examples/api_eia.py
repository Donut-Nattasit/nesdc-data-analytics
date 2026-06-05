import requests
import pandas as pd

def get_data_STEO(SERIES_ID, col_name='value'):
    API_VERSION = 'v2'
    url = f"https://api.eia.gov/{API_VERSION}/steo/data/"
    params = {
        'api_key': 'ugXohh7WKnvSito1OKKEbofWbCfff50TTdNmL6Dh',
        'frequency': 'monthly',
        'data[0]': 'value',
        'facets[seriesId][]': SERIES_ID,
        'sort[0][column]': 'period',
        'sort[0][direction]': 'asc'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get('response', {}).get('data', [])
        if data:
            df = pd.DataFrame(data)
            df = df[['period', 'value']]
            # rename period to date
            df.rename(columns={'period': 'date'}, inplace=True)
            # Convert 'value' to numeric, handling errors
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            # convert 'date' to datetime (current format is YYYY-MM)
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m')
            # set 'date' as index
            df.set_index('date', inplace=True)
            # rename 'value' to col_name
            df.rename(columns={'value': col_name}, inplace=True)
            return df
        else:
            print("No data found for the specified series ID.")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()