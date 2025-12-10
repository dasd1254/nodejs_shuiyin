# 1. 使用 Node.js 18 轻量版镜像
FROM node:18-alpine

# 2. 设置工作目录
WORKDIR /app

# 3. 复制依赖清单并安装
# (利用 Docker 缓存机制，先只拷 package.json 加速构建)
COPY package*.json ./
# 安装生产环境依赖 (不装 devDependencies)
RUN npm install --production --registry=https://registry.npmmirror.com

# 4. 复制项目所有代码
COPY . .

# 5. 暴露端口 (通常 Node.js 默认是 3000，如果是其他请修改)
EXPOSE 3000

# 6. 启动命令
# ⚠️ 注意：如果你的入口文件是 app.js，请把 index.js 改成 app.js
CMD ["node", "server.js"]