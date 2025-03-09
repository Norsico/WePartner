from Core.WxClient import WxChatClient
from config import Config


def main():
    config = Config('./config.json')
    wx_client = WxChatClient(config)

    # wx_client.send_text_message_by_name("N", "Hello, World!")

if __name__ == "__main__":
    main()
