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

    def __init__(self):
        # 自动获取当前类的名称作为日志名称
        self.name = self.__class__.__name__

    def log(self, level, message):
        """通用日志方法"""
        timestamp = _get_timestamp()
        if level == "DEBUG":
            color = "\033[96m"  # 青色
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
        print(f"{self.YELLOW}{_get_timestamp()} - {self.name} - WARNING{self.RESET_COLOR} - {message}")

    def error(self, message):
        """输出 ERROR 级别的日志"""
        print(f"{self.RED}{_get_timestamp()} - {self.name} - ERROR{self.RESET_COLOR} - {message}")

    def success(self, message):
        """输出 SUCCESS 级别的日志"""
        print(f"{self.GREEN}{_get_timestamp()} - {self.name} - SUCCESS{self.RESET_COLOR} - {message}")
