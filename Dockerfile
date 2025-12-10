# ============================================================
# 【核心修改】使用 node:18-bullseye-slim
# 解释：Bullseye 是 Debian 11，自带 Python 3.9 (AI 库兼容性最好)
# 之前的 slim 是 Debian 12，自带 Python 3.11 (容易报错)
# ============================================================
FROM node:18-bullseye-slim

WORKDIR /app

# 1. 换源并安装系统依赖
# 注意：Bullseye 的源配置稍微有点不一样，这里用了通用的清华源配置
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

# 2. 升级 pip (防止 pip 版本太老找不到包)
RUN python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 安装 Python 依赖 (PaddleOCR)
COPY requirements.txt .
# 去掉了 --break-system-packages 参数，因为 Python 3.9 不需要它
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 预下载 PaddleOCR 模型 (可选，防止运行时卡顿)
RUN python3 -c "from paddleocr import PaddleOCR; PaddleOCR(lang='ch', show_log=False)"

# 5. 安装 Node 依赖
COPY package*.json ./
RUN npm install --production --registry=https://registry.npmmirror.com

# 6. 复制代码
COPY . .

EXPOSE 3001
CMD ["node", "server.js"]