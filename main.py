"""
wxChatBot 主程序入口
"""
from Core.Logger import Logger
from Core.initializer import SystemInitializer

logger = Logger()


def main():
    """主程序入口"""
    logger.info("wxChatBot 正在启动...")
    
    # 系统初始化
    initializer = SystemInitializer()
    success, wx_client = initializer.initialize()
    
    if not success:
        logger.error("系统初始化失败，程序退出")
        return
    
    # 注意：WxClient.set_wx_callback方法已经包含了一个无限循环
    # 所以这里不需要再添加循环，程序会在WxClient中保持运行
    logger.info("wxChatBot 已启动，按Ctrl+C退出")


if __name__ == "__main__":
    main()
