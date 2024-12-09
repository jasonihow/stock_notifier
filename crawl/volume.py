import requests
import json

# API URL
url = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date=20241101&type=MS&response=json&_=1729853427943"

# 設定請求標頭
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Referer": "https://www.twse.com.tw/zh/trading/historical/mi-index.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "X-Requested-With": "XMLHttpRequest",
}

# 發送 GET 請求
response = requests.get(url, headers=headers)

# 檢查請求是否成功
if response.status_code == 200:
    # 解析資料
    # 嘗試用不同的編碼進行解碼
    try:
        # 假設資料是以 big5 編碼
        data = response.content.decode("UTF-8")
        # 由於原始資料是以某種結構化方式返回，嘗試將其轉換為字典

        json_data = json.loads(data)

        volume = json_data["tables"][6]["data"][16][1].replace(",", "")
        volume = int(volume) / 100000000  # 根據需求解析並處理資料
        print(volume)
    except Exception as e:
        print(f"資料解析失敗: {e}")
else:
    print(f"請求失敗，狀態碼: {response.status_code}")
