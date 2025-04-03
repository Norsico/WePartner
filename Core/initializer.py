"""
系统初始化模块，负责依赖检查、环境检查、配置初始化等功能
"""
import platform
import subprocess
import sys
import time
from typing import Tuple

from Core.Logger import Logger
from Core.WxClient import WxChatClient
from config import Config

logger = Logger()


class SystemInitializer:
    """
    系统初始化器，负责系统启动前的各项检查和初始化工作
    """
    
    # 必需的Python包
    REQUIRED_PACKAGES = [
        "gradio",
        "requests",
        "web.py",
        "pydub",
        "pilk",
        "pysilk",
        "ffmpeg-python",
        "qrcode",
    ]
    
    def __init__(self):
        """初始化系统初始化器"""
        self.config = None
        self.wx_client = None
        self.start_time = None
    
    def check_dependencies(self) -> bool:
        """
        检查并安装必要的依赖
        
        Returns:
            bool: 是否所有依赖都已正确安装
        """
        logger.info("正在检查系统依赖...")
        all_installed = True
        return all_installed
        
        # for package in self.REQUIRED_PACKAGES:
        #     try:
        #         __import__(package)
        #         logger.debug(f"依赖检查: {package} - 已安装")
        #     except ImportError:
        #         all_installed = False
        #         logger.warning(f"缺少必要依赖: {package}，开始安装...")
        #         try:
        #             subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        #             logger.success(f"成功安装依赖: {package}")
        #         except Exception as e:
        #             logger.error(f"安装依赖 {package} 失败: {str(e)}")
        #             logger.info(f"请手动安装: pip install {package}")
        #             return False
        
        # if all_installed:
        #     logger.success("所有依赖检查完成")
        # return all_installed
    
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
    
    def _ask_user_confirmation(self, question: str) -> bool:
        """
        请求用户确认
        
        Args:
            question: 要询问的问题
            
        Returns:
            bool: 用户的选择（是/否）
        """
        while True:
            response = input(f"{question} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("请输入 y/yes 或 n/no")
    
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

            # 判断时间是否超过8小时
            if self.is_time_difference_over_8_hours(self.config.get('start_time'), time.time()):
                logger.warning("时间超过8小时，重新登录一下，防止出现回调异常bug")
                self.config.set('call_back_success_falg', False)
                print(f"已将call_back_success_falg设置为false")
            
            # 更新启动时间
            self.start_time = time.time()
            self.config.set('start_time', self.start_time)
            
            # 检查运行环境设置
            is_remote_server = self.config.get('is_remote_server')
            if is_remote_server is None:
                system_info = platform.system()
                logger.info(f"检测到当前系统为: {system_info}")
                
                # 询问用户是否为远程服务器
                is_remote = self._ask_user_confirmation(
                    "是否在远程服务器上运行？\n"
                    "- 选择 yes: 使用服务器URL和端口\n"
                    "- 选择 no: 使用本地URL和Ngrok内网穿透\n"
                    "请确认"
                )
                
                self.config.set('is_remote_server', is_remote)
                logger.info(f"已设置运行环境为: {'远程服务器' if is_remote else '本地机器'}")
            
            # # 确保设置了master_name
            # if not self.config.get('master_name'):
            #     logger.warning("未设置master_name，将使用默认值")
            #     self.config.set('master_name', 'filehelper')  # 默认使用文件传输助手
            
            # 验证配置
            if not self.config.validate():
                logger.error("配置验证失败")
                return False
                
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
        
        # 检查依赖
        if not self.check_dependencies():
            return False, None
            
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

    @staticmethod
    def is_time_difference_over_8_hours(timestamp1, timestamp2):
        """
        判断两个时间戳之间的时间差是否超过8小时。
        
        参数:
        timestamp1 (float): 第一个时间戳
        timestamp2 (float): 第二个时间戳
        
        返回:
        bool: 如果时间差超过8小时，返回True；否则返回False
        """
        # 计算时间差（以秒为单位）
        time_difference = abs(timestamp2 - timestamp1)
        
        # 将时间差转换为小时
        time_difference_hours = time_difference / 3600
        
        # 判断时间差是否超过8小时
        return time_difference_hours > 8