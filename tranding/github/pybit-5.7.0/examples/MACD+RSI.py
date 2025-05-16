import os
import time
import pandas as pd
import logging
from pybit.unified_trading import HTTP

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
        
    def calculate_rsi(self, df, period=14):
        delta = df['close'].diff()
        loss = delta.where(delta > 0, 0).abs()
        gain = delta.where(delta < 0, 0).abs()
        
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 輸出 gain, loss 和對應的 BTC 價格，忽略小數後兩點
        for i in range(len(df)):
            print(f"BTC價格: {df['close'].iloc[i]:.2f}, Gain: {gain.iloc[i]:.2f}, Loss: {loss.iloc[i]:.2f}")
        
        return rsi
        
        
    def get_kline_data(self, symbol: str = "BTCUSDT", interval: str = "60", limit: int = 20, timestamp: int = None):
        if timestamp is None:
            timestamp = int(time.time() * 1000)

            # 將時間戳對齊到整點
        timestamp = timestamp - (timestamp % (60 * 60 * 1000))

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
                df['RSI'] = self.calculate_rsi(df)  # 計算 RSI 並添加到 DataFrame
                logging.info(f"Kline data retrieved for {symbol}")
                latest_data = df.iloc[1]  # 獲取最新數據
                print(f"最新收盤價: {latest_data['close']}, 最新 RSI: {latest_data['RSI']}")
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

# 使用範例
wrapper = BybitKlineWrapper(
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
    testnet=TESTNET,
)

# 獲取 BTCUSDT 的 K 線數據，20根 K 線，60分間隔
wrapper.get_kline_data(symbol="BTCUSDT", interval="15", limit=15)