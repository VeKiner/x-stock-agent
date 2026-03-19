# 🚀 X-Stock 部署指南

## 方式一：Streamlit Cloud（推荐，免费）

### 步骤 1️⃣：上传代码到 GitHub

```bash
# 进入项目目录
cd /home/gem/workspace/x-stock-agent

# 重命名分支为 main（Streamlit Cloud 默认识别）
git branch -M main

# 创建 GitHub 仓库（手动操作）
# 1. 打开 https://github.com/new
# 2. 仓库名：x-stock-agent
# 3. 可见性：Public（免费部署必须公开）
# 4. 点击 "Create repository"

# 推送代码（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/x-stock-agent.git
git push -u origin main
```

### 步骤 2️⃣：部署到 Streamlit Cloud

1. **打开** https://streamlit.io/cloud
2. **点击** "New app"
3. **选择** 你的 GitHub 仓库 `x-stock-agent`
4. **设置**：
   - Branch: `main`
   - Main file path: `web/app.py`
5. **点击** "Deploy!"

### 步骤 3️⃣：获取访问链接

部署完成后，你会得到类似这样的链接：
```
https://x-stock-agent-web-app-abc123.streamlit.app
```

**🎉 完成！** 现在你可以随时随地访问这个链接查看实时数据。

---

## 方式二：本地运行（开发测试用）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动 Web 看板

```bash
streamlit run web/app.py --server.address=0.0.0.0 --server.port=8501
```

浏览器访问：`http://localhost:8501`

---

## 方式三：云服务器部署（7×24 小时运行）

### 1. 准备云服务器

- 系统：Ubuntu 20.04+
- 配置：1 核 2G 即可（最低）
- 网络：能访问外网（AKShare 数据源）

### 2. 安装 Python 环境

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 使用 PM2 守护进程

```bash
# 安装 PM2
npm install -g pm2

# 启动 Web 看板
pm2 start "streamlit run web/app.py --server.address=0.0.0.0 --server.port=8501" --name xstock-web

# 启动交易引擎
pm2 start "python3 run.py trade" --name xstock-trade

# 查看状态
pm2 status

# 设置开机自启
pm2 startup
pm2 save
```

### 4. 配置 Nginx 反向代理（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## ⚙️ 配置优化

### 修改初始资金

编辑 `config.yaml`：
```yaml
trading:
  initial_capital: 500000  # 改为 50 万
```

### 调整风险参数

```yaml
risk:
  max_position_per_stock: 0.15  # 单票最大 15%
  stop_loss_per_stock: 0.05     # 止损 5%
```

### 启用/禁用策略

```yaml
strategies:
  momentum:
    enabled: true
    weight: 0.4
  mean_reversion:
    enabled: false  # 禁用均值回归
```

---

## 🔧 故障排查

### Web 看板无法访问

```bash
# 检查端口是否占用
netstat -tulpn | grep 8501

# 检查防火墙
sudo ufw allow 8501
```

### 数据获取失败

```bash
# 测试 AKShare 连接
python3 -c "import akshare as ak; print(ak.__version__)"

# 检查网络
curl -I https://www.eastmoney.com/
```

### 内存不足

```bash
# 查看内存使用
free -h

# 添加 Swap（如果只有 1G 内存）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📊 监控与维护

### 查看日志

```bash
# Web 看板日志
tail -f logs/xstock.log

# PM2 日志
pm2 logs xstock-web
```

### 重启服务

```bash
# PM2 方式
pm2 restart xstock-web

# Systemd 方式
sudo systemctl restart xstock
```

### 更新代码

```bash
git pull origin main
pm2 restart all
```

---

## 🎯 下一步

部署完成后：

1. ✅ 访问 Web 看板，确认数据显示正常
2. ✅ 观察 1-2 天，检查数据更新是否及时
3. ✅ 开始运行模拟交易，记录每日收益
4. ✅ 每周回顾策略表现，调整权重

---

<div align="center">

**🦞 祝部署顺利！有问题随时反馈～**

</div>
