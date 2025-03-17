# wxChatBot

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Dify](https://img.shields.io/badge/Dify-Powered-purple)
![WeChat](https://img.shields.io/badge/WeChat-Work-brightgreen)

</div>

<p align="center">wxChatBot 是一个强大的基于微信的智能聊天机器人，通过集成 Dify AI 平台，提供高效、智能的消息处理和自动回复服务。支持ChatFlow，可自定义编排AI作业任务</p>

## ✨ 功能特性(暂未完善)

### 🤖 智能对话系统
- 集成 Dify AI 平台，支持自然语言处理
- 智能上下文理解和对话管理
- 可定制的对话流程和话术模板

### 📱 微信集成
- 无缝对接企业微信应用
- 支持多种消息类型（文本、图片、文件等）
- 群聊和私聊消息处理

### ⚙️ 系统功能
- 多工作流程配置支持
- 插件化架构设计
- 完善的日志记录系统
- 安全的配置管理机制

### 🔄 自动化能力
- 智能消息分类和路由
- 自定义触发规则
- 灵活的定时任务支持

## 📁 主要项目结构

```
wxChatBot/
├── Core/                  # 核心功能模块
│   ├── bridge/            # 通信桥接层
│   ├── commands/          # 命令系统
│   ├── difyAI/            # difyAI集成
│   ├── factory/           # 通信层工厂
│   └── web/               # 网页端设置
├── gewechat/              # 微信API集成
│   ├── api/               # API接口封装
│   └── util/              # gewechat工具接口层
├── config.py              # 配置管理
├── main.py                # 主程序入口
├── config.example.json    # 配置文件示例
├── requirements.txt       # 项目依赖
└── docker-compose.yml     # Docker部署配置(Gewechat配置)
```

## 🔧 系统要求

### 基础环境
- Python 3.7+
- 个人微信账号(最好是另一部手机上运行的)
- Dify AI环境 
- Ngrok环境

### 推荐配置
- 内存：2GB+
- CPU：双核+
- 存储：10GB+
- 操作系统：Linux/Windows/MacOS

## 📦 主要依赖

| 依赖包 | 版本 | 用途 |
|-------|------|------|
| web.py | >=0.62 | Web服务框架 |
| requests | >=2.26.0 | HTTP请求库 |
| gradio | >=3.50.2 | UI界面支持 |
| pyngrok | >=6.0.0 | 内网穿透支持 |

## ⚙️ 配置说明

系统通过`config.json`进行配置，支持以下主要配置项：

### 微信配置
- 应用ID和Token(自动生成)
- 本地ip地址(可通过ipconfig查看)
- 回调配置(一般不需要修改)

### Dify AI 配置
- API密钥
- 模型选择
- 工作流配置

### 系统配置
- 运行模式
- 日志级别
- 性能参数
- 安全设置

详细配置请参考`config.example.json`文件。配置好后将其修改成`config.json`即可

## 🚀 开发计划

### 近期计划
- [ ] 完善ChatFlow相关功能
- [ ] 完善设置网页页面
- [√] 微信发送语音开关

### 中期计划
- [ ] 支持上传文档
- [ ] 支持上传视频、图片
- [ ] 支持自定义

### 长期计划
- 未知 TAT

## 🤝 贡献指南

我们欢迎各种形式的贡献，包括但不限于：

- 提交问题和建议
- 改进文档
- 提交代码修复
- 添加新功能

请参考我们的贡献指南来了解如何参与项目开发。

## 📄 许可证

本项目采用 MIT 许可证，查看 [LICENSE](LICENSE) 文件了解更多详细信息。

## 🌟 致谢

感谢以下开源项目的支持：

- [Dify](https://dify.ai)
- [Gewechat](https://github.com/Devo919/Gewechat)
- [Ngrok](https://ngrok.com/)

---

<p align="center">如果这个项目对您有帮助，请考虑给它一个星标 ⭐️</p>
