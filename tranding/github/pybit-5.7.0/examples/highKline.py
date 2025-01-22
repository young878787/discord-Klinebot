import os
import time
import pandas as pd
import json
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

    def get_kline_data(self, symbol: str = "BTCUSDT", interval: str = "60", limit: int = 24):
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
                logging.warning(f"No Kline data found for {symbol} in the specified time.")
                return None
        except Exception as e:
            logging.error(f"Error retrieving Kline data for {symbol}: {e}")
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

    def calculate_percentage_change(self, df):
        if df is None or df.empty:
            return None, None, None
        open_price = df['open'].iloc[0]
        close_price = df['close'].iloc[-1]
        percentage_change = ((open_price - close_price) / open_price) * 100
        return percentage_change, open_price, close_price

    def compare_price_changes(self):
        # 讀取 alltrade.json 文件中的所有交易對符號
        try:
            with open('c:/Users/Rushia is boingboing/Desktop/tranding/github/pybit-5.7.0/examples/alltrade.json', 'r') as file:
                symbols_data = json.load(file)
        except FileNotFoundError:
            logging.error("alltrade.json file not found.")
            return []
        except json.JSONDecodeError:
            logging.error("Error decoding alltrade.json file.")
            return []

        symbols = [item['Symbol'] for item in symbols_data]

        changes = {}
        for symbol in symbols:
            df = self.get_kline_data(symbol=symbol)
            if df is not None:
                change, open_price, close_price = self.calculate_percentage_change(df)
                if change is not None:
                    changes[symbol] = (change, open_price, close_price)
            else:
                logging.warning(f"Skipping {symbol} due to missing data.")

        sorted_changes = sorted(changes.items(), key=lambda item: item[1][0], reverse=True)
        return sorted_changes[:10]  # 返回前10個漲幅最大的交易對

if __name__ == "__main__":
    wrapper = BybitKlineWrapper(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET, testnet=TESTNET)
    top_changes = wrapper.compare_price_changes()
    for rank, (symbol, (change, open_price, close_price)) in enumerate(top_changes, start=1):
        print(f"{rank}. {symbol}: {change:.2f}% (Open: {open_price}, Close: {close_price})")
#def calculate_percentage_change(self, df):
        #if df is None or df.empty:
        #    return None, None, None
        #open_price = df['open'].iloc[0]
        #close_price = df['close'].iloc[-1]
        #percentage_change = ((open_price - close_price) / close_price) * 100
        #return percentage_change, open_price, close_price