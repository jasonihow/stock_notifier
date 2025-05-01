# 使用 Python 官方 image
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements 並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案全部檔案進容器
COPY . .

# 預設執行的 Python 檔案（你可以改成 crawler.py 或 lineV3.py）
CMD ["python", "crawler.py"]
