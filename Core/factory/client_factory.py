from gewechat.client import GewechatClient
from Core.Logger import Logger

logging = Logger()

class ClientFactory:
    """
    GewechatClient工厂类，负责创建和管理GewechatClient实例
    使用单例模式确保全局只有一个客户端实例
    """
    _client_instance = None
    _is_logged_in = False
    
    @classmethod
    def get_client(cls, config):
        """
        获取GewechatClient实例
        如果实例不存在，则创建一个新实例
        
        :param config: 配置对象，包含gewechat_base_url和gewechat_token
        :return: GewechatClient实例
        """
        if cls._client_instance is None:
            base_url = config.get('gewechat_base_url')
            token = config.get('gewechat_token')
            
            if not base_url or not token:
                logging.error("缺少必要的配置参数：gewechat_base_url 或 gewechat_token")
                return None
                
            cls._client_instance = GewechatClient(base_url, token)
            logging.info(f"已创建GewechatClient实例，base_url: {base_url}")
        
        return cls._client_instance
    
    @classmethod
    def login_if_needed(cls, client, app_id, config):
        """
        如果需要，执行登录操作
        
        :param client: GewechatClient实例
        :param app_id: 应用ID
        :param config: 配置对象
        :return: 是否登录成功
        """
        if cls._is_logged_in:
            logging.info("客户端已登录，无需重复登录")
            return True
            
        app_id, error_msg = client.login(app_id=app_id)
        if error_msg:
            logging.error(f"登录失败: {error_msg}")
            return False
        else:
            logging.success(f"登录成功，app_id: {app_id}")
            cls._is_logged_in = True
            # 保存app_id
            config.set('gewechat_app_id', app_id)
            return True
    
    @classmethod
    def reset(cls):
        """
        重置工厂状态，用于测试或重新初始化
        """
        cls._client_instance = None
        cls._is_logged_in = False