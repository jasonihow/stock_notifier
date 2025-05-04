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
import requests  # 添加這行
import json
import time

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    ImageMessage,
    PushMessageRequest,
)
import argparse
from datetime import datetime, timedelta


# 設置控制台輸出編碼為UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# Line Messaging API settings
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
USER_ID = os.environ.get("LINE_USER_ID")

# 更新 LINE Bot API 初始化
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_argument("--lang=zh-TW")
    return webdriver.Chrome(options=options)


def get_volume(target_date):
    target_date = target_date.replace("/", "")
    url = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={target_date}&type=MS&response=json&_=1729853427943"

    # 設定請求標頭
    # headers = {
    #     "Accept": "application/json, text/javascript, */*; q=0.01",
    #     "Accept-Encoding": "gzip, deflate, br, zstd",
    #     "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    #     "Connection": "keep-alive",
    #     "Referer": "https://www.twse.com.tw/zh/trading/historical/mi-index.html",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    #     "X-Requested-With": "XMLHttpRequest",
    # }

    # 發送 GET 請求
    response = requests.get(url)

    # 檢查請求是否成功
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            response.encoding = "utf-8"  # 優先嘗試 UTF-8 解碼
            data = response.text
            json_data = json.loads(data)
            volume = json_data["tables"][6]["data"][16][1].replace(",", "")
            volume = round(int(volume) / 100000000, 1)
            return volume
        except UnicodeDecodeError as e_utf8:
            print(f"UTF-8 解碼失敗: {e_utf8}")
            print(f"嘗試使用 big5 解碼...")
            try:
                data_big5 = response.content.decode("big5")
                json_data_big5 = json.loads(data_big5)
                volume = json_data_big5["tables"][6]["data"][16][1].replace(",", "")
                volume = round(int(volume) / 100000000, 1)
                return volume
            except (UnicodeDecodeError, json.JSONDecodeError) as e_big5:
                print(f"嘗試 big5 解碼也失敗: {e_big5}")
                print(f"原始回應內容 (byte): {response.content[:200]}...")
        except json.JSONDecodeError as e_json:
            print(f"JSON 解析失敗: {e_json}")
            print(f"原始回應內容 (UTF-8 解碼後 - 部分): {response.text[:200]}...")
    else:
        print(f"請求失敗，狀態碼: {response.status_code}")
        return None


def get_three_big_man(target_date):
    target_date = target_date.replace("/", "")
    url = f"https://www.twse.com.tw/rwd/zh/fund/BFI82U?type=day&dayDate={target_date}&response=json&_=1729856960636"

    # 設定請求標頭
    # headers = {
    #     "Accept": "application/json, text/javascript, */*; q=0.01",
    #     "Accept-Encoding": "gzip, deflate, br, zstd",
    #     "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    #     "Connection": "keep-alive",
    #     "Referer": "https://www.twse.com.tw/zh/trading/historical/mi-index.html",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    #     "X-Requested-With": "XMLHttpRequest",
    # }

    # 發送 GET 請求
    response = requests.get(url)

    # 檢查請求是否成功
    if response.status_code == 200:
        # 解析資料
        # 嘗試用不同的編碼進行解碼
        try:
            # 假設資料是以 big5 編碼
            data = response.content.decode("UTF-8")
            # 由於原始資料是以某種結構化方式返回，嘗試將其轉換為字典

            json_data = json.loads(data)
            a = json_data["data"][0][3].replace(",", "")
            b = json_data["data"][1][3].replace(",", "")
            self_dealer_sum = f"{round((int(a) + int(b)) / 100000000, 1)}"
            investment_trust = (
                f"{round(int(json_data['data'][2][3].replace(',', '')) / 100000000, 1)}"
            )
            foreign_investors = (
                f"{round(int(json_data['data'][3][3].replace(',', '')) / 100000000, 1)}"
            )

            return foreign_investors, investment_trust, self_dealer_sum
            # 顯示解析後的資料

        except Exception as e:
            print(f"資料解析失敗: {e}")
    else:
        print(f"請求失敗，狀態碼: {response.status_code}")


