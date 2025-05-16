import os

import time
import logging
import matplotlib
from pybit.unified_trading import HTTP
from tabulate import tabulate  # 用於格式化輸出
from wcwidth import wcswidth  # 用於計算字元寬度
import matplotlib.pyplot as plt  # 用於繪製圖表
from matplotlib.ticker import FuncFormatter  # 用於格式化圖表刻度
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 支援中文
matplotlib.rcParams['axes.unicode_minus'] = False

# 設定日誌記錄
LOG_FOLDER = "coin-track"
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 輸出到控制台
        logging.FileHandler(os.path.join(LOG_FOLDER, "coin_track.log"), encoding="utf-8")  # 輸出到 coin-track 資料夾
    ]
)

# 從環境變數中讀取 API 鍵和密鑰
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
TESTNET = False  # True 表示使用測試網


def format_large_number(value):
    """格式化數值，將其轉換為帶單位的格式（萬/億），保留小數點後兩位"""
    if value >= 1e8:  # 億
        return f"{value / 1e8:.2f} 億"
    elif value >= 1e4:  # 萬
        return f"{value / 1e4:.2f} 萬"
    else:  # 小於萬
        return f"{value:.2f}"


def pad_string(value, width):
    """根據字元寬度補齊空格，確保對齊"""
    current_width = wcswidth(value)
    if current_width < width:
        return value + " " * (width - current_width)
    return value


