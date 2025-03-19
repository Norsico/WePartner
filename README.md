# wxChatBot

<div align="center">
  <a href="README.md">中文</a> | 
  <a href="docs/en/README.md">English</a>
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

<div align="center" style="display: flex; justify-content: center; flex-wrap: nowrap; gap: 10px; max-width: 100%; overflow-x: auto;">
  <img src="docs/images/wxchat_demo.jpg" alt="微信聊天演示" width="32%" style="max-width: 32%;">
  <img src="docs/images/settings_chatflow.jpg" alt="功能展示" width="32%" style="max-width: 32%;">
  <img src="docs/images/settings_voice.jpg" alt="语音设置界面" width="32%" style="max-width: 32%;">
</div>
<p align="center"><b>微信聊天演示 | ChatFlow功能配置界面 | 语音设置界面</b></p>


## ✨ 功能特性

### 🤖 Dify集成
- 支持Dify的ChatFlow功能，提供从Agent构建到AI workflow编排、RAG检索、模型管理等能力
- 轻松构建和运营生成式AI原生应用，理论上Dify支持的功能都能集成到本项目
- 原生支持永久记忆和本地知识库检索
- 支持自定义插件、自定义函数调用等扩展功能

<div align="center">
  <img src="docs/images/dify_home.png" alt="Dify主页" width="80%" style="max-width: 800px; margin: 20px 0; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <p><b>Dify主页面</b></p>
  
  <img src="docs/images/dify_model.png" alt="Dify模型配置页" width="80%" style="max-width: 800px; margin: 20px 0; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <p><b>模型配置界面</b></p>
  
  <img src="docs/images/dify_chatflow.png" alt="Dify的Chatflow工作页" width="80%" style="max-width: 800px; margin: 20px 0; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <p><b>ChatFlow工作流配置</b></p>
</div>

### 📱 微信集成
- 无缝对接个人微信，轻松接入微信生态
- 支持文本、语音回复（原生语音泡，非文件形式）
- 可通过简单指令（如发送`#设置`）获取管理界面

### 🔊 语音功能
- 基于GPT-SoVITS技术，可自定义语音模型
- 仅需极少量语音数据即可高度还原声音特征
- 支持语音消息转文本和文本合成语音
- 可配置多种语音参数，实现个性化语音体验

### ⚙️ 系统功能
- 使用Gradio开发Web管理界面，实现轻松配置
- 使用Gradio的share=True模式，无需公网IP即可远程访问配置界面
- 项目结构简单易懂，易于自定义扩展和二次开发
- 自带日志记录与监控系统

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

## 🚀 快速开始

### 环境要求
- Python 3.11+
- 一个绑定了自己身份证的微信账号(最好还开通了钱包，里面放1块钱，建议使用独立设备运行)
- Dify的Docker环境
- Gewechat的Docker环境

### 视频教程
- 在做了，在做了

### 安装步骤

#### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/wxChatBot.git
cd wxChatBot
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 修改配置文件（见下方配置说明）
```bash
# 编辑config.json填入必要信息
config.json
```

#### 4. 通过Docker构建Dify (可参考: [Dify](https://github.com/langgenius/dify))
```bash
git clone https://github.com/langgenius/dify.git
cd dify
cd docker
cp .env.example .env
docker compose up -d
```

#### 5. 通过Docker构建GeweChat (可参考: [Gewechat](https://github.com/Devo919/Gewechat))
##### 5.1 拉取镜像
```bash
docker pull registry.cn-hangzhou.aliyuncs.com/gewe/gewe:latest
docker tag registry.cn-hangzhou.aliyuncs.com/gewe/gewe gewe
```

##### 5.2 运行镜像容器
```bash
mkdir -p /root/temp
docker update --restart=always gewe
docker run -itd -v /root/temp:/root/temp -p 2531:2531 -p 2532:2532 --privileged=true --name=gewe gewe /usr/sbin/init
```

##### 5.3 将容器设置成开机运行
```bash
docker update --restart=always gewe
```

#### 6. 启动项目主程序
```bash
python main.py
```

启动成功后控制台输出如下:
<div align="center">
<img src="docs/images/app_run.png" alt="配置界面" width="80%" style="max-width: 800px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
<p><b>系统启动界面</b></p>
</div>


## ⚙️ 配置说明

初次运行，请修改`config.json`，主要配置项包括：

