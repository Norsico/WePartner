import json
import os

import requests

from Core.Logger import Logger
from Core.factory.client_factory import ClientFactory

logging = Logger()


class Config:
    def __init__(self, file_path="./config.json", is_init=False):
        """
        初始化Config类，指定配置文件路径。
        :param file_path: 配置文件的路径，默认为当前目录下的config.json
        :param is_init: 是否仅初始化配置，不执行登录操作
        """
        self.is_init = is_init
        self.file_path = file_path
        self.data = {}
        self.gewechat_client = None
        
        # 如果文件存在，加载配置文件内容
        if os.path.exists(self.file_path):
            self.load()
        else:
            # 如果文件不存在，创建一个空的配置文件
            logging.warning(f"配置文件 {self.file_path} 不存在，已创建空配置文件")
            self.save()
            
        # 初始化配置
        self.init_config()

    def init_config(self):
        """
        初始化配置，包括检查必要的配置项和获取token
        """
        # 设置日志级别
        log_level = self.data.get('log_level', 'INFO')
        debug_mode = self.data.get('debug_mode', False)
        if debug_mode:
            log_level = 'DEBUG'
        try:
            logging.set_level(log_level)
        except (ValueError, TypeError) as e:
            logging.warning(f"设置日志级别失败: {e}，使用默认级别INFO")
            logging.set_level('INFO')
        
        # 检查token是否存在，如果不存在则获取
        if self.data.get('gewechat_token', '') == '':
            # 获取token
            url = self.data.get('gewechat_base_url', '') + "/tools/getTokenId"
            if not self.data.get('gewechat_base_url', ''):
                logging.error("缺少必要的配置参数：gewechat_base_url")
                return
                
            try:
                response = requests.request("POST", url, headers={}, data={})
                token = json.loads(response.text)['data']
                logging.warning(f"Token未设置，已自动获取Token: {token}")
                self.set('gewechat_token', token)
            except Exception as e:
                logging.error(f"获取Token失败: {e}")
                return

    def load(self):
        """
        从文件中加载配置数据。
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except json.JSONDecodeError as e:
            logging.error(f"加载配置文件时出错: {e}")
            self.data = {}

    def save(self):
        """
        将当前配置数据保存到文件中。
        """
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        """
        获取配置项的值。
        :param key: 配置项的键
        :param default: 如果键不存在时返回的默认值
        :return: 配置项的值或默认值
        """
        return self.data.get(key, default)

    def set(self, key, value):
        """
        设置配置项的值。
        :param key: 配置项的键
        :param value: 配置项的值
        """
        self.data[key] = value
        self.save()
        logging.success(f"设置配置项 {key} = {value}成功")

    def delete(self, key):
        """
        删除配置项。
        :param key: 配置项的键
        """
        if key in self.data:
            del self.data[key]
            self.save()

    def get_gewechat_client(self):
        """
        获取GewechatClient实例
        使用ClientFactory确保全局只有一个实例
        
        :return: GewechatClient实例
        """
        # 使用工厂获取客户端实例
        client = ClientFactory.get_client(self)
        
        # 如果不是仅初始化模式，并且有app_id，则尝试登录
        if not self.is_init and self.get('gewechat_app_id', ''):
            ClientFactory.login_if_needed(client, self.get('gewechat_app_id'))
            
        return client

    def __str__(self):
        """
        返回配置数据的字符串表示。
        """
        return json.dumps(self.data, indent=4, ensure_ascii=False)
