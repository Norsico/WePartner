"""
命令处理器基类
所有命令处理器都应继承此类
"""
from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """
    命令处理器基类
    
    提供了命令处理器的基本结构和接口，所有具体的命令处理器都应继承此类并实现其抽象方法。
    """
    
    def __init__(self, channel):
        """
        初始化命令处理器
        
        Args:
            channel: 通信通道对象，用于发送消息等操作
        """
        self.channel = channel
        self.config = channel.config
        
    @property
    @abstractmethod
    def name(self):
        """
        命令名称
        
        Returns:
            命令的主要名称，用于识别和触发命令
        """
        pass
        
    @property
    @abstractmethod
    def description(self):
        """
        命令描述
        
        Returns:
            对命令功能的简短描述
        """
        pass
        
    @property
    def aliases(self):
        """
        命令别名列表
        
        Returns:
            命令的别名列表，用于通过不同名称触发同一个命令
        """
        return []
        
    @property
    def usage(self):
        """
        命令使用方法
        
        Returns:
            命令的使用格式说明
        """
        return f"#{self.name}"
        
    @abstractmethod
    def execute(self):
        """
        执行命令
        
        Returns:
            执行结果
        """
        pass 