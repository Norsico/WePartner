from Core.WxClient import WxChatClient
from Core.factory.client_factory import ClientFactory
from Core.Logger import Logger
from config import Config
import time
import platform
import subprocess
import sys


def check_dependencies():
    """检查并安装必要的依赖"""
    logger = Logger()
    required_packages = ["gradio", "pyngrok"]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            logger.warning(f"缺少必要依赖: {package}，开始安装...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.success(f"成功安装依赖: {package}")
            except Exception as e:
                logger.error(f"安装依赖 {package} 失败: {str(e)}")
                logger.info(f"请手动安装: pip install {package}")


def main():
    # 检查依赖
    check_dependencies()
    
    # 创建日志记录器
    logger = Logger()
    logger.info("wxChatBot 正在启动...")
    
    # 记录启动时间
    start_time = time.time()
    
    # 创建配置
    config = Config('./config.json')
    
    # 设置启动时间
    config.set('start_time', start_time)
    
    # 自动检测运行环境
    system_info = platform.system()
    is_remote_server = config.get('is_remote_server')
    
    # 如果未设置运行环境，根据系统自动判断
    if is_remote_server is None:
        # 如果是Linux系统，默认认为是远程服务器
        is_remote_server = system_info == "Linux"
        config.set('is_remote_server', is_remote_server)
        logger.info(f"自动检测运行环境: {'远程服务器' if is_remote_server else '本地机器'}")
    
    # 确保设置了master_name
    if not config.get('master_name'):
        logger.warning("未设置master_name，将使用默认值")
        config.set('master_name', 'filehelper')  # 默认使用文件传输助手
    
    # 创建WxChatClient
    logger.info("正在初始化微信客户端...")
    wx_client = WxChatClient(config)
    logger.success("微信客户端初始化完成")
    
    # 注意：WxClient.set_wx_callback方法已经包含了一个无限循环
    # 所以这里不需要再添加循环，程序会在WxClient中保持运行
    logger.info("wxChatBot 已启动，按Ctrl+C退出")


if __name__ == "__main__":
    main()
