# wxChatBot

<div align="center">
  <a href="README.md">中文</a> | 
  <a href="../en/README.md">English</a>
</div>

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Dify](https://img.shields.io/badge/Dify-Powered-purple)
![WeChat](https://img.shields.io/badge/WeChat-Work-brightgreen)
![GPT-SoVITS](https://img.shields.io/badge/GPT--SoVITS-Enabled-red)

</div>

<p align="center">wxChatBot 是一个强大的基于Dify和Gewechat的智能聊天机器人。通过集成 Dify AI 平台，提供高效、智能的消息处理和自动回复服务。支持ChatFlow，可自定义编排AI作业任务，原生自带永久记忆功能，支持GPT-SoVITS自定义音色，支持发送微信语音气泡</p>

<div align="center" style="display: flex; justify-content: center; flex-wrap: nowrap; gap: 5px; max-width: 100%; overflow-x: auto;">
  <img src="docs/images/wxchat_demo.jpg" alt="微信聊天演示" width="32%" style="max-width: 32%;">
  <img src="docs/images/settings_chatflow.jpg" alt="功能展示" width="32%" style="max-width: 32%;">
  <img src="docs/images/settings_voice.jpg" alt="语音设置界面" width="32%" style="max-width: 32%;">
</div>
<p align="center">微信聊天演示 | ChatFlow功能配置界面 | 语音设置界面</p>


## ✨ 功能特性

### 🤖 Dify集成
- 支持Dify的ChatFlow功能，提供从Agent构建到AI workflow编排、RAG检索、模型管理等能力
- 轻松构建和运营生成式AI原生应用，理论上Dify支持的功能都能集成到本项目
- 原生支持永久记忆和本地知识库检索
- 支持自定义插件、自定义函数调用等扩展功能

### 📱 微信集成
- 无缝对接个人微信，轻松接入现有微信生态
- 支持文本、语音回复（原生语音泡，非文件形式）
- 支持群聊和私聊消息智能处理
- 可通过简单指令（如发送`#设置`）获取管理界面

### 🔊 语音功能
- 基于GPT-SoVITS技术，可自定义语音模型
- 仅需极少量语音数据即可高度还原声音特征
- 支持语音消息转文本和文本合成语音
- 可配置多种语音参数，实现个性化语音体验

### ⚙️ 系统功能
- 使用Gradio开发Web管理界面，实现轻松配置
- 使用Gradio的share=True模式，无需公网IP即可远程访问配置界面
- 插件化架构，易于扩展和二次开发
- 完善的日志记录与监控系统

## 🚀 快速开始

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

### 环境要求
- Python 3.11+
- 一个绑定了本人身份证的微信账号(最好还开通了钱包，里面放1块钱，建议使用独立设备运行)
- Dify AI环境
- Gewechat的Docker 环境

### 视频教程
- 在做了，在做了

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


## ⚙️ 配置说明

初次运行，请修改`config.json`，主要配置项包括：

```json
{
    "master_name": "N", // 你大号的微信的名称(注意不是备注，是账号名称，最好别重名)
    "dify_api_base": "http://localhost/v1", // dify的baseurl,一般不需要改
    "gewechat_base_url": "http://your_local_ip:2531/v2/api", // gewechat的baseurl,把your_local_ip改成你的电脑IPv4地址,下面同理
    "gewechat_token": "", // 初次创建应用，留空，这里自动填写
    "gewechat_app_id": "", // 初次创建应用，留空，这里自动填写
    "gewechat_callback_url": "http://your_local_ip:1145/v2/api/callback/collect", // 一般不需要改
    "server_host": "localhost", // 应该也不需要修改
    "settings_url": "", // 自动生成
    "GPT-SoVITS_url": "http://127.0.0.1:9880", // GPT-SoVITS的url,一般默认即可
    "text_language": "ja", // 模型发送的语音语言(如果为中文之外的语言，需要在Dify端修改提示词)
    "call_back_success_falg": false, // 登陆后如果发送消息没反应，把这个变为false即可重新登录，记得登陆后成功了修改为true
    "is_remote_server": false, // 是否为远程服务器，本地部署的就填false
    "debug_mode": true, // 可以不改
    "log_level": "DEBUG", // 可以不该
    "start_time": 1742287344.8490422 // 自动生成
}
```
如果你不太知道怎么填写，可以参考项目中的config.example.json


##  主要依赖

| 依赖包 | 版本 | 用途 |
|-------|------|------|
| gradio | >=5.21.0 | Web界面框架 |
| web.py | >=0.62 | Web服务框架 |
| requests | >=2.32.3 | HTTP请求库 |
| qrcode | >=7.4.2 | 二维码生成 |
| pilk/pysilk | 最新 | 语音处理支持 |

## 🚀 开发计划

### 近期计划
- [x] 完善ChatFlow相关功能
- [x] 优化Web设置界面
- [x] 微信发送语音开关
- [ ] 正式发布V1.0.0版本
- [ ] 更新视频教程

### 后期计划
- [ ] 增加web端的功能(支持新建对话、删除对话、修改提示词等等)
- [ ] 一键部署
- [ ] 支持文档上传及处理
- [ ] 支持视频、图片识别等
- [ ] 表情包发送
- [ ] 用户可以发语音(语音识别)
- [ ] 支持群聊
- [ ] QQ移植


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

## 📜 项目声明
- 本项目仅供技术研究与学习交流
- 严禁用于任何违法或违反道德的场景
- 生成内容不代表开发者立场和观点
- 使用者需对自身行为负全责
- 开发者不对因使用本项目产生的任何问题承担责任

---

<p align="center">如果这个项目对您有帮助，请考虑给它一个星标 ⭐️</p>
