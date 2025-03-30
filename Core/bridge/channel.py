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

            # 处理消息
            response = dify_client.chat(query=message,
                                         conversation_name=self.current_settings
                                         .get("selected_chatflow", {})
                                         .get("conversation", {})
                                         .get("name", "")
                                         )

            res = dify_client.handle_response(response)

            # 继续已有对话
            
            for r in res:
                if r['type'] == 'text':
                    self.handle_text(r['content'])
                elif r['type'] == 'voice':
                    self.handle_voice(r['content'])


            # if res['type'] == 'text':
           
            return "success"

    def handle_text(self, text):
        try:
            # 发送回复
            master_name = self.config.get('master_name')
            self.send_text_message_by_name(master_name, text)
            logging.info(f"已发送回复")
            return "success"
            
        except Exception as e:
            logging.error(f"处理消息时出错: {str(e)}")
            return "error"

    def handle_voice(self, voice_url):
        """
        处理语音消息
        
        Args:
            voice_url: 语音文件的URL
            
        Returns:
            处理结果
        """
        try:
            import os
            import requests
            import uuid
            from Core.bridge.temp_dir import TmpDir
            
            # 创建临时目录
            tmp_dir = TmpDir().path()

            logging.debug(f"tmp_dir路径: {tmp_dir}")
            # 生成唯一的文件名
            file_name = f"{uuid.uuid4()}"
            relative_voice_file = f"voice_{file_name}.wav"
            audio_path = os.path.join(tmp_dir, relative_voice_file)
            # 下载语音文件
            logging.info(f"正在下载语音文件: {voice_url}")
            response = requests.get(voice_url)
            if response.status_code != 200:
                logging.error(f"下载语音文件失败: {response.status_code}")
                return "error"
            # 保存为WAV文件
            with open(audio_path, "wb") as f:
                f.write(response.content)
            audio_path = os.path.abspath(audio_path)
            logging.info(f"语音文件已保存至: {audio_path}")

            silk_path = audio_path + '.silk'
            
            # 转换为silk格式
            duration = wav_to_silk(audio_path, silk_path)
            
            # 发送语音消息
            master_name = self.config.get('master_name')
            callback_url = self.config.get("gewechat_callback_url")
            silk_url = callback_url + "?file=" + str(silk_path)
            
            wxid = self.get_wxid_by_name(master_name)
            if not wxid:
                logging.error(f"未找到用户 {master_name} 的wxid，无法发送语音")
                return "error"
                
            # 发送语音消息
            self.client.post_voice(self.gewechat_app_id, wxid, silk_url, duration)
            logging.info(f"[gewechat] 已发送语音到 {master_name}: {silk_url}, 时长: {duration / 1000.0} 秒")
            
            return "success"
            
        except Exception as e:
            logging.error(f"处理语音消息时出错: {str(e)}")
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
