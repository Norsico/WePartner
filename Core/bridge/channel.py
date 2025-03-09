from Core.Logger import Logger

logging = Logger()


class Channel:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.gewechat_app_id = config.get('gewechat_app_id')

    def compose_context(self, message):
        print(f"消息: {message}")
        # 组装消息内容
        self.send_text_message_by_name('N', "???")

    def send_text_message_by_name(self, name, message):
        wxid = self.get_wxid_by_name(name)
        # 发送消息
        send_msg_result = self.client.post_text(self.gewechat_app_id, wxid, message)
        if send_msg_result.get('ret') != 200:
            print("发送消息失败:", send_msg_result)
            return
        print("发送消息成功:", send_msg_result)

    def get_wxid_by_name(self, name):
        try:

            # 获取好友列表
            fetch_contacts_list_result = self.client.fetch_contacts_list(self.gewechat_app_id)
            if fetch_contacts_list_result.get('ret') != 200 or not fetch_contacts_list_result.get('data'):
                logging.error(f"获取好友列表失败: {fetch_contacts_list_result}")
                return
            friends = fetch_contacts_list_result['data'].get('friends', [])
            if not friends:
                logging.error("获取到的好友列表为空")
                return
            logging.debug(f"获取到的好友列表: {friends}")
            # 获取好友的简要信息
            friends_info = self.client.get_brief_info(self.gewechat_app_id, friends)
            if friends_info.get('ret') != 200 or not friends_info.get('data'):
                logging.error(f"获取好友简要信息失败: {friends_info}")
                return
            # 找对目标好友的wxid
            friends_info_list = friends_info['data']
            if not friends_info_list:
                logging.error("获取到的好友简要信息列表为空")
                return
            wxid = None
            for friend_info in friends_info_list:
                if friend_info.get('nickName') == name:
                    wxid = friend_info.get('userName')
                    break
            if not wxid:
                logging.error(f"没有找到好友: {name} 的wxid")
                return
            logging.success(f"找到好友: {name} 的wxid: {wxid}")
            return wxid
        except Exception as e:
            logging.error(f"获取好友wxid失败: {e}")
            return None
