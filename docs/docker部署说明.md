# wxChatBot Docker部署说明（目前不太推荐Docker部署，因为没经过充分测试，推荐使用Anaconda环境部署）

## 准备工作

确保您的系统已安装Docker和Docker Compose：

- Docker: [安装指南](https://docs.docker.com/get-docker/)
- Docker Compose: [安装指南](https://docs.docker.com/compose/install/)

## 部署步骤

### 1. 配置文件准备

确保您已经正确配置了`config.json`文件。如果没有，请复制`config.example.json`并进行相应修改：

```bash
cp config.example.json config.json
```

根据您的实际需求修改`config.json`中的配置参数。

### 2. 构建并启动容器

在项目根目录下执行以下命令构建并启动容器：

```bash
docker-compose up -d
```

这将在后台启动wxChatBot应用。

### 3. 查看日志

您可以通过以下命令查看应用日志：

```bash
docker-compose logs -f
```

### 4. 停止服务

如需停止服务，请执行：

```bash
docker-compose down
```

## 端口说明

- 7860: Gradio Web界面端口
- 1145: 回调URL端口

## 数据持久化

以下目录通过卷挂载实现持久化：

- `./config.json`: 配置文件
- `./logs`: 日志文件
- `./tmp`: 临时文件

## 常见问题

### 1. 端口冲突

如果出现端口冲突，请修改`docker-compose.yml`文件中的端口映射。例如：

```yaml
ports:
  - "8000:7860"  # 将主机的8000端口映射到容器的7860端口
```

### 2. 配置修改

如果修改了`config.json`文件，需要重启容器才能生效：

```bash
docker-compose restart
``` 