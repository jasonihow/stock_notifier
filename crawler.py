import csv
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sys
import re
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage
import requests
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_USER_ID, IMGUR_CLIENT_ID

# 設置控制台輸出編碼為UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# Line Messaging API settings
# CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
# USER_ID = os.environ.get("LINE_USER_ID")

# 使用從 config.py 導入的變量
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_argument("--lang=zh-TW")
    return webdriver.Chrome(options=options)


def get_volume_and_date(driver):
    driver.get("https://www.twse.com.tw/zh/trading/historical/mi-index.html")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "reports")))
    soup = BeautifulSoup(driver.page_source, "lxml")

    # 提取日期
    time_element = soup.find("div", id="table6")
    date_str = time_element.find("hgroup").text.split(" ")[0][1:]
    year, month, day = (
        date_str.replace("年", "/").replace("月", "/").replace("日", "").split("/")
    )
    year = int(year) + 1911  # 轉換民國年為西元年
    date = f"{year:04d}/{int(month):02d}/{int(day):02d}"

    # 提取成交量
    tbody = soup.find("tbody", class_="is-last-page")
    volume = None
    if tbody:
        rows = tbody.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            if columns and columns[0].get_text(strip=True) == "總計(1~15)":
                total_value = columns[1].get_text(strip=True)
                total_value = total_value.replace(",", "")
                volume = round(int(total_value) / 100000000, 1)
                break

    return date, volume


def get_three_big_man(driver):
    driver.get("https://www.twse.com.tw/zh/trading/foreign/bfi82u.html")
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "reports"))
    )
    soup = BeautifulSoup(driver.page_source, "lxml")
    tbody = soup.find("tbody", class_="is-last-page")
    if tbody:
        rows = tbody.find_all("tr")
        values = [
            int(rows[i].find_all("td")[3].text.replace(",", "")) for i in [0, 1, 2, 3]
        ]
        foreign_investors = round(values[3] / 100000000, 2)
        investment_trust = round(values[2] / 100000000, 2)
        self_dealer_sum = round((values[0] + values[1]) / 100000000, 2)
        return foreign_investors, investment_trust, self_dealer_sum
    return None, None, None


def get_future_empty(driver):
    driver.get("https://www.taifex.com.tw/cht/3/futContractsDate")
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "printhere"))
    )
    soup = BeautifulSoup(driver.page_source, "lxml")
    tbody = soup.find("tbody")
    if tbody:
        rows = tbody.find_all("tr")
        nums = [
            int(rows[i].find_all("td")[11].text.split("\n")[1].replace(",", "")[1:])
            for i in [2, 11]
        ]
        return round(nums[0] + nums[1] / 4), nums[1]
    return None


def get_top510(driver):
    driver.get("https://www.taifex.com.tw/cht/3/largeTraderFutQryTbl")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_middle"))
    )
    soup = BeautifulSoup(driver.page_source, "lxml")
    tbody = soup.select("tbody")[1]
    row = tbody.select("tr")[2]
    columns = row.select("td")

    def extract_number(text):
        match = re.search(r"-?\d+", text.replace(",", ""))
        return int(match.group()) if match else 0

    nums = [extract_number(columns[i].text) for i in [1, 3, 5, 7]]
    top5 = nums[0] - nums[2]
    top10 = nums[1] - nums[3]
    return top5, top10


def get_choice(driver):
    driver.get("https://www.taifex.com.tw/cht/3/callsAndPutsDate")
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "printhere"))
    )
    soup = BeautifulSoup(driver.page_source, "lxml")
    tbody = soup.find("tbody")
    if tbody:
        rows = tbody.find_all("tr")
        nums = [
            int(row.find_all("td")[11].text.replace(",", "").strip())
            for row in [rows[2], rows[5]]
        ]
        return nums[0] - nums[1]
    return None


def get_pcr(driver):
    driver.get("https://www.taifex.com.tw/cht/3/pcRatio")
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "printhere"))
    )
    soup = BeautifulSoup(driver.page_source, "lxml")
    tbody = soup.find("tbody")
    if tbody:
        row = tbody.find("tr")
        columns = row.find_all("td")
        if len(columns) >= 2:
            return float(columns[-1].text.strip())
    return None


