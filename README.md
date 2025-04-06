# API测试工具使用说明

这个工具用于测试wxChatBot的配置修改API，可以方便地修改Dify和Coze的配置，以及切换AI平台。

## 使用方法

### 查看当前配置

```bash
python apitest.py info
```

### 修改Dify配置

```bash
# 修改Dify服务器地址
python apitest.py dify --server api.dify.ai

# 修改Dify API密钥
python apitest.py dify --key 你的API密钥

# 同时修改服务器和密钥
python apitest.py dify --server api.dify.ai --key 你的API密钥
```

### 修改Coze配置

```bash
# 修改Coze智能体ID
python apitest.py coze --id 你的智能体ID

# 修改Coze API令牌
python apitest.py coze --token 你的API令牌

# 同时修改智能体ID和令牌
python apitest.py coze --id 你的智能体ID --token 你的API令牌
```

### 切换AI平台

```bash
# 切换到Dify平台
python apitest.py platform dify

# 切换到Coze平台
python apitest.py platform coze
```

### 指定服务器IP和端口

如果API服务器不在本地或使用了非默认端口：

```bash
python apitest.py --ip 192.168.1.100 --port 8080 info
```

## 参数说明

- `--ip`: 服务器IP地址，默认为localhost
- `--port`: 服务器端口，默认为8002
- `dify`: 修改Dify配置
  - `--server`: Dify服务器地址
  - `--key`: Dify API密钥
- `coze`: 修改Coze配置
  - `--id`: Coze智能体ID
  - `--token`: Coze API令牌
- `platform`: 切换AI平台
  - `type`: 平台类型，可选值为dify或coze
- `info`: 显示当前配置信息 