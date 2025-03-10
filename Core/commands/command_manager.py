"""
命令管理器
专门用于管理设置命令
"""
from Core.Logger import Logger
from Core.commands.setting_command import SettingCommand

logging = Logger()


class CommandManager:
    """
    命令管理器
    简化版本，只管理设置命令
    """
    
    def __init__(self, channel):
        """
        初始化命令管理器
        
        Args:
            channel: 通信通道对象
        """
        self.channel = channel
        self.command = SettingCommand(channel)
        logging.success(f"已加载设置命令")
        
    def execute_setting_command(self):
        """
        执行设置命令
        
        Returns:
            执行结果
        """
        try:
            logging.info("执行设置命令")
            result = self.command.execute()
            logging.success("设置命令执行成功")
            return result
        except Exception as e:
            error_msg = f"执行设置命令时出错: {str(e)}"
            logging.error(error_msg)
            return "error" 