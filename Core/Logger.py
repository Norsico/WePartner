import datetime


def _get_timestamp():
    """获取当前时间戳"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Logger:
    """
    使用 print 实现带有颜色的日志输出。
    """
    # 定义颜色代码
    ICE_CRYSTAL_BLUE = "\033[94m"  # 浅蓝色
    RESET_COLOR = "\033[0m"  # 重置颜色
    GREEN = "\033[92m"  # 绿色
    YELLOW = "\033[93m"  # 黄色
    RED = "\033[91m"  # 红色
    
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

    _instance = None
    _current_level = LEVEL_INFO  # 默认日志级别为INFO
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 自动获取当前类的名称作为日志名称
        self.name = self.__class__.__name__
    
    @classmethod
    def set_level(cls, level):
        """设置日志级别"""
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

    def log(self, level, message):
        """通用日志方法"""
        level_value = self.LEVEL_MAP.get(level, 0)
        if level_value >= self._current_level:
            timestamp = _get_timestamp()
            if level == "DEBUG":
                color = "\033[96m"  # 青色
            elif level == "SUCCESS":
                color = self.GREEN
            elif level == "WARNING":
                color = self.YELLOW
            elif level == "ERROR":
                color = self.RED
            else:
                color = self.ICE_CRYSTAL_BLUE  # 默认颜色
            print(f"{color}{timestamp} - {self.name} - {level}{self.RESET_COLOR} - {message}")

    def debug(self, message):
        """输出 DEBUG 级别的日志"""
        self.log("DEBUG", message)

    def info(self, message):
        """输出 INFO 级别的日志"""
        self.log("INFO", message)

    def warning(self, message):
        """输出 WARNING 级别的日志"""
        self.log("WARNING", message)

    def error(self, message):
        """输出 ERROR 级别的日志"""
        self.log("ERROR", message)

    def success(self, message):
        """输出 SUCCESS 级别的日志"""
        self.log("SUCCESS", message)
