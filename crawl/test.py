from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoAlertPresentException,
)
from bs4 import BeautifulSoup
import sys
import re
import traceback
import time
from selenium.webdriver.support.ui import Select

# 設置控制台輸出編碼為UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# 設定 Selenium 的 Chrome 驅動
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # 如果不需要顯示瀏覽器，可以啟用 headless 模式
options.add_argument("--log-level=3")  # 設置日誌級別以抑制冗長輸出
options.add_argument("--lang=zh-TW")  # 設置語言為繁體中文

# 禁用 Selenium 的日志輸出
service = Service(log_path="NUL")  # Windows 使用 'NUL'

# 啟動驅動
driver = webdriver.Chrome(options=options, service=service)

# 開啟網頁
driver.get("https://www.taifex.com.tw/cht/3/futDailyMarketReport")

try:
    # 使用顯式等，直到側邊欄加載完
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_right"))
    )

    # 等待日期輸入框可用
    input_element = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "queryDate"))
    )
    input_element.clear()
    input_element.send_keys("2024/10/24")

    # 等待選擇時段的下拉選單可見
    market_code_select = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "MarketCode"))
    )

    # 點擊選擇時段的下拉選單
    market_code_select.click()

    # 等待並選擇一般交易時段（value="0"）
    option_market_code = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//select[@id='MarketCode']/option[@value='0']")
        )
    )
    option_market_code.click()  # 點擊選擇一般交易時段

    # 等待選擇契約的下拉選單可見
    commodity_idt_select = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "commodity_idt"))
    )

    # 點擊選擇契約的下拉選單
    commodity_idt_select.click()

    # 等待並選擇契約 MTX
    option_commodity_idt = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//select[@id='commodity_idt']/option[@value='MTX']")
        )
    )
    option_commodity_idt.click()  # 點擊選擇 MTX

    # 等待「送出查詢」按鈕可見
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "button"))
    )

    # 點擊「送出查詢」按鈕
    submit_button.click()

    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "lxml")

    # 提取數據
    target_td = soup.find(
        "td", {"align": "right", "bgcolor": "#ecf2f9", "class": "12bk"}
    )
    if target_td:
        value = target_td.text.strip()
        print(f"小台全體未平倉量: {value}")
    else:
        print("無法找到目標數據")

except UnexpectedAlertPresentException:
    try:
        alert = driver.switch_to.alert
        print(f"發生警告: {alert.text}")
        alert.accept()  # 關閉警告
        print("警告已關閉，重試操作")
        # 這裡可以選擇重試操作或其他處理方式
    except NoAlertPresentException:
        print("警告已經不存在")

except Exception as e:
    print(f"發生錯誤: {e}")
    traceback.print_exc()

finally:
    # 關閉瀏覽器
    driver.quit()
