FROM python:3.12-slim

# 安裝 Chrome 及中文字體
RUN apt-get update && \
    apt-get install -y wget unzip fonts-noto-cjk && \
    wget https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.49/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip -d /opt && \
    rm chrome-linux64.zip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安裝 ChromeDriver（固定版本）
RUN wget https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.49/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip

# 設定環境變數
ENV PATH="/usr/bin/chromedriver:$PATH"
ENV DISPLAY=:99

# 複製程式碼
WORKDIR /app
COPY . .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 預設執行爬蟲
CMD ["python", "crawler.py"]
