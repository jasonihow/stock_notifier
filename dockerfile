FROM python:3.12-slim

# Install curl before running the script
RUN apt-get update && apt-get install -y curl

# 安裝 Chrome 及中文字體
RUN apt-get update && \
    apt-get install -y wget unzip fonts-noto-cjk && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安裝 ChromeDriver（需對應 Chrome 版本）
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | \
    grep -B2 $CHROME_VERSION | grep "version" | head -1 | cut -d '"' -f4) && \
    wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf chromedriver-linux64*

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
