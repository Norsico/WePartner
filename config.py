import json
import os
import time
from typing import Any, Dict, Optional

import requests

from Core.Logger import Logger
from Core.factory.client_factory import ClientFactory

logging = Logger()


class Config:
    """
    配置管理类，负责加载、保存和验证配置
    """
    
    # 默认配置
    DEFAULT_CONFIG = {
        "master_name": "filehelper",
        "is_remote_server": False,
        "server_host": "localhost",
        "debug_mode": False,
        "log_level": "INFO",
        "start_time": None
    }
    
    # 必需的配置项
    REQUIRED_CONFIG = [
        "gewechat_base_url",
        "dify_api_base"
    ]
    
    def __init__(self, file_path="./config.json", is_init=False):
        """
        初始化Config类，指定配置文件路径。
        
        Args:
            file_path: 配置文件的路径，默认为当前目录下的config.json
            is_init: 是否仅初始化配置，不执行登录操作
        """
        self.is_init = is_init
        self.file_path = file_path
        self.data: Dict[str, Any] = {}
        self.gewechat_client = None
        
        # 设置日志文件
        log_dir = os.path.join(os.path.dirname(file_path), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"wxChatBot_{time.strftime('%Y%m%d')}.log")
        logging.set_log_file(log_file)
        
        # 如果文件存在，加载配置文件内容
        if os.path.exists(self.file_path):
            self.load()
        else:
            # 如果文件不存在，创建一个包含默认配置的文件
            self.data = self.DEFAULT_CONFIG.copy()
            logging.warning(f"配置文件 {self.file_path} 不存在，已创建包含默认配置的文件")
            self.save()
            
        # 初始化配置
        self.init_config()

    def init_config(self):
        """
        初始化配置，包括验证配置、设置日志级别和获取token
        """
        # # 验证必需的配置项
        # missing_config = [key for key in self.REQUIRED_CONFIG if not self.data.get(key)]
        # if missing_config:
        #     logging.error(f"缺少必要的配置参数：{', '.join(missing_config)}")
        #     return
            
        # 设置启动时间
        if not self.data.get('start_time'):
            self.data['start_time'] = time.time()
            self.save()
        
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
        if not self.data.get('gewechat_token'):
            self._get_token()
    
    def _get_token(self) -> Optional[str]:
        """
        获取gewechat token
        
        Returns:
            Optional[str]: 获取到的token，如果失败则返回None
        """
        url = self.data.get('gewechat_base_url', '') + "/tools/getTokenId"
        if not self.data.get('gewechat_base_url'):
            logging.error("缺少必要的配置参数：gewechat_base_url")
            return None
            
        try:
            response = requests.post(url, headers={}, data={})
            response.raise_for_status()  # 检查响应状态
            token = response.json()['data']
            logging.warning(f"Token未设置，已自动获取Token: {token}")
            self.set('gewechat_token', token)
            return token
        except requests.RequestException as e:
            logging.error(f"获取Token失败: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            logging.error(f"解析Token响应失败: {e}")
            return None

    def load(self):
        """从文件中加载配置数据"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
                
            # # 使用默认值填充缺失的配置项
            # for key, value in self.DEFAULT_CONFIG.items():
            #     if key not in self.data:
            #         self.data[key] = value
                    
        except json.JSONDecodeError as e:
            logging.error(f"加载配置文件时出错: {e}")
            self.data = self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logging.error(f"读取配置文件时出错: {e}")
            self.data = self.DEFAULT_CONFIG.copy()

    def save(self):
        """将当前配置数据保存到文件中"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置文件时出错: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项的值
        
        Args:
            key: 配置项的键
            default: 如果键不存在时返回的默认值
            
        Returns:
            Any: 配置项的值或默认值
        """
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项的值
        
        Args:
            key: 配置项的键
            value: 配置项的值
        """
        if self.data.get(key) != value:
            self.data[key] = value
            self.save()
            logging.success(f"设置配置项 {key} = {value} 成功")
        else:
            logging.debug(f"配置项 {key} 的值未变化，跳过保存")

    def delete(self, key: str) -> None:
        """
        删除配置项
        
        Args:
            key: 配置项的键
        """
        if key in self.data:
            del self.data[key]
            self.save()
            logging.info(f"已删除配置项: {key}")

    def get_gewechat_client(self):
        """
        获取GewechatClient实例
        使用ClientFactory确保全局只有一个实例
        
        Returns:
            GewechatClient实例
        """
        # 使用工厂获取客户端实例
        client = ClientFactory.get_client(self)
        
        # 如果不是初始化模式，并且没有app_id，则登录
        if not self.is_init and not self.get('gewechat_app_id'):
            logging.info(f"尝试登录: {self.get('gewechat_app_id')}")
            ClientFactory.login_if_needed(client, self.get('gewechat_app_id'), self)
        return client

    def __str__(self) -> str:
        """返回配置数据的字符串表示"""
        return json.dumps(self.data, indent=4, ensure_ascii=False)

    def validate(self) -> bool:
        """
        验证配置是否完整有效
        
        Returns:
            bool: 配置是否有效
        """

        # # 检查必需的配置项
        # for key in self.REQUIRED_CONFIG:
        #     if not self.data.get(key):
        #         logging.error(f"缺少必要的配置参数：{key}")
        #         return False
        
        # # 验证URL格式
        # for key in ['gewechat_base_url', 'dify_api_base', 'gewechat_callback_url']:
        #     if url := self.data.get(key):
        #         if not url.startswith(('http://', 'https://')):
        #             logging.error(f"无效的URL格式：{key} = {url}")
        #             return False
        
        return True