def get_little_tai(driver):
    driver.get("https://www.taifex.com.tw/cht/3/futDailyMarketExcel?commodity_id=MTX")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_middle"))
    )
    soup = BeautifulSoup(driver.page_source, "lxml")
    target_td = soup.find(
        "td", {"align": "right", "bgcolor": "#ecf2f9", "class": "12bk"}
    )
    return int(target_td.text.strip()) if target_td else None


def check_and_write_data(date, data):
    file_path = "market_data.csv"
    file_exists = os.path.isfile(file_path)

    # 如果文件不存在，直接寫入數據
    if not file_exists:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "日期",
                    "成交量",
                    "外資",
                    "投信",
                    "自營商",
                    "外資期貨未平倉",
                    "前五大交易人留倉",
                    "前十大交易人留倉",
                    "外資選擇權",
                    "選擇權PCR",
                    "小台全體未平倉量",
                ]
            )
            writer.writerow(data)
        print(f"數據已成功記錄到 {file_path}")
        return

    # 如果文件存在，檢查是否已有相同日期的記錄
    with open(file_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        existing_dates = [row[0] for row in reader if row]  # 獲取所有已存在的日期

    if date in existing_dates:
        print(f"日期 {date} 的數據已存在，不進行重複記錄。")
        return

    # 如果沒有相同日期的記錄，追加新數據
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(data)
    print(f"數據已成功記錄到 {file_path}")


def create_table_image(file_path):
    # 讀取CSV文件
    df = pd.read_csv(file_path)

    # 只保留最近10天的數據
    df = df.tail(10)

    # 設置中文字體
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    # 創建圖表
    fig, ax = plt.subplots(figsize=(15, 8))  # 增加圖表大小
    ax.axis("off")

    # 創建表格
    table = ax.table(
        cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center"
    )

    # 調整表格樣式
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.5)

    # 為負數設置紅色
    for (row, col), cell in table.get_celld().items():
        if row != 0:  # 跳過標題行
            try:
                value = float(cell.get_text().get_text())
                if value < 0:
                    cell.set_text_props(color="red")
            except ValueError:
                pass  # 如果無法轉換為浮點數，就跳過

    # 保存圖片到內存
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    plt.close()

    return buf


def send_line_image(image_buffer):
    try:
        # 將圖片上傳到某個圖片託管服務（這裡使用 imgur 作為示例）
        headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
        files = {"image": ("image.png", image_buffer, "image/png")}
        response = requests.post(
            "https://api.imgur.com/3/image", headers=headers, files=files
        )
        image_url = response.json()["data"]["link"]

        # 發送圖片消息
        line_bot_api.push_message(
            LINE_USER_ID,
            ImageSendMessage(
                original_content_url=image_url, preview_image_url=image_url
            ),
        )
        print("圖片已成功發送到 Line")
    except Exception as e:
        print(f"發送 Line 圖片時發生錯誤: {e}")


def format_data_message(data):
    return f"""
日期: {data[0]}
成交量: {data[1]}
外資: {data[2]}
投信: {data[3]}
自營商: {data[4]}
外資期貨未平倉: {data[5]}
前五大交易人留倉: {data[6]}
前十大交易人留倉: {data[7]}
外資選擇權: {data[8]}
選擇權PCR: {data[9]}
小台全體未平倉量: {data[10]}
"""


def main():
    driver = setup_driver()
    try:
        date, volume = get_volume_and_date(driver)
        foreign_investors, investment_trust, self_dealer = get_three_big_man(driver)
        future_empty = get_future_empty(driver)
        top5, top10 = get_top510(driver)
        choice = get_choice(driver)
        pcr = get_pcr(driver)
        little_tai = get_little_tai(driver)

        data = [
            date,
            volume,
            foreign_investors,
            investment_trust,
            self_dealer,
            future_empty,
            top5,
            top10,
            choice,
            pcr,
            little_tai,
        ]

        check_and_write_data(date, data)

        # 創建表格圖片
        image_buffer = create_table_image("market_data.csv")

        # 發送圖片到 Line
        send_line_image(image_buffer)

    except Exception as e:
        error_message = f"發生錯誤: {e}"
        print(error_message)
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=error_message))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
