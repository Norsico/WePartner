"""
wxChatBot 主程序入口
"""
from Core.Logger import Logger
from Core.initializer import SystemInitializer
from Core.web.web_init import WebInitializer


logger = Logger()


def main():
    """主程序入口"""
    logger.info("wxChatBot 正在启动...")

    initializer = SystemInitializer()
    web_initializer = WebInitializer('./config.json')

    # 初始化web
    web_initializer.initialize()
    logger.success(f"Web初始化完成，设置页面URL: {web_initializer.get_settings_url()}")
    # 系统初始化
    initializer.initialize()

if __name__ == "__main__":
    main()
