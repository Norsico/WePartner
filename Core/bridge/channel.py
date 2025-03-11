from Core.Logger import Logger
from Core.bridge.context import ContextType, Context
from Core.commands.command_manager import CommandManager
import os
import re

logging = Logger()

class Channel:
    def __init__(self, client, config):
        """
        初始化通信通道
        
        Args:
            client: 微信客户端API
            config: 配置对象
        """
        self.client = client
        self.config = config
        self.gewechat_app_id = config.get('gewechat_app_id')
        
        # 初始化命令管理器
        self.command_manager = CommandManager(self)

    def compose_context(self, message):
        """
        处理接收到的消息
        
        Args:
            message: 消息内容
            
        Returns:
            处理结果
        """
        logging.info(f"收到消息: {message}")
        
        # 判断是否为设置命令
        if message.lower() in ["#设置", "#setting", "#config"]:
            logging.info("检测到设置命令")
            result = self.command_manager.execute_setting_command()
            logging.info(f"命令处理结果: {result}")
            return result
        else:
            # 处理普通消息
            logging.info("检测到普通消息")
            # 检查是否启用了自动回复
            if not self.config.get('auto_reply_enabled', False):
                logging.info("自动回复未启用，忽略普通消息")
                return "ignored"
                
            try:
                # 发送默认回复
                default_reply = self.config.get('default_reply', '收到您的消息，稍后回复。')
                master_name = self.config.get('master_name')
                self.send_text_message_by_name(master_name, default_reply)
                logging.info(f"已发送默认回复")
                return "success"
            except Exception as e:
                logging.error(f"处理消息时出错: {str(e)}")
                return "error"

    def send_text_message_by_name(self, name, message):
        """
        通过昵称发送文本消息
        
        Args:
            name: 接收者昵称
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        wxid = self.get_wxid_by_name(name)
        if not wxid:
            logging.error(f"未找到用户 {name} 的wxid，无法发送消息")
            return False
            
        # 发送消息
        send_msg_result = self.client.post_text(self.gewechat_app_id, wxid, message)
        if send_msg_result.get('ret') != 200:
            logging.error(f"发送消息失败: {send_msg_result}")
            return False
        logging.success(f"发送消息成功: {message}")
        return True

    def get_wxid_by_name(self, name):
        """
        通过昵称获取微信ID
        
        Args:
            name: 用户昵称
            
        Returns:
            微信ID
        """
        try:
            # 获取好友列表
            fetch_contacts_list_result = self.client.fetch_contacts_list(self.gewechat_app_id)
            if fetch_contacts_list_result.get('ret') != 200 or not fetch_contacts_list_result.get('data'):
                logging.error(f"获取好友列表失败: {fetch_contacts_list_result}")
                return None
            friends = fetch_contacts_list_result['data'].get('friends', [])
            if not friends:
                logging.error("获取到的好友列表为空")
                return None
                
            # 获取好友的简要信息
            friends_info = self.client.get_brief_info(self.gewechat_app_id, friends)
            if friends_info.get('ret') != 200 or not friends_info.get('data'):
                logging.error(f"获取好友简要信息失败: {friends_info}")
                return None
                
            # 查找目标好友的wxid
            friends_info_list = friends_info['data']
            if not friends_info_list:
                logging.error("获取到的好友简要信息列表为空")
                return None
                
            # 查找匹配昵称的好友
            for friend_info in friends_info_list:
                if friend_info.get('nickName') == name:
                    wxid = friend_info.get('userName')
                    logging.success(f"找到好友: {name} 的wxid: {wxid}")
                    return wxid
                    
            logging.error(f"没有找到好友: {name} 的wxid")
            return None
        except Exception as e:
            logging.error(f"获取好友wxid失败: {e}")
            return None
