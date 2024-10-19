from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import sys

# 設置控制台輸出編碼為UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# 設定 Selenium 的 Chrome 驅動
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 如果不需要顯示瀏覽器，可以啟用 headless 模式
options.add_argument("--lang=zh-TW")  # 設置瀏覽器語言為繁體中文
driver = webdriver.Chrome(options=options)

# 開啟網頁
driver.get("https://www.twse.com.tw/zh/trading/historical/mi-index.html")

try:
    # 使用顯式等待，直到目標 div 加載完成
    div = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "reports"))
    )

    html = div.get_attribute("outerHTML")

    soup = BeautifulSoup(html, "lxml")

    # 提取日期並轉換格式
    time_element = soup.find("div", id="table6")
    date_str = time_element.find("hgroup").text.split(" ")[0][1:]
    year, month, day = (
        date_str.replace("年", "/").replace("月", "/").replace("日", "").split("/")
    )
    year = int(year) + 1911  # 轉換民國年為西元年
    date = f"{year:04d}/{int(month):02d}/{int(day):02d}"
    print(f"日期: {date}")

    # 提取總成交金額
    tbody = soup.find("tbody", class_="is-last-page")
    if tbody:
        rows = tbody.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            if columns and columns[0].get_text(strip=True) == "總計(1~15)":
                total_value = columns[1].get_text(strip=True)
                total_value = total_value.replace(",", "")
                total_billion = round(int(total_value) / 100000000, 1)
                print(f"成交量: {total_billion} 億")
                break
    else:
        print("找不到 tbody")

except Exception as e:
    print(f"發生錯誤: {e}")

finally:
    # 關閉瀏覽器
    driver.quit()
