import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pybit.unified_trading import HTTP
from mplfinance.original_flavor import candlestick_ohlc
from datetime import datetime
import logging

# 設定日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 從環境變數中讀取 API 鍵和密鑰
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
TESTNET = False  # True 表示使用測試網

# 讀取文件
def get_user_choice(filepath):
    with open(filepath, 'r',encoding='utf-8') as file:
        lines = file.readlines()
        symbol = str(lines[0].split('=')[1].strip())
        interval = lines[1].split('=')[1].strip()
        if interval =="未指定":interval = "5m"
        times = interval
        if interval =="1m":interval = 1
        elif interval =="5m":interval = 5
        elif interval =="15m":interval = 15
        elif interval =="30m":interval = 30
        elif interval =="1h":interval = 60
        elif interval =="4h":interval = 240
    return symbol, interval,times

# 測試讀取 userchose.txt 文件
user_choice_file = 'C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\discord\\userchose.txt'
symbol, interval ,times= get_user_choice(user_choice_file)

class BybitKlineWrapper:
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = None):
        self.session = HTTP(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
        )

    def get_kline_data(self, symbol: str = "BTCUSDT", interval: str = "240", limit: int = 20, timestamp: int = None):
        if timestamp is None:
            timestamp = int(time.time() * 1000)

        try:
            kline_data = self.session.get_kline(
                category="linear",
                symbol=symbol,
                interval=interval,
                limit=limit,
                **{"start_time": timestamp - (int(interval) * 1000 * limit), "end_time": timestamp}
            )["result"]

            if kline_data and "list" in kline_data and kline_data["list"]:
                df = self.process_kline_data(kline_data["list"])
                logging.info(f"Kline data retrieved for {symbol}")
                self.plot_kline(df)  # 繪製 K 線圖
            else:
                logging.warning("No Kline data found for the specified time.")
        except Exception as e:
            logging.error(f"Error retrieving Kline data: {e}")

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

    def plot_kline(self, df):
        # 確保 K highline 資料夾存在
        if not os.path.exists('K line'):
            os.makedirs('K line')

        # 將時間轉換為 matplotlib 可用的格式
        df['timestamp'] = mdates.date2num(df.index.to_pydatetime())

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})

        # 設置 K 線圖的寬度
        if interval == 1: width=0.0005
        elif interval == 5: width=0.002
        elif interval == 15: width=0.005
        elif interval == 30: width=0.01
        elif interval == 60: width=0.02
        elif interval == 240: width=0.1
        # 繪製 K 線圖，調整 width 參數以增加 K 線的寬度
        candlestick_ohlc(ax1, df[['timestamp', 'open', 'high', 'low', 'close']].values, width, colorup='g', colordown='r')

        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45)
        ax1.set_title(f"{symbol} K Line Chart {times}")
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Price')
        ax1.grid()

        # 繪製交易量柱狀圖
        colors = ['g' if close >= open else 'r' for open, close in zip(df['open'], df['close'])]
        ax2.bar(df['timestamp'], df['volume'], color=colors, width=width)
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Volume')
        plt.tight_layout()
        
        # 添加浮水印
        plt.text(0.5, 0.5, f'{symbol}/{times}', fontsize=70, color='gray', alpha=0.25,
                 ha='center', va='center', transform=ax1.transAxes, rotation=0)


        # 儲存 K 線圖到 K highline 資料夾
        plt.savefig("C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\discord\\user\\chose.png")  # 保存為 PNG 檔案
        plt.close()  # 關閉圖表以釋放記憶體
        #plt.show()
# 使用範例
wrapper = BybitKlineWrapper(
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
    testnet=TESTNET,
)

# 獲取 BTCUSDT 的 K 線數據，20根 K 線，60分間隔
wrapper.get_kline_data(symbol, interval, limit=200)
