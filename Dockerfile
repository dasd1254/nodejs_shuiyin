# 依然使用 Node.js + Debian 基础
FROM node:18-slim

WORKDIR /app

# 1. 换源并安装系统依赖
# 新增了 libgomp1 (PaddlePaddle 需要)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. 安装 Python 依赖 (PaddleOCR)
# 这步会比较慢，因为包比较大
COPY requirements.txt .
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --break-system-packages

# 3. 预下载 PaddleOCR 模型 (可选，但推荐)
# 这样容器启动时不需要现场下载，防止网络超时
# 运行一次空识别来触发下载
RUN python3 -c "from paddleocr import PaddleOCR; PaddleOCR(lang='ch', show_log=False)"

# 4. 安装 Node 依赖
COPY package*.json ./
RUN npm install --production --registry=https://registry.npmmirror.com

# 5. 复制代码
COPY . .

EXPOSE 3001
CMD ["node", "server.js"]