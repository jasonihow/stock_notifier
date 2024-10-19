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
options.add_argument("--lang=zh-TW")  # 設置語言為繁體中文

# 禁用 Selenium 的日志輸出
service = Service(log_path="NUL")  # Windows 使用 'NUL'

# 啟動驅動
driver = webdriver.Chrome(options=options, service=service)

try:
    # 開啟網頁
    driver.get("https://www.taifex.com.tw/cht/3/futDailyMarketExcel?commodity_id=MTX")

    # 使用顯式等待，直到目標元素加載完成
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_middle"))
    )

    soup = BeautifulSoup(driver.page_source, "lxml")

    # 提取日期
    date_element = soup.find("div", class_="content edu_more")
    if date_element and date_element.find("p"):
        date = date_element.find("p").text.split("\t")[-1].strip()
        print(f"日期: {date}")
    else:
        print("無法找到日期")

    # 提取數據
    target_td = soup.find(
        "td", {"align": "right", "bgcolor": "#ecf2f9", "class": "12bk"}
    )
    if target_td:
        value = target_td.text.strip()
        print(f"小台全體未平倉量: {value}")
    else:
        print("無法找到目標數據")

except Exception as e:
    print(f"發生錯誤: {e}")

finally:
    # 關閉瀏覽器
    driver.quit()
