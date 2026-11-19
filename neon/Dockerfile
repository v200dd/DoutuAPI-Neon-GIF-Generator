# 使用官方轻量级 Python 3.11 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 1. 中文字体已随源码提供，避免额外下载 56.7 MB 的 fonts-noto-cjk。

# 2. 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 复制项目代码
COPY . .

# 4. 构建时确认运行所需的中文字体存在。
RUN test -s fonts/jiying.ttf

# 5. 暴露端口
EXPOSE 8000

# 6. 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
