from Core.WxClient import WxChatClient
from Core.factory.client_factory import ClientFactory
from config import Config


def main():
    # 创建配置
    config = Config('./config.json')
    
    # 获取客户端并登录（如果需要）
    # client = config.get_gewechat_client()
    
    # 创建WxChatClient
    wx_client = WxChatClient(config)

    # 示例：发送消息
    # wx_client.send_text_message_by_name("N", "Hello, World!")

if __name__ == "__main__":
    main()
