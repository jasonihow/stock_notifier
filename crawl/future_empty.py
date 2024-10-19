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
options.add_argument("--lang=zh-TW")  # 設置瀏覽器語言為繁體中文

# 禁用 Selenium 的日志輸出
service = Service(log_path="NUL")  # Windows 使用 'NUL'

# 啟動驅動
driver = webdriver.Chrome(options=options, service=service)

# 開啟網頁
driver.get("https://www.taifex.com.tw/cht/3/futContractsDate")
try:
    # 使用顯式等待，直到目標 div 加載完成
    div = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "printhere"))
    )

    html = div.get_attribute("outerHTML")
    soup = BeautifulSoup(html, "lxml")

    date = soup.find("p", class_="clearfix")
    date = date.text.split(" ")
    date = date[-1][2:-1]
    print(f"日期: {date}")
    tbody = soup.find("tbody")
    nums = []
    if tbody:
        # 提取每一行的數據
        rows = tbody.find_all("tr")
        for row in range(len(rows)):
            if row == 2 or row == 11:
                columns = rows[row].find_all("td")
                if len(columns) > 12:  # 確保有足夠的欄位
                    num = columns[11].text.split("\n")
                    want = num[1].replace(",", "")
                    nums.append(want[1:])
                else:
                    print(f"Row {row} does not have enough columns.")

        result = round(int(nums[0]) + int(nums[1]) / 4)
        print(f"外資期貨未平倉: {result} 口")
    else:
        print("找不到 tbody")

except Exception as e:
    print(f"發生錯誤: {e}")

finally:
    # 關閉瀏覽器
    driver.quit()
