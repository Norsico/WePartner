# wxChatBot
【暂未整理完成，请期待后续版本~】
<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

- 🤖 智能对话：基于Dify API的智能对话系统
- 📝 自动回复：可配置的自动回复功能
- 📁 文件处理：支持多种类型文件的处理和分析
- 🖼️ 图片分析：支持图片识别和分析
- 🔄 工作流系统：灵活的工作流配置和管理
- ⚙️ 可视化配置：提供Web界面进行配置管理
- 📊 日志系统：完善的日志记录和管理

> 一个基于 Python 的微信机器人客户端，支持自动化消息处理和管理。

## ✨ 功能特性

- 🔄 **自动化消息处理**：支持微信消息的自动发送和接收
- ⚙️ **灵活配置**：完善的配置管理系统
- 🧩 **模块化设计**：易于扩展的架构
- 📊 **完整日志**：详细的运行日志记录
- 🔌 **API集成**：与第三方服务无缝集成

## 📋 项目结构

```
wxChatBot/
├── Core/                # 核心功能模块
│   ├── bridge/         # 通信桥接模块
│   ├── factory/        # 工厂类模块
│   ├── DifyAI/         # Dify AI 集成
│   ├── WxClient.py     # 微信客户端实现
│   └── Logger.py       # 日志系统
├── gewechat/            # 微信接口模块（第三方开源项目）
│   ├── api/            # API 接口
│   ├── util/           # 工具类
│   └── data/           # 数据存储
├── config.py            # 配置管理
├── main.py              # 主程序入口
├── config.json          # 配置文件
└── docker-compose.yml   # gewechat的Docker配置文件
```

## 🚀 快速开始

### 环境要求

- Python 3.9+
- gewechat 服务（可通过Docker部署）

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/your-username/wxChatBot.git
cd wxChatBot
```

#### 2. 创建并激活虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# Windows 激活
venv\Scripts\activate

# Linux/Mac 激活
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 配置说明

#### 1. 配置文件

复制示例配置文件并编辑：

```bash
cp config.json.example config.json
```

编辑 `config.json`，填入必要的配置信息：

```json
{
  "gewechat_base_url": "http://your-server:2531/v2/api",
  "gewechat_app_id": "your-app-id",
  "gewechat_token": "",  // 留空，程序会自动获取
  "gewechat_callback_url": "http://your-server:1145/v2/api/callback/collect",
  "gewechat_download_url": "http://your-server:2532/download"
}
```

#### 2. 部署 gewechat 服务

本项目依赖于 gewechat 服务，需要先部署 gewechat：

```bash
# 启动 gewechat 服务
docker-compose up -d
```

> **注意**：docker-compose.yml 中配置的是 gewechat 服务，而非本项目的容器化配置。

## 💻 使用方法

### 启动服务

```bash
python main.py
```

### 示例代码

```python
from Core.WxClient import WxChatClient
from config import Config

# 创建配置
config = Config('./config.json')

# 创建WxChatClient
wx_client = WxChatClient(config)

# 发送文本消息
wx_client.send_text_message_by_name("好友昵称", "Hello, World!")
```

## 🔧 高级配置

### 主要配置项

| 配置项 | 说明 | 示例 |
|-------|------|------|
| `gewechat_base_url` | gewechat服务的API基础URL | `http://localhost:2531/v2/api` |
| `gewechat_app_id` | 应用ID | `wx_usXP_BDz8cmVGlBi6WDJQ` |
| `gewechat_token` | 访问令牌（可留空自动获取） | - |
| `gewechat_callback_url` | 回调URL | `http://localhost:1145/v2/api/callback/collect` |
| `gewechat_download_url` | 文件下载URL | `http://localhost:2532/download` |

## 📝 开发指南

### 代码规范

- 遵循 PEP 8 编码规范
- 使用类型注解提高代码可读性
- 编写详细的文档注释

### 模块扩展

1. 在 `Core` 目录下创建新模块
2. 实现相应的接口
3. 在 `main.py` 中集成新模块

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🙏 致谢

- [gewechat](https://github.com/path/to/gewechat) - 提供微信通信接口
- 所有贡献者和使用者 
