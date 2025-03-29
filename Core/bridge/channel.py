from Core.Logger import Logger
from Core.commands.command_manager import CommandManager
from Core.web_app.settings_manager import SettingsManager
from Core.voice.audio_convert import wav_to_silk
from Core.voice.audio_gen import AudioGen
from Core.difyAI.dify_manager import DifyManager

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
        self.settings_manager = SettingsManager()
        self.current_settings = self.settings_manager.get_settings()

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
            # 从settings.json中获取当前选中的chatflow
            chatflow_description = self.current_settings.get("selected_chatflow", {}).get("description", "")
            # 获取是否启用了语音回复
            voice_reply_enabled = self.current_settings.get("voice_reply_enabled", False)
            # 调试输出
            logging.debug(f"当前选中的chatflow: {chatflow_description}")
            logging.debug(f"是否启用了语音回复: {voice_reply_enabled}")

            dify_client = DifyManager().get_instance_by_name(self.current_settings.get("selected_chatflow", {}).get("description", ""))

            logging.debug(f"当前选中的chatflow: {dify_client.list_conversations()}")

            # 继续已有对话
            response = dify_client.chat(query=message, conversation_name=self.current_settings.get("selected_chatflow", {}).get("conversation", {}).get("name", "")).get('answer')
            logging.info(f"AI生成的回复: {response}\n")
                
            try:
                # 发送回复
                master_name = self.config.get('master_name')
                if voice_reply_enabled:
                    # 使用GPT-SoVITS生成语音，转换为silk格式后即可发送
                    audio_gen = AudioGen()
                    audio_path = audio_gen.generate_voice(response)
                    silk_path = audio_path + '.silk'
                    duration = wav_to_silk(audio_path, silk_path)
                    callback_url = self.config.get("gewechat_callback_url")
                    silk_url = callback_url + "?file=" + silk_path
                    self.client.post_voice(self.gewechat_app_id, self.get_wxid_by_name(master_name), silk_url, duration)
                    logging.info(f"[gewechat] Do send voice to {master_name}: {silk_url}, duration: {duration / 1000.0} seconds")
                else:
                    self.send_text_message_by_name(master_name, response)
                logging.info(f"已发送回复")
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
