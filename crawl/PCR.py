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
options.add_argument("--headless")  # 如果不需要顯示瀏覽器，可以啟用 headless 模式
options.add_argument("--log-level=3")  # 設置日誌級別以抑制冗長輸出
options.add_argument("--lang=zh-TW")

# 禁用 Selenium 的日志輸出
service = Service(log_path="NUL")  # Windows 使用 'NUL'

# 啟動驅動
driver = webdriver.Chrome(options=options, service=service)

# 開啟網頁
driver.get("https://www.taifex.com.tw/cht/3/pcRatio")

try:
    # 使用顯式等待，直到目標 div 加載完成
    div = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "printhere"))
    )

    soup = BeautifulSoup(driver.page_source, "lxml")

    tbody = soup.find("tbody")
    if tbody:
        row = tbody.find("tr")
        columns = row.find_all("td")
        if len(columns) >= 2:
            date = columns[0].text.strip()
            pcr = columns[-1].text.strip()
            print(f"日期: {date}")
            print(f"選擇權PCR: {pcr}")
        else:
            print("找不到足夠的數據列")
    else:
        print("找不到 tbody")

except Exception as e:
    print(f"發生錯誤: {e}")

finally:
    # 關閉瀏覽器
    driver.quit()
