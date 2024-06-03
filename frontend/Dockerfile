# 安装Node.js
FROM node:latest

# 创建工作目录
WORKDIR /app

# 将node_modules添加到工作目录
COPY package.json .
RUN npm install 
RUN npm install -g vite@4.4.9

# 将所有文件复制到工作目录
COPY . .

# 配置环境变量
ENV VITE_BACKEND_ENDPOINT=http://47.243.180.140:5000

# 编译前端项目
RUN npm run build

# 产生静态文件
FROM nginx:stable-alpine
COPY --from=0 /app/dist /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/
