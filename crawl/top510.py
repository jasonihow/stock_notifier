from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys
import re

# 設置控制台輸出編碼為UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# 設定 Selenium 的 Chrome 驅動
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 如果不需要顯示瀏覽器，可以啟用 headless 模式
options.add_argument("--log-level=3")  # 設置日誌級別以抑制冗長輸出
options.add_argument("--lang=zh-TW")  # 設置語言為繁體中文

# 禁用 Selenium 的日志輸出
service = Service(log_path="NUL")  # Windows 使用 'NUL'

# 啟動驅動
driver = webdriver.Chrome(options=options, service=service)

# 開啟網頁
driver.get("https://www.taifex.com.tw/cht/3/largeTraderFutQryTbl")

try:
    # 使用顯式等待，直到目標元素加載完成
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_middle"))
    )

    soup = BeautifulSoup(driver.page_source, "lxml")

    # 提取日期
    date = soup.select_one(".section td").text.split()[-1]
    print(f"日期: {date}")

    # 提取數據
    tbody = soup.select("tbody")[1]  # 選擇第二個 tbody
    row = tbody.select("tr")[2]  # 選擇第三行
    columns = row.select("td")

    def extract_number(text):
        # 使用正則表達式提取數字，包括負數
        match = re.search(r"-?\d+", text.replace(",", ""))
        return int(match.group()) if match else 0

    nums = [extract_number(columns[i].text) for i in [1, 3, 5, 7]]

    top5 = nums[0] - nums[2]
    top10 = nums[1] - nums[3]

    print(f"前五大交易人留倉: {top5}")
    print(f"前十大交易人留倉: {top10}")

except Exception as e:
    print(f"發生錯誤: {e}")

finally:
    # 關閉瀏覽器
    driver.quit()
