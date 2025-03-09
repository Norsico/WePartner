import json
import os

import requests

from Core.Logger import Logger
from gewechat.client import GewechatClient

logging = Logger()


class Config:
    def __init__(self, file_path="./config.json", is_init=False):
        """
        初始化Config类，指定配置文件路径。
        :param file_path: 配置文件的路径，默认为当前目录下的config.json
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
        if not self.is_init:
            self.init_config()
        else:
            self.gewechat_client = GewechatClient(self.data['gewechat_base_url'], self.data['gewechat_token'])

    def init_config(self):
        if self.is_init:
            # 创建 GewechatClient 实例
            client = GewechatClient(self.data['gewechat_base_url'], self.data['gewechat_token'])
            self.gewechat_client = client
        if self.data['gewechat_token'] != '' and self.data['gewechat_app_id'] != '' and not self.is_init:
            # 创建 GewechatClient 实例
            client = GewechatClient(self.data['gewechat_base_url'], self.data['gewechat_token'])
            print(client)
            # 登录, 自动创建二维码，扫码后自动登录
            app_id, error_msg = client.login(app_id=self.data['gewechat_app_id'])
            if error_msg:
                logging.error("登录失败")
                return
            logging.success(f"登录成功")
            self.gewechat_client = client
        else:
            if self.data['gewechat_token'] == '':
                # 获取token
                url = self.data['gewechat_base_url'] + "/tools/getTokenId"
                response = requests.request("POST", url, headers={}, data={})
                logging.warning(f"Token未设置，已自动获取Token: {json.loads(response.text)['data']}")
                self.set('gewechat_token', json.loads(response.text)['data'])
            if self.data['gewechat_app_id'] == '':
                # 创建 GewechatClient 实例
                client = GewechatClient(self.data['gewechat_base_url'], self.data['gewechat_token'])
                # 登录, 自动创建二维码，扫码后自动登录
                app_id, error_msg = client.login(app_id=self.data['gewechat_app_id'])
                self.set('gewechat_app_id', app_id)
                if error_msg:
                    logging.error("登录失败")
                    return
                logging.success(f"登录成功")
                self.gewechat_client = client

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
        return self.gewechat_client

    def __str__(self):
        """
        返回配置数据的字符串表示。
        """
        return json.dumps(self.data, indent=4, ensure_ascii=False)


# 示例用法
if __name__ == "__main__":
    config = Config()

    # # 设置配置项
    # config.set("name", "Kimi")
    # config.set("age", 25)
    # config.set("is_active", True)
    #
    # # 获取配置项
    # print("Name:", config.get("name"))
    # print("Age:", config.get("age"))
    # print("Is Active:", config.get("is_active"))
    #
    # # 删除配置项
    # config.delete("is_active")

    # 查看当前配置
    print("Current Config:")
    print(config)
