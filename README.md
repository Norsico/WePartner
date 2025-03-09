# wxChatBot

一个基于 Python 的微信机器人客户端，支持自动化消息处理和管理。

## 🌟 特性

- 支持微信消息的自动化发送和接收
- 灵活的配置管理系统
- 支持 Docker 部署
- 模块化设计，易于扩展
- 完整的日志记录

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Docker (可选，用于容器化部署)

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/your-username/wxChatBot.git
cd wxChatBot
```

2. 创建并激活虚拟环境（推荐）：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

### 配置

1. 复制示例配置文件：
```bash
cp config.json.example config.json
```

2. 编辑 `config.json`，填入必要的配置信息：
```json
{
    "gewechat_base_url": "你的服务器地址",
    "gewechat_app_id": "你的应用ID",
    "gewechat_token": ""  // 留空，程序会自动获取
}
```

### 使用方法

1. 直接运行：
```bash
python main.py
```

2. 使用 Docker 运行：
```bash
docker-compose up -d
```

## 📁 项目结构

```
wxChatBot/
├── Core/               # 核心功能模块
│   ├── bridge/        # 通信桥接模块
│   └── factory/       # 工厂类模块
├── gewechat/          # 微信接口模块
│   ├── api/          # API 接口
│   └── util/         # 工具类
├── config.py          # 配置管理
├── main.py           # 主程序入口
└── docker-compose.yml # Docker 配置文件
```

## 🔧 配置说明

主要配置项说明：

- `gewechat_base_url`: 微信服务器基础URL
- `gewechat_app_id`: 应用ID
- `gewechat_token`: 访问令牌（自动获取）

## 📝 开发说明

- 遵循 PEP 8 编码规范
- 使用模块化设计，便于扩展
- 完整的日志记录系统

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE) 