def get_future_empty_and_little_furture_empty(driver, target_date):
    driver.get("https://www.taifex.com.tw/cht/3/futContractsDate")
    # 使用顯式等待到側邊欄加載完成
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_right"))
    )

    # 等待日期輸入框可用
    input_element = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "queryDate"))
    )
    input_element.clear()
    input_element.send_keys(target_date)

    # 增加等待時間以確保選擇生效
    time.sleep(3)

    # 找到並點擊 "送出查詢" 按鈕
    submit_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.btn_orange#button"))
    )

    # 使用 JavaScript 點擊按鈕
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    driver.execute_script("arguments[0].click();", submit_button)

    div = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "printhere"))
    )

    html = div.get_attribute("outerHTML")
    soup = BeautifulSoup(html, "lxml")

    tbody = soup.find("tbody")

    nums = []
    if tbody:
        # 提取每一行的數據
        rows = tbody.find_all("tr")
        for row in range(len(rows)):
            if row == 2 or row == 10 or row == 11:
                columns = rows[row].find_all("td")
                if len(columns) > 12:  # 確保有足夠的欄位
                    num = columns[11].text.split("\n")
                    want = num[1].replace(",", "")
                    nums.append(want[1:])
                else:
                    print(f"Row {row} does not have enough columns.")
            if row == 9:
                columns = rows[row].find_all("td")
                if len(columns) > 12:  # 確保有足夠的欄位
                    num = columns[13].text.split("\n")
                    want = num[1].replace(",", "")
                    nums.append(want[1:])
                else:
                    print(f"Row {row} does not have enough columns.")

        empty = round(int(nums[0]) + int(nums[3]) / 4)
        little_future_empty = f"{int(nums[1]) + int(nums[2]) + int(nums[3])}"

        return empty, little_future_empty
    else:
        print("找不到 tbody")


def get_top510(driver, target_date):
    driver.get("https://www.taifex.com.tw/cht/3/largeTraderFutQryTbl")

    # 使用顯式等待，直到目標元素加載完成
    WebDriverWait(driver, 30).until(
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

    return top5, top10


def get_choice(driver, target_date):
    driver.get("https://www.taifex.com.tw/cht/3/callsAndPutsDate")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_right"))
    )

    # 等待日期輸入框可用
    input_element = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "queryDate"))
    )
    input_element.clear()
    input_element.send_keys(target_date)

    # 增加待時間以確保選擇生效
    time.sleep(5)

    # 找到並點擊 "送出查詢" 按鈕
    submit_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.btn_orange#button"))
    )

    # 使用 JavaScript 點擊按鈕
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    driver.execute_script("arguments[0].click();", submit_button)

    # 等待頁面加載新數據
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tbody"))
    )

    soup = BeautifulSoup(driver.page_source, "lxml")

    tbody = soup.find("tbody")
    if tbody:
        rows = tbody.find_all("tr")
        nums = [
            int(row.find_all("td")[12].text.replace(",", "").strip())
            for row in [rows[2], rows[5]]
            if len(row.find_all("td")) > 11
        ]

        if len(nums) == 2:
            result = f"{round((nums[0] - nums[1]) / 10, 1)}"
            return result
        else:
            print("無法計算結果：數據不完整")
    else:
        print("找不到 tbody")


def get_pcr(driver, target_date):
    driver.get("https://www.taifex.com.tw/cht/3/pcRatio")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_right"))
    )

    # 等待日期輸入框可用
    input_element = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "queryStartDate"))
    )
    input_element.clear()
    input_element.send_keys(target_date)

    input_element = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "queryEndDate"))
    )
    input_element.clear()
    input_element.send_keys(target_date)

    # 增加等待時間以確保選擇生效
    time.sleep(3)

    # 找到並點擊 "送出查詢" 按鈕
    submit_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.btn_gray#button4"))
    )

    # 使用 JavaScript 點擊按鈕
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    driver.execute_script("arguments[0].click();", submit_button)

    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "lxml")
    tbody = soup.find("tbody")
    if tbody:
        row = tbody.find("tr")
        columns = row.find_all("td")
        return float(columns[-1].text.strip())


