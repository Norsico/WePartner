from Core.Logger import Logger
from Core.commands.command_manager import CommandManager
from Core.web_app.settings_manager import SettingsManager
from Core.voice.audio_convert import audio_to_silk
from Core.cozeAI.coze_manager import CozeChatManager
import os

# 获取当前脚本文件的绝对路径
current_file_path = os.path.abspath(__file__)

# 获取tmp路径
tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))), "tmp")

from Core.difyAI.dify_manager import DifyManager

logging = logger = Logger()

def cleanup_tmp_folder():
    """清理tmp文件夹中的所有文件"""
    logger.info("正在清理tmp文件夹...")
    tmp_path = tmp_dir
    
    try:
        # 获取tmp文件夹中的所有文件
        files = [f for f in os.listdir(tmp_path) if os.path.isfile(os.path.join(tmp_path, f))]
        
        # 删除每个文件
        for file in files:
            file_path = os.path.join(tmp_path, file)
            try:
                os.remove(file_path)
                logger.debug(f"已删除临时文件: {file}")
            except Exception as e:
                logger.error(f"删除文件 {file} 时出错: {str(e)}")
        
        logger.success(f"已清理 {len(files)} 个临时文件")
    except Exception as e:
        logger.error(f"清理tmp文件夹时出错: {str(e)}")

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

        # 初始化coze
        self.coze_manager = CozeChatManager(api_token=self.config.get("coze_api_token"))

    def compose_context(self, message, _wxid):
        """
        处理接收到的消息
        
        Args:
            message: 消息内容
            
        Returns:
            处理结果
        """
        logging.info(f"收到消息: {message}")
        # 判断平台
        if self.config.get("agent_platform") == "dify":
            self._handle_dify(message, _wxid)
        elif self.config.get("agent_platform") == "coze":
            self._handle_coze(message, _wxid)

        return "success"
    
    def _handle_coze(self, meseage, _wxid):
        response = self.coze_manager.chat_with_bot(
            bot_id=self.config.get("coze_agent_id"), 
            wxid=_wxid,
            user_message=meseage
        )
        res = self.coze_manager.handle_response(response)
        
        if res:
            # 继续已有对话
            for r in res:
                if r['type'] == 'text':
                    self.handle_text(r['content'], _wxid)
                elif r['type'] == 'voice':
                    self.handle_voice(r['content'], _wxid)
                    cleanup_tmp_folder()
        else:
            print(f"maybe no res:{res}")
    
    def _handle_dify(self, message, _wxid):
        self.settings_manager._update_settings()
        self.current_settings = self.settings_manager.get_settings()

        # 处理普通消息
        logging.info("检测到普通消息")
        # 从settings.json中获取当前选中的chatflow
        chatflow_description = self.current_settings.get("selected_chatflow", {}).get("description", "")
        # 获取是否启用了语音回复
        voice_reply_enabled = self.current_settings.get("voice_reply_enabled", False)
        # 调试输出
        print(f"当前选中的chatflow: {chatflow_description}")
        print(f"是否启用了语音回复: {voice_reply_enabled}")
        dify_client = DifyManager().get_instance_by_name(self.current_settings.get("selected_chatflow", {}).get("description", ""))
        print(f"当前选中的chatflow: {dify_client.list_conversations()}")
        # 处理消息
        response = dify_client.chat(query=message,
                                    conversation_name=self.current_settings
                                    .get("selected_chatflow", {})
                                     .get("conversation", {})
                                    .get("name", "")
                                    )
        res = dify_client.handle_response(response)
        if res:
            # 继续已有对话
            for r in res:
                if r['type'] == 'text':
                    self.handle_text(r['content'], _wxid)
                elif r['type'] == 'voice':
                    self.handle_voice(r['content'], _wxid)
                    cleanup_tmp_folder()
        else:
            print(f"maybe no res:{res}")

    def handle_text(self, text, _wxid):
        try:
            # 发送回复
            print(f"微信id:{_wxid}")
            self.send_text_message_by_wxid(_wxid, text)
            logging.info(f"已发送回复")
            return "success"
            
        except Exception as e:
            logging.error(f"处理消息时出错: {str(e)}")
            return "error"

    def handle_voice(self, voice_url, _wxid):
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
            duration = audio_to_silk(audio_path, silk_path)
            
            # 发送语音消息
            callback_url = f"http://{self.config.get('gewe_server_ip')}:1145/v2/api/callback/collect"
            print(f"callback_url: {callback_url}")
            silk_url = callback_url + "?file=" + str(silk_path)
                
            # 发送语音消息
            self.client.post_voice(self.gewechat_app_id, _wxid, silk_url, duration)
            logging.info(f"[gewechat] 已发送语音到 {_wxid}: {silk_url}, 时长: {duration / 1000.0} 秒")
            
            return "success"
            
        except Exception as e:
            logging.error(f"处理语音消息时出错: {str(e)}")
            return "error"
        
    def send_text_message_by_wxid(self, wxid, message):
        # 发送消息
        send_msg_result = self.client.post_text(self.gewechat_app_id, wxid, message)
        if send_msg_result.get('ret') != 200:
            logging.error(f"发送消息失败: {send_msg_result}")
            return False
        logging.success(f"发送消息成功: {message}")
        return True

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
