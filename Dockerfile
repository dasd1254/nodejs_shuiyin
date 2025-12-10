# 使用 node:18-bullseye-slim (Python 3.9)
FROM node:18-bullseye-slim

WORKDIR /app

# 1. 换源并安装系统依赖
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. 升级 pip
RUN python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 安装 Python 依赖
COPY requirements.txt .
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 【关键修改】预下载模型 (去掉了 show_log=False)
RUN python3 -c "from paddleocr import PaddleOCR; PaddleOCR(lang='ch')"

# 5. 安装 Node 依赖
COPY package*.json ./
RUN npm install --production --registry=https://registry.npmmirror.com

# 6. 复制代码
COPY . .

EXPOSE 3001
CMD ["node", "server.js"]