class BybitMonitor:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """初始化 Bybit 監控器"""
        self.session = HTTP(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
        self.previous_open_interest_value = {}  # 用於儲存上一筆持倉價值
        self.previous_prices = {}  # 用於儲存上一筆價格
        self.is_first_run = True  # 標記是否為初次執行

    def get_all_market_data(self):
        """獲取所有交易對的持倉量、交易量和資金費率"""
        try:
            # 使用 /v5/market/tickers API 獲取所有交易對數據
            response = self.session.get_tickers(category="linear")

            if response and "result" in response and "list" in response["result"]:
                tickers = response["result"]["list"]
                results = []
                for ticker in tickers:
                    symbol = ticker.get("symbol", "Unknown")
                    try:
                        results.append({
                            "symbol": symbol,
                            "open_interest": float(ticker.get("openInterest", 0.0) or 0.0),  # 總持倉顆數
                            "open_interest_value": float(ticker.get("openInterestValue", 0.0) or 0.0),  # 總持倉價值
                            "last_price": float(ticker.get("lastPrice", 0.0) or 0.0),  # 幣價
                            "volume": float(ticker.get("turnover24h", 0.0) or 0.0),  # 交易量（估算）
                            "funding_rate": float(ticker.get("fundingRate", 0.0) or 0.0) * 100  # 資金費率百分比
                        })
                    except ValueError as e:
                        logging.error(f"Error parsing data for symbol {symbol}: {e}")
                        continue
                return results
            else:
                logging.warning("No data found for any symbols.")
                return []
        except Exception as e:
            logging.error(f"Error fetching market data: {e}")
            return []

    def save_table_as_image(self, data, headers, filename, title):
        """將前10與後10分成上下兩個表格儲存為圖片到 coin-track 資料夾，資金費率為負時顯示紅色"""
        folder = "coin-track"
        if not os.path.exists(folder):
            os.makedirs(folder)
        filepath = os.path.join(folder, filename)

        # 分割前10與後10
        top_10 = data[:10]
        bottom_10 = data[10:]

        fig, axs = plt.subplots(2, 1, figsize=(22, 12), dpi=500)
        plt.subplots_adjust(hspace=0.08)  # 拉近小標題與表格間距

        # 上方：前10
        axs[0].axis('off')
        table_top = axs[0].table(
            cellText=top_10,
            colLabels=headers,
            cellLoc='center',
            loc='center'
        )
        table_top.auto_set_font_size(False)
        table_top.set_fontsize(14)
        table_top.scale(1.5, 2)
        axs[0].set_title("持倉變化前10", fontsize=20, pad=10)  # 小標題，pad 控制與表格距離

        # 下方：後10
        axs[1].axis('off')
        table_bottom = axs[1].table(
            cellText=bottom_10,
            colLabels=headers,
            cellLoc='center',
            loc='center'
        )
        table_bottom.auto_set_font_size(False)
        table_bottom.set_fontsize(14)
        table_bottom.scale(1.5, 2)
        axs[1].set_title("持倉變化後10", fontsize=20, pad=10)

        # 設定資金費率為負數時字體為紅色
        for idx, row in enumerate(top_10, start=1):
            funding_rate_str = row[6].replace('%', '')
            try:
                if float(funding_rate_str) < 0:
                    cell = table_top[idx, 6]
                    cell.set_text_props(color='red')
            except Exception:
                continue
        for idx, row in enumerate(bottom_10, start=1):
            funding_rate_str = row[6].replace('%', '')
            try:
                if float(funding_rate_str) < 0:
                    cell = table_bottom[idx, 6]
                    cell.set_text_props(color='red')
            except Exception:
                continue

        # 刪除大標題，只保留小標題
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()
            

    def monitor_all_symbols(self):
        """監控所有交易對，並按照變化量排序"""
        market_data = self.get_all_market_data()
        table_data = []

        for data in market_data:
            symbol = data["symbol"]
            asset = symbol.replace("USDT", "")  # 提取交易對的單位，例如 BTCUSDT -> BTC

            # 計算持倉價值變化百分比
            if symbol not in self.previous_open_interest_value:
                self.previous_open_interest_value[symbol] = data['open_interest_value']
                change_percentage = 0.0  # 初始為 0
            else:
                previous_value = self.previous_open_interest_value[symbol]
                change_percentage = ((data['open_interest_value'] - previous_value) / previous_value) * 100
                self.previous_open_interest_value[symbol] = data['open_interest_value']  # 更新上一筆數據

            # 計算價格變化百分比
            if symbol not in self.previous_prices:
                self.previous_prices[symbol] = data['last_price']
                price_change_percentage = 0.0  # 初始為 0
            else:
                previous_price = self.previous_prices[symbol]
                if previous_price != 0:
                    price_change_percentage = ((data['last_price'] - previous_price) / previous_price) * 100
                else:
                    price_change_percentage = 0.0
                self.previous_prices[symbol] = data['last_price']  # 更新上一筆價格

            # 格式化持倉價值和交易量
            formatted_open_interest_value = format_large_number(data['open_interest_value'])
            formatted_volume = format_large_number(data['volume'])

            table_data.append([ 
                asset,  # 幣種
                f"{data['last_price']:g} USDT",  # 價格（完整顯示小數點後 8 位）
                f"{price_change_percentage:+.2f}%",  # 價格變化
                f"{data['open_interest']:.2f} {asset}",  # 持倉數量
                formatted_open_interest_value,  # 持倉價值
                formatted_volume,  # 交易量 (24h)
                f"{data['funding_rate']:.4f}%",  # 資金費率
                f"{change_percentage:+.2f}%"  # 持倉變化
            ])

        headers = ["幣種", "價格", "價格變化", "持倉數量", "持倉價值", "交易量(24h)", "資金費率", "持倉變化"]
        if not self.is_first_run:
            table_data.sort(key=lambda x: float(x[-1].strip('%')), reverse=True)
            top_10 = table_data[:10]  # 前 10 名
            bottom_10 = sorted(table_data[-10:], key=lambda x: float(x[-1].strip('%')))  # 後 10 名（由小到大）

            # 合併前10和後10
            combined = top_10 + bottom_10

            # 合併輸出
            output = (
                "持倉變化前 10 名與後 10 名:\n" +
                tabulate(
                    combined,
                    headers=headers,
                    tablefmt="fancy_grid",
                    colalign=("left", "right", "right", "right", "right", "right", "right", "right")
                )
            )
            # 將輸出寫入文件
            txt_path = os.path.join("coin-track", "coin-track.txt")
            with open(txt_path, "w", encoding="utf-8") as file:
                file.write(output)
            logging.info(f"Output written to {txt_path}")

            self.save_table_as_image(combined, headers, "coin-track.png", "持倉變化前10與後10")
            logging.info("Combined Top 10 and Bottom 10 image saved as coin-track.png.")
        else:
            self.is_first_run = False  # 標記初次執行已完成


if __name__ == "__main__":
    # 初始化監控器
    monitor = BybitMonitor(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET, testnet=TESTNET)

    # 固定更新間隔
    UPDATE_INTERVAL = 60 # 每 1 分鐘更新一次

    # 開始監控
    while True:
        monitor.monitor_all_symbols()
        time.sleep(UPDATE_INTERVAL)  # 每 UPDATE_INTERVAL 秒更新一次