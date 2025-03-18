# wxChatBot

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Dify](https://img.shields.io/badge/Dify-Powered-purple)
![WeChat](https://img.shields.io/badge/WeChat-Work-brightgreen)
![GPT-SoVITS](https://img.shields.io/badge/GPT--SoVITS-Enabled-red)

</div>

<p align="center">wxChatBot 是一个强大的基于微信的智能聊天机器人，通过集成 Dify AI 平台，提供高效、智能的消息处理和自动回复服务。支持ChatFlow，可自定义编排AI作业任务，原生自带永久记忆功能，支持GPT-SoVITS自定义音色，支持发送微信语音气泡</p>

<div align="center">
  <img src="docs/images/wxchat_demo.jpg" alt="微信聊天演示" width="300" style="display: inline-block; margin: 0 5px;">
  <img src="docs/images/settings_chatflow.jpg" alt="功能展示" width="300" style="display: inline-block; margin: 0 5px;">
  <img src="docs/images/settings_voice.jpg" alt="语音设置界面" width="300" style="display: inline-block; margin: 0 5px;">
  <br>
  <p>微信聊天演示 | ChatFlow功能配置界面 | 语音设置界面</p>
</div>

<img src="docs/images/app_run.png" alt="程序运行日志" width="600">
<p align="center">程序运行日志</p>

## ✨ 功能特性

### 🤖 Dify集成
- 支持Dify的ChatFlow功能


### 📱 微信集成
- 无缝对接企业微信与个人微信
- 支持多种消息类型（文本、语音、图片、文件等）
- 智能处理群聊和私聊消息

### 🔊 语音功能
- 支持语音消息转文本
- 集成语音合成，实现文本到语音转换
- 可配置的语音模型设置

### ⚙️ 系统功能
- 基于Web的管理界面，轻松配置
- 多工作流程和自定义规则支持
- 插件化架构，易于扩展
- 完善的日志记录与监控系统

<div align="center">

<!-- 展示图片位置 -->
<!-- 图片2：功能展示 -->

</div>

## 🚀 快速开始

### 环境要求
- Python 3.11+
- 微信账号(建议使用独立设备运行)
- Dify AI环境
- Ngrok环境(可选，用于内网穿透)

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/wxChatBot.git
cd wxChatBot
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置文件
```bash
# 复制配置模板并修改
cp config.example.json config.json
# 编辑config.json填入必要信息
```

4. 启动服务
```bash
python main.py
```

<div align="center">
<img src="docs/images/app_run.png" alt="配置界面" width="600">
<p>系统启动界面</p>
</div>

## 📁 项目结构

```
wxChatBot/
├── Core/                  # 核心功能模块
│   ├── bridge/            # 通信桥接层
│   ├── commands/          # 命令系统
│   ├── difyAI/            # Dify AI集成
│   ├── factory/           # 服务工厂
│   ├── voice/             # 语音处理模块
│   └── web/               # Web管理界面
├── gewechat/              # 微信API集成
│   ├── api/               # API接口封装
│   ├── util/              # 工具接口层
│   └── data/              # 数据存储
├── voice_model/           # 语音模型文件
├── logs/                  # 日志文件
├── tmp/                   # 临时文件目录
├── config.py              # 配置管理
├── main.py                # 主程序入口
├── config.example.json    # 配置文件示例
└── requirements.txt       # 项目依赖
```

## ⚙️ 配置说明

系统通过`config.json`进行配置，主要配置项包括：

### 基本配置
- `master_name`: 管理员微信昵称
- `debug_mode`: 调试模式开关
- `log_level`: 日志级别(DEBUG/INFO/WARNING/ERROR)
- `server_host`: 服务器主机地址

### 微信配置
- `gewechat_base_url`: Gewechat服务器地址
- `gewechat_token`: 认证令牌
- `gewechat_app_id`: 应用ID
- `gewechat_callback_url`: 回调URL
- `gewechat_download_url`: 文件下载URL

### Dify AI 配置
- `dify_api_base`: Dify API服务器地址

### 高级配置
- `is_remote_server`: 是否为远程服务器
- `ngrok_auth_token`: Ngrok认证Token(内网穿透使用)

详细配置请参考`config.example.json`文件。配置后将其重命名为`config.json`即可使用。

<div align="center">
<img src="docs/images/settings_voice.jpg" alt="系统架构图" width="600">
<p>系统语音设置界面</p>
</div>

##  主要依赖

| 依赖包 | 版本 | 用途 |
|-------|------|------|
| gradio | >=5.21.0 | Web界面框架 |
| web.py | >=0.62 | Web服务框架 |
| requests | >=2.32.3 | HTTP请求库 |
| pyngrok | >=7.2.3 | 内网穿透支持 |
| qrcode | >=7.4.2 | 二维码生成 |
| pilk/pysilk | 最新 | 语音处理支持 |

## 🚀 开发计划

### 近期计划
- [ ] 完善ChatFlow相关功能
- [ ] 优化Web设置界面
- [x] 微信发送语音开关

### 中期计划
- [ ] 支持文档上传及处理
- [ ] 支持视频、图片多媒体处理
- [ ] 支持自定义触发规则

### 长期计划
- [ ] 多平台集成支持
- [ ] AI知识库建设
- [ ] 插件商店

## 🤝 贡献指南

我们欢迎各种形式的贡献，包括但不限于：

- 提交问题和建议
- 改进文档
- 提交代码修复
- 添加新功能

贡献前请先阅读我们的贡献指南，确保代码符合项目规范。

## 📄 许可证

本项目采用 MIT 许可证，查看 [LICENSE](LICENSE) 文件了解更多详细信息。

## 🌟 致谢

感谢以下开源项目的支持：

- [Dify](https://dify.ai) - 提供强大的AI能力支持
- [Gewechat](https://github.com/Devo919/Gewechat) - 微信接口实现
- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) - 语音合成技术支持

---

<p align="center">如果这个项目对您有帮助，请考虑给它一个星标 ⭐️</p>
