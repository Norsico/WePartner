import json
import threading
import time
from urllib.parse import urlparse
import os
import web

from Core.GewechatMessage import GeWeChatMessage
from Core.Logger import Logger
from Core.bridge.context import ContextType
from Core.bridge.channel import Channel
from Core.factory.client_factory import ClientFactory
from config import Config
from Core.api import serverapi
logger = logging = Logger()
is_callback_success = False


class WxChatClient:
    def __init__(self, config):
        self.gewechat_base_url = config.get('gewechat_base_url')
        self.gewechat_token = config.get('gewechat_token')
        self.gewechat_app_id = config.get('gewechat_app_id')
        self.client = config.get_gewechat_client()
        self.gewechat_callback_url = config.get('gewechat_callback_url')
        self.config = config
        self.channel = Channel(self.client, config)
        self.set_wx_callback()

    def set_wx_callback(self):
        # 从回调地址中解析出端口与url path，启动回调服务器
        parsed_url = urlparse(self.gewechat_callback_url)
        path = parsed_url.path
        # 如果没有指定端口，使用默认端口80
        port = parsed_url.port or 80
        logger.info(f"正在启动回调服务器: {self.gewechat_callback_url}, 使用端口 {port}")
        urls = (path, "Core.WxClient.Query")
        app = web.application(urls, globals(), autoreload=False)
        
        # 在新线程中启动服务器
        def run_server():
            web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", port))
            
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        logger.info("等待服务器启动（5秒）...")
        time.sleep(5)
        
        # 启动 API 服务
        serverapi.run()
        
        # 保持主线程运行
        try:
            while True:
                time.sleep(1)  # 每秒检查一次
        except KeyboardInterrupt:
            logger.info("服务器正在停止...")



class Query:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Query, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # 使用is_init=True创建配置，表示只初始化配置，不执行登录
            self.config = Config(file_path='./config.json', is_init=True)
            # 使用ClientFactory获取客户端实例，确保全局只有一个实例
            self.client = ClientFactory.get_client(self.config)
            # 创建通道对象
            self.channel = Channel(self.client, self.config)
            self._initialized = True
            logger.debug("Query类初始化完成")

    def GET(self):
        # 搭建简单的文件服务器，用于向gewechat服务传输语音等文件，但只允许访问tmp目录下的文件
        params = web.input(file="")
        file_path = params.file
        if file_path:
            # 使用os.path.abspath清理路径
            clean_path = os.path.abspath(file_path)
            # 获取tmp目录的绝对路径
            tmp_dir = os.path.abspath("tmp")
            # 检查文件路径是否在tmp目录下
            if not clean_path.startswith(tmp_dir):
                logger.error(
                    f"[gewechat] Forbidden access to file outside tmp directory: file_path={file_path}, clean_path={clean_path}, tmp_dir={tmp_dir}")
                raise web.forbidden()

            if os.path.exists(clean_path):
                with open(clean_path, 'rb') as f:
                    return f.read()
            else:
                logger.error(f"[gewechat] File not found: {clean_path}")
                raise web.notfound()
        return "gewechat callback server is running"

    def POST(self):
        """处理微信回调消息"""
        global is_callback_success

        web_data = web.data()
        data = json.loads(web_data)

        # print(data)
        
        # gewechat服务发送的回调测试消息
        if isinstance(data, dict) and 'testMsg' in data and 'token' in data:
            logger.debug(f"收到回调测试消息: {data}")
            return "success"
            
        # 解析消息
        gewechat_msg = GeWeChatMessage(data, self.client)
        
        # 过滤不需要处理的消息
        
        # 微信客户端的状态同步消息
        if gewechat_msg.ctype == ContextType.STATUS_SYNC:
            logger.debug("忽略状态同步消息")
            is_callback_success = True
            return "success"

        # 忽略非用户消息（如公众号、系统通知等）
        if gewechat_msg.ctype == ContextType.NON_USER_MSG:
            logger.debug(f"忽略非用户消息，来自 {gewechat_msg.from_user_id}: {gewechat_msg.content}")
            return "success"

        # 忽略来自自己的消息
        if gewechat_msg.my_msg:
            logger.debug(f"忽略自己发送的消息: {gewechat_msg.content}")
            is_callback_success = True
            return "success"

        # 忽略过期的消息
        if int(gewechat_msg.create_time) < int(time.time()) - 60 * 5:  # 跳过5分钟前的历史消息
            logger.debug(f"忽略过期消息（5分钟前），来自 {gewechat_msg.actual_user_id}: {gewechat_msg.content}")
            return "success"
        
        # 群聊消息处理
        if not gewechat_msg.my_msg:
            wxid = gewechat_msg.other_user_id
            if gewechat_msg.is_at:
                # 处理有效消息
                try:
                    self.channel.compose_context(gewechat_msg.content, wxid)
                    return "success"
                except Exception as e:
                    logger.error(f"消息处理过程中出现错误: {str(e)}")
        
        # 私信消息处理
        if not gewechat_msg.my_msg:
            if not gewechat_msg.is_group:
                if gewechat_msg.ctype not in {
                    ContextType.VOICE,             # 语言
                    ContextType.IMAGE,             # 图片
                    ContextType.NON_USER_MSG,      # 公众号消息
                    ContextType.SHARING,           # 分享信息
                    ContextType.EMOJI              # 表情包
                    }:
                    wxid = gewechat_msg.other_user_id
                    # 处理有效消息
                    try:
                        self.channel.compose_context(gewechat_msg.content, wxid)
                        return "success"
                    except Exception as e:
                        logger.error(f"消息处理过程中出现错误: {str(e)}")           
            
        return "success"
