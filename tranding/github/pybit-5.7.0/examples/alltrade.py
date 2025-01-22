import os
import time
import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pybit.unified_trading import HTTP
from mplfinance.original_flavor import candlestick_ohlc
from datetime import datetime, timedelta
import logging
import shutil

# 設定日誌記錄，將日誌輸出到指定的檔案中
log_file_path = "C:/Users/Rushia is boingboing/Desktop/tranding/github/pybit-5.7.0/examples/combined.log"
logging.basicConfig(
    level=logging.ERROR,  # 設定日誌級別為 ERROR
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 從環境變數中讀取 API 鍵和密鑰
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
TESTNET = False  # True 表示使用測試網

class BybitTradeFetcher:
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = None):
        self.session = HTTP(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
        )

    def get_all_usdt_trading_pairs(self):
        try:
            response = self.session.get_instruments_info(category="spot")
            if 'ret_code' in response and response['ret_code'] == 0:
                symbols = [item for item in response['result']['list'] if item['quote_currency'] == 'USDT']
                return symbols
            else:
                logging.error(f"Error retrieving symbols: {response.get('ret_msg', 'Unknown error')}")
                return []
        except Exception as e:
            logging.error(f"Exception occurred while retrieving symbols: {e}")
            return []

    def save_symbols_to_json(self, symbols, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(symbols, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Exception occurred while saving symbols to JSON: {e}")

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

    def plot_kline(self, df, symbol):
        # 確保 K highline 資料夾存在
        kline_dir = 'K highline'
        if not os.path.exists(kline_dir):
            os.makedirs(kline_dir)

        # 將時間轉換為 matplotlib 可用的格式
        df['timestamp'] = mdates.date2num(df.index.to_pydatetime())

        fig, ax = plt.subplots(figsize=(10, 5))

        # 繪製 K 線圖，調整 width 參數以增加 K 線的寬度
        candlestick_ohlc(ax, df[['timestamp', 'open', 'high', 'low', 'close']].values, width=0.002, colorup='g', colordown='r')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45)
        plt.title(f'K Line Chart for {symbol}')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.grid()
        plt.tight_layout()

        # 儲存 K 線圖到 K highline 資料夾
        plt.savefig(f"{kline_dir}/{symbol}_Kline.png")  # 保存為 PNG 檔案
        plt.close()  # 關閉圖表以釋放記憶體

if __name__ == "__main__":
    # 獲取所有 USDT 交易對並保存到 JSON 文件
    fetcher = BybitTradeFetcher(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET, testnet=TESTNET)
    symbols = fetcher.get_all_usdt_trading_pairs()
    if symbols:
        fetcher.save_symbols_to_json(symbols, 'c:/Users/Rushia is boingboing/Desktop/tranding/github/pybit-5.7.0/examples/alltrade.json')

    # 比較所有交易對的漲幅並輸出前10個漲幅最大的交易對
    wrapper = BybitKlineWrapper(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET, testnet=TESTNET)
    top_changes = wrapper.compare_price_changes()

    # 清空 K highline 資料夾
    kline_dir = 'K highline'
    if not os.path.exists(kline_dir):
        os.makedirs(kline_dir)
    else:
        for filename in os.listdir(kline_dir):
            file_path = os.path.join(kline_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logging.error(f'Failed to delete {file_path}. Reason: {e}')

    output_messages = []
    for rank, (symbol, (change, open_price, close_price)) in enumerate(top_changes, start=1):
        message = f"{rank}. {symbol}: {change:.2f}% (Open: {open_price}, Close: {close_price})"
        print(message)
        output_messages.append(message)
        df = wrapper.get_kline_data(symbol=symbol, interval="5", limit=200)
        if df is not None:
            wrapper.plot_kline(df, symbol)

    # 將輸出結果保存到文件
    output_file_path = "C:/Users/Rushia is boingboing/Desktop/tranding/github/pybit-5.7.0/examples/output.txt"
    with open(output_file_path, 'w', encoding='utf-8') as f:
        for message in output_messages:
            f.write(message + "\n")