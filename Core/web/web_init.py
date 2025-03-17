"""
wxChatBot Web初始化模块
负责初始化web服务和配置
"""
from Core.web.settings_app import get_settings_app
from config import Config
from Core.Logger import Logger

logger = Logger()

class WebInitializer:
    """Web初始化类，负责初始化web服务和配置"""
    
    def __init__(self, config_path='./config.json'):
        """
        初始化WebInitializer
        
        Args:
            config_path: 配置文件路径，默认为'./config.json'
        """
        self.config_path = config_path
        self.config = Config(config_path)
        self.settings_url = None
        
    def initialize(self):
        """
        初始化web服务
        
        Returns:
            str: 设置页面URL
        """
        logger.info("正在初始化Web服务...")
        
        # 获取设置应用实例并启动
        settings_app = get_settings_app()
        self.settings_url = settings_app.start()
        
        # 更新配置
        self.config.set("settings_url", self.settings_url)
        self.config.save()
        
        logger.success(f"Web服务初始化完成，设置页面URL: {self.settings_url}")
        return self.settings_url
    
    def get_settings_url(self):
        """
        获取设置页面URL
        
        Returns:
            str: 设置页面URL
        """
        return self.settings_url
