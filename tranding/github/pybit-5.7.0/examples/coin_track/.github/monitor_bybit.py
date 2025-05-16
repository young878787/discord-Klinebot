from http import client
import time
import os
from pybit.unified_trading import HTTP

# Read API credentials and testnet flag from environment variables
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
TESTNET = False  # True 表示使用測試網


class BybitKlineWrapper:
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = None):
        self.session = HTTP(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
        )

def fetch_positions():
    """Fetch open positions from Bybit."""
    try:
        response = client.get_positions()
        return response['result']
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return []

# Update fetch_funding_rates to use the correct API endpoint
def fetch_funding_rates():
    """Fetch funding rates for all symbols."""
    try:
        response = client.get_public_funding_rate()  # Corrected method name
        return response['result']
    except Exception as e:
        print(f"Error fetching funding rates: {e}")
        return []

# Update fetch_trading_volume to include correct parameters
def fetch_trading_volume():
    """Fetch trading volume for all symbols."""
    try:
        response = client.get_tickers(category="linear")  # Specify category as 'linear'
        return response['result']
    except Exception as e:
        print(f"Error fetching trading volume: {e}")
        return []

def monitor_bybit():
    """Monitor Bybit perpetual contracts."""
    while True:
        print("Fetching data...")
        positions = fetch_positions()
        funding_rates = fetch_funding_rates()
        trading_volume = fetch_trading_volume()

        print("Open Positions:", positions)
        print("Funding Rates:", funding_rates)
        print("Trading Volume:", trading_volume)

        time.sleep(60)  # Fetch data every 60 seconds

if __name__ == "__main__":
    monitor_bybit()