FROM mcr.microsoft.com/playwright/python:latest

WORKDIR /app

# 拷贝依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝应用代码
COPY app.py .

# 安装浏览器驱动
RUN playwright install

CMD ["python", "app.py"]
