from Core.Logger import Logger
from Core.bridge.context import ContextType, Context
from Core.commands.command_manager import CommandManager
from Core.DifyAI.workflow_manager import WorkflowManager
from Core.DifyAI.workflow_registry import WorkflowType, WorkflowFeature
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
        
        # 初始化工作流管理器（使用单例模式）
        self.workflow_manager = WorkflowManager.get_instance(config.get('dify_api_base'))
        logging.debug("已获取工作流管理器实例")

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
                # 获取当前默认工作流ID
                default_workflow_id = self.config.get('current_workflow', 'chat')
                
                # 解析消息内容
                message_info = self._parse_message(message)
                
                # 根据消息类型选择合适的工作流
                workflow = self._select_workflow_for_message(message_info, default_workflow_id)
                
                if workflow is None:
                    raise KeyError(f"找不到合适的工作流处理此消息")
                
                # 根据消息类型处理消息
                response = self._process_message_with_workflow(workflow, message_info)
                
                if isinstance(response, str):
                    # 发送工作流的响应
                    master_name = self.config.get('master_name')
                    self.send_text_message_by_name(master_name, response)
                    logging.info(f"已发送工作流响应")
                else:
                    # 如果工作流执行失败，发送默认回复
                    default_reply = self.config.get('default_reply', '收到您的消息，稍后回复。')
                    master_name = self.config.get('master_name')
                    self.send_text_message_by_name(master_name, default_reply)
                    logging.info(f"工作流执行失败，已发送默认回复")
            except KeyError as e:
                # 如果找不到当前工作流，发送默认回复
                default_reply = self.config.get('default_reply', '收到您的消息，稍后回复。')
                master_name = self.config.get('master_name')
                self.send_text_message_by_name(master_name, default_reply)
                logging.info(f"工作流错误: {str(e)}，已发送默认回复")
            except Exception as e:
                logging.error(f"处理消息时出错: {str(e)}")
                # 发送默认回复
                default_reply = self.config.get('default_reply', '收到您的消息，稍后回复。')
                master_name = self.config.get('master_name')
                self.send_text_message_by_name(master_name, default_reply)
                
            return "success"
            
    def _parse_message(self, message):
        """
        解析消息内容
        
        Args:
            message: 消息内容
            
        Returns:
            dict: 解析后的消息信息
        """
        message_info = {
            "type": "text",  # 默认为文本消息
            "content": message,  # 原始消息内容
            "text": message,  # 文本部分
            "file_path": None,  # 文件路径
            "file_type": None,  # 文件类型
            "needs_history": False  # 是否需要聊天历史
        }
        
        # 检查是否是文件上传请求
        file_match = re.match(r'^#(?:文件|file)\s+(.+)$', message)
        if file_match:
            file_path = file_match.group(1).strip()
            if os.path.exists(file_path):
                message_info["type"] = "file"
                message_info["file_path"] = file_path
                message_info["file_type"] = self._get_file_type(file_path)
                message_info["text"] = f"请分析这个{message_info['file_type']}文件"
            else:
                message_info["text"] = f"文件 {file_path} 不存在"
                
        # 检查是否是图片分析请求
        image_match = re.match(r'^#(?:图片|image)\s+(.+)$', message)
        if image_match:
            image_path = image_match.group(1).strip()
            if os.path.exists(image_path):
                message_info["type"] = "image"
                message_info["file_path"] = image_path
                message_info["file_type"] = "image"
                message_info["text"] = "请分析这张图片"
            else:
                message_info["text"] = f"图片 {image_path} 不存在"
                
        # 检查是否需要聊天历史
        if "上下文" in message or "历史" in message or "context" in message.lower() or "history" in message.lower():
            message_info["needs_history"] = True
            
        return message_info
            
    def _select_workflow_for_message(self, message_info, default_workflow_id):
        """
        根据消息内容选择合适的工作流
        
        Args:
            message_info: 解析后的消息信息
            default_workflow_id: 默认工作流ID
            
        Returns:
            Dify: 工作流实例
        """
        # 根据消息类型选择工作流
        if message_info["type"] == "file":
            # 需要文件上传功能的工作流
            workflow = self.workflow_manager.get_workflow_by_feature(
                WorkflowFeature.FILE_UPLOAD, 
                default_workflow_id
            )
            if workflow:
                logging.info(f"已选择支持文件上传的工作流处理消息")
                return workflow
                
        elif message_info["type"] == "image":
            # 需要图片处理功能的工作流
            workflow = self.workflow_manager.get_workflow_by_feature(
                WorkflowFeature.IMAGE_INPUT, 
                default_workflow_id
            )
            if workflow:
                logging.info(f"已选择支持图片处理的工作流处理消息")
                return workflow
                
        # 检查消息是否是数据分析请求
        if message_info["text"].startswith("#分析") or message_info["text"].startswith("#analysis"):
            # 数据分析型工作流
            workflow = self.workflow_manager.get_workflow_by_type(
                WorkflowType.ANALYSIS, 
                default_workflow_id
            )
            if workflow:
                logging.info(f"已选择数据分析型工作流处理消息")
                return workflow
                
        # 检查是否需要聊天历史
        if message_info["needs_history"]:
            # 需要聊天历史功能的工作流
            workflow = self.workflow_manager.get_workflow_by_feature(
                WorkflowFeature.CHAT_HISTORY, 
                default_workflow_id
            )
            if workflow:
                logging.info(f"已选择支持聊天历史的工作流处理消息")
                return workflow
                
        # 默认使用聊天型工作流
        try:
            workflow = self.workflow_manager.get_workflow(default_workflow_id)
            logging.info(f"已选择默认工作流 '{default_workflow_id}' 处理消息")
            return workflow
        except KeyError:
            # 如果默认工作流不存在，尝试获取任何聊天型工作流
            workflow = self.workflow_manager.get_workflow_by_type(WorkflowType.CHAT)
            if workflow:
                logging.info(f"默认工作流不存在，已选择聊天型工作流处理消息")
            return workflow
            
    def _process_message_with_workflow(self, workflow, message_info):
        """
        使用选定的工作流处理消息
        
        Args:
            workflow: 工作流实例
            message_info: 解析后的消息信息
            
        Returns:
            工作流执行结果
        """
        user = "user"  # 用户标识
        
        # 根据消息类型调用不同的处理方法
        if message_info["type"] == "file" and message_info["file_path"]:
            logging.info(f"使用文件处理方法处理消息")
            return workflow.run_workflow_with_file(
                message_info["text"],
                message_info["file_path"],
                message_info["file_type"],
                user
            )
        elif message_info["type"] == "image" and message_info["file_path"]:
            logging.info(f"使用图片处理方法处理消息")
            return workflow.run_workflow_with_image(
                message_info["text"],
                message_info["file_path"],
                user
            )
        elif message_info["needs_history"]:
            logging.info(f"使用带历史的处理方法处理消息")
            # TODO: 实现聊天历史获取逻辑
            history = []  # 这里应该从某个地方获取聊天历史
            return workflow.run_workflow_with_history(
                message_info["text"],
                history,
                user
            )
        else:
            # 普通文本消息
            logging.info(f"使用普通文本处理方法处理消息")
            return workflow.run_workflow(message_info["text"], user)
            
    def _get_file_type(self, file_path):
        """
        根据文件路径获取文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件类型
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in ['.txt', '.md', '.log']:
            return 'text'
        elif ext in ['.pdf']:
            return 'pdf'
        elif ext in ['.doc', '.docx']:
            return 'word'
        elif ext in ['.xls', '.xlsx']:
            return 'excel'
        elif ext in ['.ppt', '.pptx']:
            return 'powerpoint'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return 'image'
        elif ext in ['.mp3', '.wav', '.ogg']:
            return 'audio'
        elif ext in ['.mp4', '.avi', '.mov']:
            return 'video'
        else:
            return 'document'

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
