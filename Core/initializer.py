"""
系统初始化模块，负责依赖检查、环境检查、配置初始化等功能
"""
import platform
import sys
from typing import Tuple

from Core.Logger import Logger
from Core.WxClient import WxChatClient
from config import Config

logger = Logger()


class SystemInitializer:
    """
    系统初始化器，负责系统启动前的各项检查和初始化工作
    """
    
    def __init__(self):
        """初始化系统初始化器"""
        self.config = None
        self.wx_client = None
    
    def check_environment(self) -> bool:
        """
        检查运行环境
        
        Returns:
            bool: 环境检查是否通过
        """
        logger.info("正在检查运行环境...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            logger.error(f"Python版本过低: {sys.version}，需要Python 3.8+")
            return False
            
        # 检查操作系统
        system_info = platform.system()
        if system_info not in ["Windows", "Linux", "MacOS"]:
            logger.error(f"不支持的操作系统: {system_info}")
            return False
            
        logger.success(f"环境检查通过: Python {sys.version}, OS: {system_info}")
        return True
    
    
    def init_config(self) -> bool:
        """
        初始化配置
        
        Returns:
            bool: 配置初始化是否成功
        """
        logger.info("正在初始化配置...")
        
        try:
            # 创建配置对象
            self.config = Config('./config.json')
            # 更新启动时间

            logger.success("配置初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"配置初始化失败: {str(e)}")
            return False
    
    def init_wx_client(self) -> bool:
        """
        初始化微信客户端
        
        Returns:
            bool: 客户端初始化是否成功
        """
        logger.info("正在初始化微信客户端...")
        
        try:
            self.wx_client = WxChatClient(self.config)
            logger.success("微信客户端初始化完成")
            return True
        except Exception as e:
            logger.error(f"微信客户端初始化失败: {str(e)}")
            return False
    
    def initialize(self) -> Tuple[bool, WxChatClient]:
        """
        执行完整的初始化流程
        
        Returns:
            Tuple[bool, WxChatClient]: (是否初始化成功, 微信客户端实例)
        """
        logger.info("开始系统初始化...")
            
        # 检查环境
        if not self.check_environment():
            return False, None
            
        # 初始化配置
        if not self.init_config():
            return False, None
        
        # 初始化微信客户端
        if not self.init_wx_client():
            return False, None
        
        logger.success("系统初始化完成")
        return True, self.wx_client
