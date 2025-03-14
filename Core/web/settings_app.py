"""
基于Gradio的设置界面
提供图形化的配置管理
"""
import gradio as gr
import json
import os
import threading
import time
from pyngrok import ngrok
from typing import List, Dict, Tuple

from Core.Logger import Logger
from Core.difyAI.dify_manager import DifyManager
from config import Config
from .settings_manager import SettingsManager

logger = Logger()

class SettingsApp:
    def __init__(self):
        """初始化设置应用"""
        self.config = Config()
        self.settings_manager = SettingsManager()
        self.dify_manager = DifyManager()
        self.interface = None
        self.public_url = None
        self.ngrok_process = None
        self.settings_path = "/wxChatBot/settings"
        self.is_running = False
        
    def _load_chatflow_info(self) -> List[Dict]:
        """加载所有chatflow信息"""
        instances = self.dify_manager.list_instances()
        # 确保每个实例都包含完整的conversations信息
        for instance in instances:
            description = instance.get("description", "")
            if description:
                dify_instance = self.dify_manager.get_instance_by_name(description)
                if dify_instance:
                    conversations = dify_instance.list_conversations()
                    logger.info(f"加载对话列表 - 描述: {description}, 对话: {conversations}")
                    instance["conversations"] = conversations
        return instances
        
    def _get_chatflow_by_description(self, description: str) -> Dict:
        """根据描述获取chatflow信息"""
        instance = self.dify_manager.get_instance_by_name(description)
        if instance:
            info = instance.get_api_key_info()
            info["description"] = description
            info["api_key"] = instance.api_key
            info["base_url"] = instance.base_url
            info["conversations"] = instance.list_conversations()
            return info
        return {}
        
    def _create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="wxChatBot 设置", theme=gr.themes.Soft(), analytics_enabled=False) as interface:
            # 标题和说明
            gr.Markdown(
                """
                # 🤖 wxChatBot 配置管理
                
                在这里您可以配置wxChatBot的聊天设置。所有修改会立即生效。
                """
            )
            
            # 加载当前设置和chatflow信息
            current_settings = self.settings_manager.get_settings()
            current_chatflow = current_settings.get("selected_chatflow", {})
            current_description = current_chatflow.get("description", "")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Chatflow选择
                    chatflow_info = self._load_chatflow_info()
                    descriptions = [info.get("description", "") for info in chatflow_info if info.get("description")]
                    
                    # 获取初始API Key和对话列表
                    initial_api_key = ""
                    initial_conversations = []
                    current_conv_name = ""
                    
                    if current_description and current_description in descriptions:
                        # 从chatflow_info中获取当前选中的chatflow信息
                        for info in chatflow_info:
                            if info.get("description") == current_description:
                                initial_api_key = info.get("api_key", "")
                                initial_conversations = list(info.get("conversations", {}).keys()) if info.get("conversations") else []
                                # 如果当前有选中的对话，检查是否在对话列表中
                                current_conv = current_chatflow.get("conversation", {})
                                temp_conv_name = current_conv.get("name", "")
                                if temp_conv_name in initial_conversations:
                                    current_conv_name = temp_conv_name
                                break
                    
                    selected_chatflow = gr.Dropdown(
                        choices=descriptions,
                        value=current_description if current_description in descriptions else None,
                        label="Dify聊天机器人",
                        info="请选择一个聊天机器人...",
                        container=True  
                    )
                    
                    # API Key显示
                    api_key_text = gr.Textbox(
                        value=initial_api_key,
                        label="API Key",
                        info="当前选中的机器人的API Key",
                        interactive=False,
                        container=True
                    )
                    
                    # 对话选择
                    conversation_select = gr.Dropdown(
                        choices=initial_conversations,
                        value=current_conv_name if current_conv_name in initial_conversations else None,
                        label="选择对话",
                        info="选择一个要使用的对话",
                        container=True,
                        allow_custom_value=True
                    )
                    
                    # 语音设置
                    voice_enabled = gr.Checkbox(
                        value=self.settings_manager.is_voice_reply_enabled(),
                        label="启用语音回复",
                        info="是否将AI回复转换为语音",
                        container=True
                            )
            
            # 保存按钮和结果显示
            with gr.Row():
                save_button = gr.Button("💾 保存设置", variant="primary", scale=2)
            
            result_text = gr.Textbox(
                label="操作结果",
                interactive=False,
                container=True
            )
            
            # 更新chatflow信息
            def update_chatflow_info(description: str) -> Tuple[str, List[str]]:
                if not description:
                    return "", []
                
                logger.info(f"更新chatflow信息 - 描述: {description}")
                
                # 获取chatflow实例
                instance = self.dify_manager.get_instance_by_name(description)
                if not instance:
                    logger.warning(f"未找到chatflow实例: {description}")
                    return "", []
                
                # 获取对话列表
                conversations = instance.list_conversations()
                logger.info(f"获取到对话列表: {conversations}")
                
                # 确保返回正确的格式
                api_key = instance.api_key
                conversation_list = list(conversations.keys()) if isinstance(conversations, dict) else []
                
                logger.info(f"返回结果 - API Key: {api_key}, 对话列表: {conversation_list}")
                return api_key, conversation_list
            
            selected_chatflow.change(
                fn=update_chatflow_info,
                inputs=[selected_chatflow],
                outputs=[api_key_text, conversation_select],
                queue=False
            )
            
            # 保存设置
            def save_settings(description: str, conversation_name: str, voice_enabled: bool) -> str:
                if not description:
                    return "❌ 请选择一个聊天机器人"
                if not conversation_name:
                    return "❌ 请选择一个对话"
                
                # 如果conversation_name是列表，取第一个元素
                if isinstance(conversation_name, list):
                    conversation_name = conversation_name[0] if conversation_name else ""
                    
                logger.info(f"保存设置 - 描述: {description}, 对话名称: {conversation_name}, 语音: {voice_enabled}")
                
                try:
                    # 获取chatflow实例
                    instance = self.dify_manager.get_instance_by_name(description)
                    if not instance:
                        return "❌ 无法找到选中的聊天机器人信息"
                    
                    # 获取对话列表
                    conversations = instance.list_conversations()
                    logger.info(f"当前对话列表: {conversations}")
                    
                    # 获取对话ID
                    conversation_id = conversations.get(conversation_name) if isinstance(conversations, dict) else None
                    if not conversation_id:
                        return "❌ 无法获取对话ID，请重新选择对话"
                    
                    logger.info(f"找到对话ID: {conversation_id}")
                    
                    # 更新chatflow设置
                    if not self.settings_manager.set_selected_chatflow(description, instance.api_key, conversation_name, conversation_id):
                        return "❌ 保存chatflow设置失败"
                    
                    # 更新语音设置
                    if not self.settings_manager.set_voice_reply_enabled(voice_enabled):
                        return "❌ 保存语音设置失败"
                    
                    return "✅ 设置已保存！"
                    
                except Exception as e:
                    logger.error(f"保存设置时出错: {str(e)}")
                    return f"❌ 保存设置失败: {str(e)}"
            
            save_button.click(
                fn=save_settings,
                inputs=[selected_chatflow, conversation_select, voice_enabled],
                outputs=[result_text],
                queue=False
            )
            
        return interface
        
    def start(self, port=7860):
        """启动设置应用"""
        if self.is_running:
            return self.public_url
            
        # 创建界面
        self.interface = self._create_interface()
        
        # 检查是否需要使用Ngrok
        is_remote_server = self.config.get("is_remote_server", False)
        
        if not is_remote_server:
            # 在本地模式下使用Ngrok
            ngrok_auth_token = self.config.get("ngrok_auth_token")
            
            if ngrok_auth_token:
                try:
                    # 设置Ngrok认证
                    ngrok.set_auth_token(ngrok_auth_token)
                    
                    # 先关闭所有现有的Ngrok隧道
                    try:
                        tunnels = ngrok.get_tunnels()
                        for tunnel in tunnels:
                            logger.info(f"关闭现有Ngrok隧道: {tunnel.public_url}")
                            ngrok.disconnect(tunnel.public_url)
                    except Exception as disconnect_err:
                        logger.warning(f"关闭现有Ngrok隧道时出错: {str(disconnect_err)}")
                    
                    # 添加重试机制
                    max_retries = 3
                    retry_count = 0
                    
                    while retry_count < max_retries:
                        try:
                            # 启动Ngrok隧道
                            public_url = ngrok.connect(port, bind_tls=True).public_url
                            break
                        except Exception as connect_err:
                            retry_count += 1
                            if retry_count >= max_retries:
                                raise
                            logger.warning(f"Ngrok连接失败，正在重试 ({retry_count}/{max_retries}): {str(connect_err)}")
                            time.sleep(2)
                    
                    self.public_url = public_url
                    logger.success(f"Ngrok隧道已建立，公共URL: {self.public_url}")
                except Exception as e:
                    logger.error(f"Ngrok隧道建立失败: {str(e)}")
                    self.public_url = f"http://localhost:{port}"
            else:
                logger.warning("未设置Ngrok认证令牌，使用本地URL")
                self.public_url = f"http://localhost:{port}"
        else:
            # 在远程服务器模式下，直接使用服务器URL
            server_host = self.config.get("server_host", "localhost")
            self.public_url = f"http://{server_host}:{port}"
            
        # 在新线程中启动Gradio界面
        def run_interface():
            self.interface.launch(
                server_name="0.0.0.0",
                server_port=port,
                share=False,
                inbrowser=False,
                debug=False,
                root_path=self.settings_path if self.settings_path != "/" else None
            )
            
        thread = threading.Thread(target=run_interface, daemon=True)
        thread.start()
        
        time.sleep(2)
        self.is_running = True
        logger.success(f"设置界面已启动，访问URL: {self.public_url}")
        
        return self.public_url
        
    def stop(self):
        """停止设置应用"""
        if not self.is_running:
            return
            
        if self.ngrok_process:
            ngrok.disconnect(self.public_url)
            
        self.is_running = False
        logger.info("设置界面已关闭")

# 单例模式，确保全局只有一个设置应用实例
_instance = None

def get_settings_app():
    """获取设置应用实例"""
    global _instance
    if _instance is None:
        _instance = SettingsApp()
    return _instance 