```json
{
    "master_name": "", // 你大号的微信的名称(注意不是备注，是账号名称，最好别重名)
    "dify_api_base": "http://localhost/v1", // dify的baseurl,一般不需要改
    "gewechat_base_url": "http://your_local_ip:2531/v2/api", // gewechat的baseurl,把your_local_ip改成你的电脑IPv4地址,下面同理
    "gewechat_token": "", // 初次创建应用，留空，这里自动填写
    "gewechat_app_id": "", // 初次创建应用，留空，这里自动填写
    "gewechat_callback_url": "http://your_local_ip:1145/v2/api/callback/collect", // 一般不需要改
    "server_host": "localhost", // 应该也不需要修改
    "settings_url": "", // 自动生成
    "GPT-SoVITS_url": "http://127.0.0.1:9880", // GPT-SoVITS的url,一般默认即可
    "text_language": "ja", // 模型发送的语音语言(如果为中文之外的语言，需要在Dify端修改提示词)常用的:中文(zh),英文(en),日文(ja)
    "call_back_success_falg": false, // 登陆后如果发送消息没反应，把这个变为false即可重新登录，记得登陆后成功了修改为true
    "is_remote_server": false, // 是否为远程服务器，本地部署的就填false
    "debug_mode": true, // 可以不改
    "log_level": "DEBUG", // 可以不该
    "start_time": 1742287344.8490422 // 自动生成
}
```

> 💡 **提示**：如果你不太知道怎么填写，可以参考项目中的`config.example.json`


## ❗注意事项

### 💡 微信回调配置
- 首次运行时，Gewechat的回调地址会自动配置
- 新设备在次日凌晨会自动掉线一次
- 解决方案：
  1. 将`config.json`中的`call_back_success_falg`设为`false`
  2. 重新扫码登录
  3. 登录成功后将`call_back_success_falg`改回`true`
- 小技巧：如果不介意每次扫码，可以始终保持`false`状态，这样能避免回调地址异常问题

