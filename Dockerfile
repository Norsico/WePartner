FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建tmp目录
RUN mkdir -p tmp

# 暴露端口 (根据应用需要调整)
EXPOSE 7860

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 启动应用
CMD ["python", "main.py"] 