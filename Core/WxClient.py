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
from Core.web.settings_manager import SettingsManager
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
        
        # 在新线程中设置回调地址
        def setup_callback():
            try:
                callback_resp = self.client.set_callback(self.gewechat_token, self.gewechat_callback_url)
                if callback_resp.get("ret") == 200:
                    logger.success("回调地址设置成功")
                else:
                    logger.warning(f"回调地址设置返回异常状态: {callback_resp}")
                    logger.info("继续运行，回调可能仍然有效...")
                    if not self.config.get("call_back_success_falg"):
                        self.client.logout(self.gewechat_app_id)
                        ClientFactory.reset()
                        # 重新登录
                        app_id, error_msg = self.client.login(app_id=self.gewechat_app_id)
                        if error_msg:
                            logger.error(f"重新登录失败: {error_msg}")
                            self.config.set("call_back_success_falg", False)
                        else:
                            logger.success(f"重新登录成功，应用ID: {app_id}")
                        # 重新设置回调
                        callback_resp = self.client.set_callback(self.gewechat_token, self.gewechat_callback_url)
                        if callback_resp.get("ret") == 200:
                            logger.success("重新登录后回调地址设置成功")
                        else:
                            logger.warning(f"重新登录后回调地址设置返回异常状态: {callback_resp}")
                            logger.warning(f"正在测试回调是否有效...")
                            # 测试回调是否有效
                            self.test_callback()
                        self.config.set("call_back_success_falg", True)
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

    def test_callback(self):
        # 新建线程发送消息测试回调是否有效
        def send_test_msg():
            self.channel.send_text_message_by_name(self.config.get("master_name"), "测试回调(6秒等待)...")
            time.sleep(6)
            global is_callback_success
            if is_callback_success:
                logger.success("回调测试成功")
                self.channel.send_text_message_by_name(self.config.get("master_name"), "回调设置成功")
            else:
                logger.error("回调测试失败")
                self.channel.send_text_message_by_name(self.config.get("master_name"), "回调设置失败")

        # 新建线程发送消息测试回调是否有效
        test_thread = threading.Thread(target=send_test_msg, daemon=True)
        test_thread.start()


class Query:
    def __init__(self):
        # 使用is_init=True创建配置，表示只初始化配置，不执行登录
        self.config = Config(file_path='./config.json', is_init=True)
        # 使用ClientFactory获取客户端实例，确保全局只有一个实例
        self.client = ClientFactory.get_client(self.config)
        # 创建通道对象
        self.channel = Channel(self.client, self.config)
        self.message_queue = []  # 消息队列
        self.timer = None  # 定时器
        self.queue_lock = threading.Lock()  # 队列锁
        self.settings_manager = SettingsManager()

    def process_message_queue(self):
        """处理消息队列中的所有消息"""
        with self.queue_lock:
            if not self.message_queue:
                return
                
            # 合并所有消息
            combined_message = "\n".join([msg.content for msg in self.message_queue])
            logger.info(f"处理合并后的消息: {combined_message}")
            
            try:
                result = self.channel.compose_context(combined_message)
                logger.info(f"消息处理完成，结果: {result}")
            except Exception as e:
                logger.error(f"消息处理过程中出现错误: {str(e)}")
            
            # 清空消息队列
            self.message_queue.clear()
        
    def reset_timer(self):
        """重置定时器"""
        if self.timer is not None:
            self.timer.cancel()
        self.timer = threading.Timer(self.settings_manager.get_settings().get("timer_seconds"), self.process_message_queue)
        self.timer.start()

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

        # 处理有效消息
        try:
            with self.queue_lock:
                self.message_queue.append(gewechat_msg)
                logger.info(f"收到新消息，加入队列: {gewechat_msg.content}")
            self.reset_timer()
        except Exception as e:
            logger.error(f"消息处理过程中出现错误: {str(e)}")
            
        return "success"
