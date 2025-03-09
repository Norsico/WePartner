import json
import threading
import time
from urllib.parse import urlparse

import web

from Core.GewechatMessage import GeWeChatMessage
from Core.Logger import Logger
from Core.bridge.context import ContextType
from config import Config

logger = logging = Logger()


class WxChatClient:
    def __init__(self, config):
        self.gewechat_base_url = config.get('gewechat_base_url')
        self.gewechat_token = config.get('gewechat_token')
        self.gewechat_app_id = config.get('gewechat_app_id')
        self.client = config.get_gewechat_client()
        self.gewechat_callback_url = config.get('gewechat_callback_url')
        self.set_wx_callback()

    def set_wx_callback(self):
        # 创建新线程设置回调地址
        def set_callback():
            # 等待服务器启动（给予适当的启动时间）
            import time
            logger.info("[gewechat] sleep 3 seconds waiting for server to start, then set callback")
            time.sleep(3)

            # 设置回调地址，{ "ret": 200, "msg": "操作成功" }
            callback_resp = self.client.set_callback(self.gewechat_token, self.gewechat_callback_url)
            if callback_resp.get("ret") != 200:
                logger.error(f"[gewechat] set callback failed: {callback_resp}")
                # 可能是次日凌晨自动掉线，需要重新扫码登录
                if callback_resp.get("ret") == 500 and callback_resp.get("msg") is None:
                    logger.info("[gewechat] callback 设置失败,请重新扫码登录")
                    # 退出登录
                    self.client.log_out(self.gewechat_app_id)
                    # 重新登录
                    self.client.login(self.gewechat_app_id)
                    # 重新设置回调地址
                    self.client.set_callback(self.gewechat_token, self.gewechat_callback_url)
                    logger.info("[gewechat] callback set successfully")
                    return
            logger.info("[gewechat] callback set successfully")

        callback_thread = threading.Thread(target=set_callback, daemon=True)
        callback_thread.start()

        # 从回调地址中解析出端口与url path，启动回调服务器
        parsed_url = urlparse(self.gewechat_callback_url)
        path = parsed_url.path
        # 如果没有指定端口，使用默认端口80
        port = parsed_url.port or 80
        logger.info(f"[gewechat] start callback server: {self.gewechat_callback_url}, using port {port}")
        urls = (path, "Core.WxClient.Query")
        app = web.application(urls, globals(), autoreload=False)
        web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", port))

        self.client.set_callback(self.gewechat_token, self.gewechat_callback_url)


class Query:
    def __init__(self):
        self.config = Config(file_path='./config.json', is_init=True)
        self.client = self.config.get_gewechat_client()

    def POST(self):
        web_data = web.data()
        data = json.loads(web_data)
        # gewechat服务发送的回调测试消息
        if isinstance(data, dict) and 'testMsg' in data and 'token' in data:
            logger.debug(f"[gewechat] 收到gewechat服务发送的回调测试消息: {data}")
            return "success"
        gewechat_msg = GeWeChatMessage(data, self.client)
        # 微信客户端的状态同步消息
        if gewechat_msg.ctype == ContextType.STATUS_SYNC:
            # logger.debug(f"[gewechat] ignore status sync message: {gewechat_msg.content}")
            return "success"

        # 忽略非用户消息（如公众号、系统通知等）
        if gewechat_msg.ctype == ContextType.NON_USER_MSG:
            logger.debug(f"[gewechat] ignore non-user message from {gewechat_msg.from_user_id}: {gewechat_msg.content}")
            return "success"

        # 忽略来自自己的消息
        if gewechat_msg.my_msg:
            logger.debug(
                f"[gewechat] ignore message from myself: {gewechat_msg.actual_user_id}: {gewechat_msg.content}")
            return "success"

        # 忽略过期的消息
        if int(gewechat_msg.create_time) < int(time.time()) - 60 * 5:  # 跳过5分钟前的历史消息
            logger.debug(
                f"[gewechat] ignore expired message from {gewechat_msg.actual_user_id}: {gewechat_msg.content}")
            return "success"

        print("Debug")
        print(f"gewechat_msg.ctype: {gewechat_msg.ctype} Type: {type(gewechat_msg.ctype)}")
        print(f"gewechat_msg.content: {gewechat_msg.content} Type: {type(gewechat_msg.content)}")
        print(f"gewechat_msg.is_group: {gewechat_msg.is_group} Type: {type(gewechat_msg.is_group)}")
        print(f"gewechat_msg: {gewechat_msg} Type: {type(gewechat_msg)}")
        print(f"from_user_id: {gewechat_msg.from_user_id} Type: {type(gewechat_msg.from_user_id)}")
        print("Debug end")

        # 处理指令消息
        if gewechat_msg.content.startswith("#"):
            from Core.bridge.channel import Channel
            channel = Channel(self.client, self.config)
            # 立即处理指令
            channel.compose_context(gewechat_msg.content)
            return "success"
        # 处理普通消息
        else:
            from Core.bridge.channel import Channel
            channel = Channel(self.client, self.config)
            # 立即处理消息
            channel.compose_context(gewechat_msg.content)

        return "success"
