import json
import threading
import time
from urllib.parse import urlparse

import web

from Core.GewechatMessage import GeWeChatMessage
from Core.Logger import Logger
from Core.bridge.context import ContextType
from Core.bridge.channel import Channel
from Core.factory.client_factory import ClientFactory
from config import Config

logger = logging = Logger()


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
        
        # 在新线程中设置回调地址
        def setup_callback():
            try:
                callback_resp = self.client.set_callback(self.gewechat_token, self.gewechat_callback_url)
                if callback_resp.get("ret") == 200:
                    logger.success("回调地址设置成功")
                else:
                    logger.warning(f"回调地址设置返回异常状态: {callback_resp}")
                    logger.info("继续运行，回调可能仍然有效...")
                    self.client.logout(self.gewechat_app_id)
                    ClientFactory.reset()
                    # 重新登录
                    app_id, error_msg = self.client.login(app_id=self.gewechat_app_id)
                    if error_msg:
                        logger.error(f"重新登录失败: {error_msg}")
                    else:
                        logger.success(f"重新登录成功，应用ID: {app_id}")
                    # 重新设置回调
                    callback_resp = self.client.set_callback(self.gewechat_token, self.gewechat_callback_url)
                    if callback_resp.get("ret") == 200:
                        logger.success("重新登录后回调地址设置成功")
                    else:
                        logger.warning(f"重新登录后回调地址设置返回异常状态: {callback_resp}")
            except Exception as e:
                logger.error(f"设置回调地址时出错: {e}")
                logger.info("继续运行，回调可能仍然有效...")
        
        # 启动回调设置线程
        callback_thread = threading.Thread(target=setup_callback, daemon=True)
        callback_thread.start()
        
        # 保持主线程运行
        try:
            while True:
                time.sleep(1)  # 每秒检查一次
        except KeyboardInterrupt:
            logger.info("服务器正在停止...")


class Query:
    def __init__(self):
        # 使用is_init=True创建配置，表示只初始化配置，不执行登录
        self.config = Config(file_path='./config.json', is_init=True)
        # 使用ClientFactory获取客户端实例，确保全局只有一个实例
        self.client = ClientFactory.get_client(self.config)
        # 创建通道对象
        self.channel = Channel(self.client, self.config)

    def POST(self):
        """处理微信回调消息"""
        web_data = web.data()
        data = json.loads(web_data)
        
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
            return "success"

        # 忽略非用户消息（如公众号、系统通知等）
        if gewechat_msg.ctype == ContextType.NON_USER_MSG:
            logger.debug(f"忽略非用户消息，来自 {gewechat_msg.from_user_id}: {gewechat_msg.content}")
            return "success"

        # 忽略来自自己的消息
        if gewechat_msg.my_msg:
            logger.debug(f"忽略自己发送的消息: {gewechat_msg.content}")
            return "success"

        # 忽略过期的消息
        if int(gewechat_msg.create_time) < int(time.time()) - 60 * 5:  # 跳过5分钟前的历史消息
            logger.debug(f"忽略过期消息（5分钟前），来自 {gewechat_msg.actual_user_id}: {gewechat_msg.content}")
            return "success"

        # 处理有效消息
        try:
            # 直接将消息传递给channel处理，让channel决定如何处理不同类型的消息
            logger.info(f"正在处理消息: {gewechat_msg.content}")
            result = self.channel.compose_context(gewechat_msg.content)
            logger.info(f"消息处理完成，结果: {result}")
        except Exception as e:
            logger.error(f"消息处理过程中出现错误: {str(e)}")
            
        return "success"
