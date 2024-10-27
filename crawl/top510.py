from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoAlertPresentException,
)
from bs4 import BeautifulSoup
import sys
import re
import traceback
import time

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
driver.get("https://www.taifex.com.tw/cht/3/largeTraderFutQry")

try:
    # 使用顯式等待，直到側邊欄加載完成
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_right"))
    )

    # 等待日期輸入框可用
    input_element = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "queryDate"))
    )
    input_element.clear()
    input_element.send_keys("2024/10/24")

    # 等待下拉選單元素可見
    select_element = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "contractId"))
    )

    # 使用 JavaScript 來選擇選項
    driver.execute_script(
        """
        var select = arguments[0];
        for(var i = 0; i < select.options.length; i++) {
            if(select.options[i].text.includes('TX')) {
                select.selectedIndex = i;
                var event = new Event('change');
                select.dispatchEvent(event);
                break;
            }
        }
    """,
        select_element,
    )

    # 增加等待時間以確保選擇生效
    time.sleep(3)

    # 找到並點擊 "送出查詢" 按鈕
    submit_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.btn_orange#submitButton"))
    )
    print("按鈕已找到並可點擊")

    # 使用 JavaScript 點擊按鈕
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    driver.execute_script("arguments[0].click();", submit_button)
    print("按鈕已點擊")

    # 等待頁面加載新數據
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
    )
    print("新數據已加載")

    # 使用 BeautifulSoup 解析頁面
    soup = BeautifulSoup(driver.page_source, "lxml")

    # 提取數據
    tbody = soup.select("tbody")[0]  # 選擇第二個 tbody
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
