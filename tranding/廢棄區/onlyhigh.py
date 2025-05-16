import os
import time
import pandas as pd
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta
import logging

# 設定日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 從環境變數中讀取 API 鍵和密鑰
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

    def get_kline_data(self, symbol: str = "ETHUSDT", interval: str = "60", limit: int = 24):
        end_time = int(time.time() * 1000)
        start_time = end_time - (24 * 60 * 60 * 1000)  # 24 小時前的時間戳

        try:
            kline_data = self.session.get_kline(
                category="linear",
                symbol=symbol,
                interval=interval,
                limit=limit,
                **{"start_time": start_time, "end_time": end_time}
            )["result"]

            if kline_data and "list" in kline_data and kline_data["list"]:
                df = self.process_kline_data(kline_data["list"])
                logging.info(f"Kline data retrieved for {symbol}")
                return df
            else:
                logging.warning("No Kline data found for the specified time.")
                return None
        except Exception as e:
            logging.error(f"Error retrieving Kline data: {e}")
            return None

    def process_kline_data(self, kline_list):
        data = []
        for kline in kline_list:
            data.append([kline[0], kline[1], kline[2], kline[3], kline[4], kline[5]])

        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_numeric(df['timestamp'])  # 顯式轉換為數字類型
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # 將數據列轉換為數字類型
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        df['volume'] = pd.to_numeric(df['volume'])

        df.set_index('timestamp', inplace=True)
        return df

    def get_current_price(self, symbol: str = "ETHUSDT"):
        try:
            ticker_data = self.session.get_tickers(
                category="linear",
                symbol=symbol
            )["result"]

            if ticker_data and len(ticker_data) > 0:
                current_price = float(ticker_data[0]['last_price'])
                logging.info(f"Current price for {symbol} retrieved: {current_price}")
                return current_price
            else:
                logging.warning("No ticker data found for the specified symbol.")
                return None
        except Exception as e:
            logging.error(f"Error retrieving current price: {e}")
            return None

    def calculate_percentage_change(self, df):
        if df is not None and len(df) >= 2:
            latest_close = df['close'].iloc[0]
            previous_close = df['close'].iloc[-1]
            logging.info(f"latest_close: {latest_close}, previous_close: {previous_close}")
            percentage_change = ((latest_close - previous_close) / previous_close) * 100
            return percentage_change
        else:
            return None

def fetch_and_print_percentage_change():
    wrapper = BybitKlineWrapper(
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
        testnet=TESTNET,
    )

    df = wrapper.get_kline_data(symbol="ETHUSDT", interval="60", limit=24)
    percentage_change = wrapper.calculate_percentage_change(df)
    if percentage_change is not None:
        logging.info(f"ETHUSDT 過去24小時漲幅: {percentage_change:.2f}%")
    else:
        logging.warning("無法計算漲幅")

# 一次性測試
fetch_and_print_percentage_change()