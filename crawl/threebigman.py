from selenium import webdriver
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
options.add_argument("--lang=zh-TW")  # 設置瀏覽器語言為繁體中文
driver = webdriver.Chrome(options=options)

# 開啟網頁
driver.get("https://www.twse.com.tw/zh/trading/foreign/bfi82u.html")

try:
    # 使用顯式等待，直到目標 div 加載完成
    div = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "reports"))
    )

    html = div.get_attribute("outerHTML")
    soup = BeautifulSoup(html, "lxml")

    # 提取日期
    date_element = soup.find("h2", class_="")
    date_str = date_element.find("span").text.strip()
    year, month, day = (
        date_str.replace("年", "/").replace("月", "/").replace("日", "").split("/")
    )
    year = int(year) + 1911  # 轉換民國年為西元年
    formatted_date = f"{year:04d}/{int(month):02d}/{int(day):02d}"
    print(f"日期: {formatted_date}")

    # 提取數據
    tbody = soup.find("tbody", class_="is-last-page")
    if tbody:
        rows = tbody.find_all("tr")
        values = []
        for i, row in enumerate(rows):
            if i in [0, 1, 2, 3]:  # 只取前四行
                columns = row.find_all("td")
                if len(columns) >= 4:
                    value = columns[3].text.strip().replace(",", "")
                    values.append(int(value))

        # 計算並輸出結果（單位：億）
        self_dealer_sum = round((values[0] + values[1]) / 100000000, 2)
        investment_trust = round(values[2] / 100000000, 2)
        foreign_investors = round(values[3] / 100000000, 2)

        print(f"自營商買賣超金額: {self_dealer_sum} 億")
        print(f"投信買賣超金額: {investment_trust} 億")
        print(f"外資買賣超金額: {foreign_investors} 億")
    else:
        print("找不到數據表格")

except Exception as e:
    print(f"發生錯誤: {e}")

finally:
    # 關閉瀏覽器
    driver.quit()
