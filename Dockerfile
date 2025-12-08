# 使用 Node 18 的轻量版镜像
FROM node:18-alpine

# 设置工作目录
WORKDIR /app

# 先复制 package.json 安装依赖（利用缓存机制加速）
COPY package.json .
# 如果有 package-lock.json 也可以在这里 copy
# 使用淘宝源加速安装
RUN npm install --registry=https://registry.npmmirror.com

# 复制所有源代码
COPY . .

# 暴露 3000 端口
EXPOSE 3000

# 启动服务
CMD ["node", "server.js"]