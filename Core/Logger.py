import datetime
import os
import sys
from typing import Optional, TextIO


def _get_timestamp():
    """获取当前时间戳"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Logger:
    """
    增强的日志系统，支持控制台彩色输出和文件日志
    使用单例模式确保全局只有一个日志实例
    """
    # 定义颜色代码
    ICE_CRYSTAL_BLUE = "\033[94m"  # 浅蓝色
    RESET_COLOR = "\033[0m"  # 重置颜色
    GREEN = "\033[92m"  # 绿色
    YELLOW = "\033[93m"  # 黄色
    RED = "\033[91m"  # 红色
    CYAN = "\033[96m"  # 青色
    MAGENTA = "\033[95m"  # 紫色
    
    # 定义日志级别
    LEVEL_DEBUG = 10
    LEVEL_INFO = 20
    LEVEL_WARNING = 30
    LEVEL_ERROR = 40
    LEVEL_SUCCESS = 50
    
    # 日志级别映射
    LEVEL_MAP = {
        "DEBUG": LEVEL_DEBUG,
        "INFO": LEVEL_INFO,
        "WARNING": LEVEL_WARNING,
        "ERROR": LEVEL_ERROR,
        "SUCCESS": LEVEL_SUCCESS
    }
    
    # 日志级别对应的颜色
    LEVEL_COLORS = {
        "DEBUG": CYAN,
        "INFO": ICE_CRYSTAL_BLUE,
        "WARNING": YELLOW,
        "ERROR": RED,
        "SUCCESS": GREEN
    }

    _instance = None
    _current_level = LEVEL_INFO  # 默认日志级别为INFO
    _log_file: Optional[TextIO] = None
    _use_colors = True  # 是否使用彩色输出
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance

    def __init__(self):
        # 自动获取当前类的名称作为日志名称
        self.name = self.__class__.__name__
    
    def _setup(self):
        """初始化日志系统"""
        # 检查是否在Windows终端中运行
        if sys.platform == 'win32':
            # 启用Windows终端的ANSI转义序列支持
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
    @classmethod
    def set_level(cls, level):
        """
        设置日志级别
        
        Args:
            level: 可以是字符串('DEBUG', 'INFO'等)或整数(10, 20等)
        """
        if isinstance(level, str):
            level = level.upper()
            if level in cls.LEVEL_MAP:
                cls._current_level = cls.LEVEL_MAP[level]
            else:
                raise ValueError(f"无效的日志级别: {level}")
        elif isinstance(level, int):
            if level in [cls.LEVEL_DEBUG, cls.LEVEL_INFO, cls.LEVEL_WARNING, cls.LEVEL_ERROR, cls.LEVEL_SUCCESS]:
                cls._current_level = level
            else:
                raise ValueError(f"无效的日志级别值: {level}")
        else:
            raise TypeError("日志级别必须是字符串或整数")
    
    @classmethod
    def set_log_file(cls, file_path: str):
        """
        设置日志文件
        
        Args:
            file_path: 日志文件路径
        """
        if cls._log_file:
            cls._log_file.close()
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        cls._log_file = open(file_path, 'a', encoding='utf-8')
    
    @classmethod
    def set_use_colors(cls, use_colors: bool):
        """
        设置是否使用彩色输出
        
        Args:
            use_colors: 是否使用彩色输出
        """
        cls._use_colors = use_colors

    def log(self, level: str, message: str):
        """
        通用日志方法
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        level_value = self.LEVEL_MAP.get(level, 0)
        if level_value >= self._current_level:
            timestamp = _get_timestamp()
            
            # 构建日志消息
            color = self.LEVEL_COLORS.get(level, self.ICE_CRYSTAL_BLUE)
            log_message = f"{timestamp} - {self.name} - {level} - {message}"
            
            # 控制台输出（带颜色）
            if self._use_colors:
                print(f"{color}{log_message}{self.RESET_COLOR}")
            else:
                print(log_message)
            
            # 文件输出（不带颜色）
            if self._log_file:
                self._log_file.write(f"{log_message}\n")
                self._log_file.flush()

    def debug(self, message: str):
        """输出 DEBUG 级别的日志"""
        self.log("DEBUG", message)

    def info(self, message: str):
        """输出 INFO 级别的日志"""
        self.log("INFO", message)

    def warning(self, message: str):
        """输出 WARNING 级别的日志"""
        self.log("WARNING", message)

    def error(self, message: str):
        """输出 ERROR 级别的日志"""
        self.log("ERROR", message)

    def success(self, message: str):
        """输出 SUCCESS 级别的日志"""
        self.log("SUCCESS", message)
    
    def __del__(self):
        """确保在对象销毁时关闭日志文件"""
        if self._log_file:
            self._log_file.close()
