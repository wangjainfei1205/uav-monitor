# 无人机智能化应用系统

基于Streamlit开发的无人机智能化应用系统，包含航线规划、飞行监控、心跳检测和坐标转换功能。

## 功能特性

### 🗺️ 航线规划
- 3D地图展示（高德地图）
- A/B点坐标设置
- 障碍物标记
- 航线距离计算
- 自动2D/3D切换

### 🚁 飞行监控
- 心跳包实时监控
- 掉线检测报警（3秒阈值）
- 电池电量监控
- 飞行姿态显示
- 导航日志记录

### 🔄 坐标转换
- WGS-84 ↔ GCJ-02 双向转换
- WGS-84 ↔ BD-09 双向转换
- 批量转换支持
- 历史记录导出

## 技术栈

- **前端框架**: Streamlit
- **数据可视化**: Plotly
- **地图服务**: 高德地图API
- **编程语言**: Python 3.8+

## 本地运行

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/uav-monitor.git
cd uav-monitor
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
streamlit run app.py
```

## 部署到Streamlit Cloud

### 1. 推送代码到GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. 在Streamlit Cloud部署

1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 使用GitHub账号登录
3. 点击 "New app"
4. 选择仓库和分支
5. 设置主文件路径为 `app.py`
6. 点击 "Deploy"

## 配置说明

### 高德地图API Key

在航线规划页面输入您的高德地图Web JS API Key。

申请地址: [高德开放平台](https://lbs.amap.com/)

## 项目结构

```
uav_monitor/
├── app.py                    # 主应用入口
├── heartbeat.py              # 心跳包模拟模块
├── coordinate_converter.py   # 坐标转换模块
├── route_planning.py         # 航线规划页面
├── flight_monitor.py         # 飞行监控页面
├── coord_converter_page.py   # 坐标转换页面
├── requirements.txt          # 依赖列表
└── .streamlit/
    └── config.toml           # Streamlit配置
```

## 许可证

MIT License

---

© 2024 南京科技职业学院 | 无人机智能化应用项目