### 🛠️ 环境依赖
- **Dify环境**：必须确保Dify正确部署，这是使用大模型能力的基础
- **GPT-SoVITS**：如需语音功能，请先完成部署
  - Windows用户推荐使用[GPT-SoVITS整合包](https://github.com/RVC-Boss/GPT-SoVITS?tab=readme-ov-file)
  - 其他系统请参考官方文档部署
- **本地模型**：支持使用LM Studio或Ollama部署本地模型
  - 在Dify模型配置界面中选择对应选项
  - 可根据需求进行深度定制

### 📦 FFmpeg安装指南
根据您的操作系统选择合适的安装方式：

<details>
<summary><b>Windows 系统</b></summary>

```bash
# 方式1：使用Anaconda
conda install -c conda-forge ffmpeg

# 方式2：使用Chocolatey
choco install ffmpeg
```
</details>

<details>
<summary><b>Linux 系统</b></summary>

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```
</details>

<details>
<summary><b>macOS 系统</b></summary>

```bash
# 使用Homebrew
brew install ffmpeg
```
</details>

> ⚠️ **重要提示**：
> - 推荐使用Anaconda环境，实测这样安装更加简单
> - 安装完成后请确保FFmpeg已添加到系统环境变量
> - 如遇到"路径不存在"错误，请检查环境变量配置
> - Windows用户可在系统变量Path中添加FFmpeg所在目录

## 📊 主要依赖

| 依赖包 | 版本 | 用途 |
|-------|------|------|
| `gradio` | 5.21.0 | Web界面框架，用于构建设置页面 |
| `web.py` | 0.62 | Web服务框架，处理回调和API请求 |
| `pyngrok` | 7.2.3 | 内网穿透工具，用于远程访问 |
| `requests` | 2.32.3 | HTTP请求库，用于与各服务通信 |
| `ffmpeg-python` | 0.2.0 | 音频格式转换，处理语音消息 |
| `pilk` | 0.2.4 | 微信语音编码处理 |
| `pysilk` | 0.0.1 | SILK格式音频处理 |
| `qrcode` | 7.4.2 | 二维码生成，用于微信登录 |
| `coloredlogs` | 15.0.1 | 日志美化，提供彩色日志输出 |
| `tqdm` | 4.67.1 | 进度条显示，优化用户体验 |

> 💡 **安装提示**：
> - 建议使用Anaconda环境安装依赖：
>   ```bash
>   conda create -n wxchatbot python=3.11
>   conda activate wxchatbot
>   # 确保当前在项目路径下
>   pip install -r requirements.txt
>   ```
> - 某些依赖（如 gradio）会自动安装其他必要的包
> - 确保系统已安装 FFmpeg（参考上方安装指南）

## 🚀 开发计划

### 近期计划
- [x] 完善ChatFlow相关功能
- [x] 优化Web设置界面
- [x] 微信发送语音开关
- [ ] 正式发布V1.0.0版本
- [ ] 更新视频教程

### 后期计划
- [ ] 一键部署方案
- [ ] 可设置的主动发送消息功能
- [ ] 用户可设置(自定义)在一定时间段内多次发送消息，Dify那边能够一次性处理
- [ ] 批处理操作(针对需要多次执行的指令)
- [ ] 增加web端的功能(支持新建对话、删除对话、修改提示词等等)
- [ ] 表情包发送
- [ ] 支持群聊
- [ ] 支持文档上传及处理
- [ ] 支持视频、图片识别等
- [ ] 用户可以发送语音
- [ ] QQ移植
- [ ] 长文本网页markdown渲染


## ❤️ 支持我(当前项目为本人独立开发)

<div align="center">
  <h3>💝 支持我</h3>
  <p>您的支持是我持续改进的动力</p>
  
  <p>🎯 您的投喂将用于：</p>
  <p>🎓 开源教程 • 💡 功能开发 • 🌍 社区建设 • 🔥 更多的AI功能</p>
  
  <div style="display: flex; justify-content: center; gap: 20px; margin: 20px 0;">
    <div>
      <img src="docs/images/wechat_qr.jpg" alt="微信支付" width="200px" style="border-radius: 10px;">
      <p><b>微信支付</b></p>
    </div>
    <div>
      <img src="docs/images/alipay_qr.jpg" alt="支付宝" width="200px" style="border-radius: 10px;">
      <p><b>支付宝</b></p>
    </div>
  </div>
  
  <p>🔒 赞助计划：解锁完整技术支持与进阶功能</p>
  <p style="color: #666; font-size: 0.9em;">
    🎯 基础服务：
    <br>• 📱 私有化部署方案
    <br>• 🔧 远程指导安装与环境配置
    <br>• 💻 问题解决与故障排查
  </p>
  <p style="color: #666; font-size: 0.9em;">
    🌟 进阶服务：
    <br>• 🤖 AI模型私有化部署与调优
    <br>• 🎨 定制化对话流程与场景
    <br>• 📊 专属知识库构建与数据处理
    <br>• 🔐 企业级安全性与并发优化
  </p>
  <p style="color: #666; font-size: 0.9em;">
    💎 专属服务：
    <br>• 📘 项目源码深度解析课程
    <br>• 🛠️ 项目二次开发技术咨询
    <br>• 💡 商业化应用方案定制
  </p>
  <p>💼 商务合作(非诚勿扰)：wx:N19880667051</p>
</div>

## 💬 核心交流群

<div style="display: flex; justify-content: center; gap: 20px; margin: 20px 0;">
  <div style="background: #0288d1; padding: 10px; border-radius: 5px; color: white;">
    ✨ 交流群 <span style="margin-left: 10px;">没米TAT，待开发~</span>
  </div>
  <div style="background: #ffd700; padding: 10px; border-radius: 5px; color: black;">
    🎁 赞助群 <span style="margin-left: 10px;">没米TAT，开发中~</span>
  </div>
</div>

## 🤝 贡献指南

感谢您对项目的关注！非常欢迎社区的贡献，让我们一起使这个项目变得更好。

### 🌟 贡献方式

1. 🐛 **问题反馈**
   - 提交 Bug 报告时请详细描述问题
   - 提供复现步骤和相关日志
   - 说明运行环境和相关配置

2. 💡 **功能建议**
   - 清晰描述新功能的用途和场景
   - 可以提供相关的设计思路
   - 欢迎分享使用过程中的想法

3. 📝 **文档改进**
   - 修正文档中的错误
   - 补充安装和配置说明
   - 添加使用示例和最佳实践
   - 翻译文档到其他语言

4. 💻 **代码贡献**
   - 修复已知的 Bug
   - 新功能开发
   - 性能优化
   - 代码重构

### 🎯 开发指南

- 等项目源码我再写的更加专业一点再写这个吧~

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

<div align="center">
  <p>如果这个项目对您有帮助，请考虑给它一个星标 ⭐️</p>
</div>
