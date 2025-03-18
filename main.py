"""
wxChatBot 主程序入口
"""
import os
import signal
import sys
from Core.Logger import Logger
from Core.initializer import SystemInitializer
from Core.web.web_init import WebInitializer
from Core.bridge.temp_dir import TmpDir


logger = Logger()
tmp_dir = TmpDir()


def cleanup_tmp_folder():
    """清理tmp文件夹中的所有文件"""
    logger.info("正在清理tmp文件夹...")
    tmp_path = tmp_dir.path()
    
    try:
        # 获取tmp文件夹中的所有文件
        files = [f for f in os.listdir(tmp_path) if os.path.isfile(os.path.join(tmp_path, f))]
        
        # 删除每个文件
        for file in files:
            file_path = os.path.join(tmp_path, file)
            try:
                os.remove(file_path)
                logger.debug(f"已删除临时文件: {file}")
            except Exception as e:
                logger.error(f"删除文件 {file} 时出错: {str(e)}")
        
        logger.success(f"已清理 {len(files)} 个临时文件")
    except Exception as e:
        logger.error(f"清理tmp文件夹时出错: {str(e)}")


def signal_handler(sig, frame):
    """处理程序终止信号"""
    logger.info("接收到终止信号，正在清理资源...")
    cleanup_tmp_folder()
    sys.exit(0)


def main():
    """主程序入口"""
    logger.info("wxChatBot 正在启动...")
    
    # 注册信号处理程序
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    initializer = SystemInitializer()
    web_initializer = WebInitializer('./config.json')

    # 初始化web
    web_initializer.initialize()
    logger.success(f"Web初始化完成，设置页面URL: {web_initializer.get_settings_url()}")
    # 系统初始化
    initializer.initialize()
    
    try:
        # 让主程序保持运行，直到收到终止信号
        while True:
            signal.pause()
    except KeyboardInterrupt:
        # 捕获键盘中断
        cleanup_tmp_folder()
    except Exception as e:
        logger.error(f"程序异常终止: {str(e)}")
        cleanup_tmp_folder()

if __name__ == "__main__":
    main()
