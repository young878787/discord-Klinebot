# Discordbot-K線圖 (使用 Bybit API 調用)

## 更新
2025/1/25 beta 0.2 完善了搜尋功能 但想要新增按鈕補充更多時間 debug快2小好累先放棄 
2025/1/24 beta 0.1 嘗試加入指令搜尋結果只做到建資料庫還沒連結運算K線圖功能 並debug和學習一點東西 

## 介紹
Discordbot-K線圖是一個專門為交易者設計的自動化工具。它可以24H連線獲取即時數據，提供分析和提醒交易機會，幫助您做出更優化的交易決策。

## 功能特色
- 自動每小時提供即時資訊並提醒應進行交易。
- 有 `/owo` 指令可呼叫機器人作用。
- 提供 1H、4H的交易數據和即時的漲幅榜。

## 安裝指南
1. 自行新增 `.env` 檔案，包含下列內容：
   - DISCORD_TOKEN
   - DISCORD_CLIENT_ID
   - DISCORD_GUILD_ID
   - DISCORD_CHANNEL_ID
2. 安裝先前申請 Bybit API，并將 API 密鑰充填進相關配置。
3. 使用 Python 和 [Pybit](https://github.com/verata-veritatis/pybit) 套件。
4. 修改所有的路徑 改為目前本地的檔案夾 
例：
```bash
pip install pybit
```

## 使用方法
1. 啟動 Bot：確保配置檔無誤後執行。
2. 使用 `/owo` 指令和其他功能互動。
3. 每小時正常提供資訊，始終保持連線狀態。

## 技術細節
- 使用部分 AI 寫成 (60%)，其他由我設計和除錯。
- 主要套件：Pybit。
- 歡迎其他開發者提供優化或技術指導，我很希望了解更多。

## 貢獻說明
如果使用我的 Bot 賺錢，可以加入 Discord 和我分享經驗，我也想學習！

## 聯絡方式
- [Discord](https://discord.gg/UxwTqpvepr)
- IG: `young20160124`

## 其他資訊
- 我是學生，如有問題，歡迎反應給我，我會確保修正。
- Bot 會根據您的意見一直作出修改，感謝您的支持！
- 順帶一提 這是用chatgpt寫的readme 我文案懶得寫xd
- 目前bot 處在有空就修改的情況 使用狀況可能不太好 

