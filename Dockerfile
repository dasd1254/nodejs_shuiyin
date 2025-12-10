# ============================================================
# 使用基于 Debian 的 Node.js 镜像作为基础
# 相比 Alpine，Debian 对 Python 和 OpenCV 的支持更好，坑更少
# ============================================================
FROM node:18-slim

# 设置工作目录
WORKDIR /app

# ------------------------------------------------------------
# 1. 配置系统环境 (安装 Python 和 OpenCV 依赖库)
# ------------------------------------------------------------
# 替换为阿里云镜像源，加速下载 (针对国内服务器)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 更新软件源并安装必要的系统库
# python3-pip: Python 包管理器
# libgl1-mesa-glx & libglib2.0-0: OpenCV 运行必须依赖的底层图形库
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 2. 安装 Python 项目依赖
# ------------------------------------------------------------
COPY requirements.txt .
# 使用清华源加速 pip 安装
# --break-system-packages 是为了在新版 Debian 中允许全局安装 pip 包
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --break-system-packages

# ------------------------------------------------------------
# 3. 安装 Node.js 项目依赖
# ------------------------------------------------------------
COPY package*.json ./
# 使用淘宝源加速 npm 安装
RUN npm install --production --registry=https://registry.npmmirror.com

# ------------------------------------------------------------
# 4. 复制代码并启动
# ------------------------------------------------------------
# 复制剩下所有的代码 (包括 index.js 和 process.py)
COPY . .

# 确保对外暴露 3001 端口
EXPOSE 3001

# 启动 Node.js 服务
CMD ["node", "index.js"]