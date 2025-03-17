"""
设置命令处理器
用于打开Web界面进行系统配置
"""
from Core.commands.base_command import BaseCommand
from Core.Logger import Logger
from Core.web.settings_app import get_settings_app

logging = Logger()


class SettingCommand(BaseCommand):
    """设置命令处理器，打开Web设置界面"""
    
    @property
    def name(self):
        """命令名称"""
        return "设置"
        
    @property
    def description(self):
        """命令描述"""
        return "打开Web界面进行系统设置"
        
    @property
    def aliases(self):
        """命令别名"""
        return ["setting", "config"]
        
    @property
    def usage(self):
        """命令用法"""
        return "#设置"
        
    def execute(self):
        """
        执行设置命令，启动Web设置界面并发送访问链接
        
        Returns:
            执行结果
        """
        master_name = self.config.get('master_name')
        
        try:
            # 获取设置界面url
            settings_url = self.config.get('settings_url')
            
            # 发送设置链接
            welcome_text = f"设置界面url: {settings_url}"
            
            self.channel.send_text_message_by_name(master_name, welcome_text)
            logging.success(f"已发送设置Web界面链接: {settings_url}")
            
            return "success"
        except Exception as e:
            error_msg = f"启动设置界面失败: {str(e)}"
            self.channel.send_text_message_by_name(master_name, f"错误: {error_msg}")
            logging.error(error_msg)
            return "error" 