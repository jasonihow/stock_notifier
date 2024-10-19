from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys

# 設置控制台輸出編碼為UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# 設定 Selenium 的 Chrome 驅動
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_argument("--lang=zh-TW")

# 禁用 Selenium 的日志輸出
service = Service(log_path="NUL")

# 啟動驅動
driver = webdriver.Chrome(options=options, service=service)

try:
    # 開啟網頁
    driver.get("https://www.taifex.com.tw/cht/3/callsAndPutsDate")

    # 使用顯式等待，直到目標 div 加載完成
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "printhere"))
    )

    soup = BeautifulSoup(driver.page_source, "lxml")

    # 提取日期
    date_span = soup.find("span", class_="right")
    date = date_span.text.strip().split("日期")[-1] if date_span else "日期未找到"
    print(f"日期: {date}")

    tbody = soup.find("tbody")
    if tbody:
        rows = tbody.find_all("tr")
        nums = [
            int(row.find_all("td")[11].text.replace(",", "").strip())
            for row in [rows[2], rows[5]]
            if len(row.find_all("td")) > 11
        ]

        if len(nums) == 2:
            result = nums[0] - nums[1]
            print(f"外資選擇權: {result}")
        else:
            print("無法計算結果：數據不完整")
    else:
        print("找不到 tbody")

except Exception as e:
    print(f"發生錯誤: {e}")

finally:
    # 關閉瀏覽器
    driver.quit()