def get_little_tai(driver, target_date):
    driver.get("https://www.taifex.com.tw/cht/3/futDailyMarketReport")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar_right"))
    )

    # 等待日期輸入框可用
    input_element = WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.ID, "queryDate"))
    )
    input_element.clear()
    input_element.send_keys(target_date)

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
    target_td = soup.find_all(
        "td", {"align": "right", "style": "background-color:#ecf2f9", "class": "12bk"}
    )
    target_td = target_td[3]
    if target_td:
        value = target_td.text.strip()
        return value
    else:
        print("無法找到小台全體未平倉")


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
                    "十大交易人留倉",
                    "外資選擇權",
                    "選擇權PCR",
                    "韭菜指數",
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
    plt.rcParams["font.sans-serif"] = [
        "Noto Sans CJK TC",
        "Noto Sans CJK JP",
        "Noto Sans CJK KR",
        "Noto Sans CJK SC",
        "sans-serif",
        # 優先使用 Noto Sans CJK
        "WenQuanYi Micro Hei",  # 或者使用 WenQuanYi Micro Hei
        "Microsoft YaHei",  # 或者使用 Microsoft YaHei
        "SimHei",  # 或者使用 SimHei
    ]
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

    # 為負數和小於100的選擇權PCR設置紅色
    for (row, col), cell in table.get_celld().items():
        if row != 0:  # 跳過標題行
            try:
                value = float(cell.get_text().get_text())
                # 檢查選擇權PCR列（假設選擇權PCR在第9列）
                if value < 0 or (col == 8 and value < 100):  # 確保列索引正確
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
        imgur_client_id = os.environ.get("IMGUR_CLIENT_ID")
        if not imgur_client_id:
            raise ValueError("IMGUR_CLIENT_ID 環境變量未設置")

        headers = {"Authorization": f"Client-ID {imgur_client_id}"}
        files = {"image": ("image.png", image_buffer, "image/png")}
        response = requests.post(
            "https://api.imgur.com/3/image", headers=headers, files=files
        )
        response.raise_for_status()  # 如果請求失敗，這將引發異常

        response_data = response.json()
        print(f"Imgur API 響應: {response_data}")  # 添加這行來查看完整的響應

        if "data" not in response_data or "link" not in response_data["data"]:
            raise ValueError(f"Imgur API 響應中缺少預期的數據: {response_data}")

        image_url = response_data["data"]["link"]

        # 發送圖片消息
        message = ImageMessage(
            original_content_url=image_url, preview_image_url=image_url
        )
        request = PushMessageRequest(to=USER_ID, messages=[message])
        line_bot_api.push_message(request)
        print("圖片已成功發送到 Line")
    except requests.RequestException as e:
        print(f"上傳圖片到 Imgur 時發生網絡錯誤: {str(e)}")
    except ValueError as e:
        print(f"處 Imgur 響應時發生錯誤: {str(e)}")
    except Exception as e:
        print(f"發送 Line 圖片時發生未知錯誤: {str(e)}")


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
選擇權PCR: {data[9]}
外資選擇權: {data[8]}
韭菜指數: {data[10]}
"""


def main(target_date=None):
    driver = setup_driver()
    try:
        print(target_date)
        volume = get_volume(target_date)
        print(f"成交量: {volume}億")

        foreign_investors, investment_trust, self_dealer = get_three_big_man(
            target_date
        )

        print(f"外資: {foreign_investors}億")
        print(f"投信: {investment_trust}億")
        print(f"自營商: {self_dealer}億")
        future_empty, small_future_empty = get_future_empty_and_little_furture_empty(
            driver, target_date
        )  # 獲取兩個值
        print(f"外資期貨未平倉: {future_empty}億")
        top5, top10 = get_top510(driver, target_date)
        print(f"前五大交易人留倉: {top5}")
        choice = get_choice(driver, target_date)
        print(f"選擇權: {choice}億")
        pcr = get_pcr(driver, target_date)
        print(f"PCR: {pcr}")
        little_tai = get_little_tai(driver, target_date)
        print(f"韭菜指數: {little_tai}億")

        # 計算韭菜指數
        chive_index = (
            round(-int(small_future_empty) / int(little_tai) * 100, 2)
            if little_tai
            else None
        )

        # 格式化數據
        data = [
            target_date,
            f"{volume}億",
            foreign_investors,
            investment_trust,
            self_dealer,
            future_empty,  # 外資期貨未平倉
            top5,
            top10,
            f"{round(pcr, 1)}",  # 選擇權PCR進位到小數點後一位
            f"{round(float(choice), 0)}",  # 外資選擇權進位到個位數
            f"{chive_index}%",  # 韭菜指數
        ]

        check_and_write_data(target_date, data)

        # 創建表格圖片
        image_buffer = create_table_image("market_data.csv")

        # 發送圖片到 Line
        send_line_image(image_buffer)

    except Exception as e:
        error_message = f"發生錯誤: {str(e)}"
        print(error_message)
        message = TextMessage(text=error_message)
        request = PushMessageRequest(to=USER_ID, messages=[message])
        line_bot_api.push_message(request)
    finally:
        driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="抓取特定日期的市場數據")

    # 獲取當前日期作為默認值
    default_date = datetime.now().strftime("%Y/%m/%d")

    parser.add_argument(
        "--date", type=str, help="指定日期 (格式: YYYY/MM/DD)", default=default_date
    )
    args = parser.parse_args()

    try:
        target_date = datetime.strptime(args.date, "%Y/%m/%d")
        # 檢查是否為工作日（週一到週五）
        if target_date.weekday() >= 5:
            # 如果是週末，將日期調整為上一個工作日
            days_to_subtract = 1 if target_date.weekday() == 5 else 2
            target_date -= timedelta(days=days_to_subtract)
            print(
                f"指定日期為週末，已自動調整為上一個工作日: {target_date.strftime('%Y/%m/%d')}"
            )

        main(target_date.strftime("%Y/%m/%d"))
    except ValueError:
        print("日期格式錯誤，請使用 YYYY/MM/DD 格式")
        exit(1)
