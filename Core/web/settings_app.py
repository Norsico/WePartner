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

logger = Logger()

class SettingsApp:
    def __init__(self):
        """初始化设置应用"""
        self.config = Config()
        self.dify_manager = DifyManager()
        self.interface = None
        self.public_url = None
        self.ngrok_process = None
        self.settings_path = "/wxChatBot/settings"
        self.is_running = False
        
    def _load_chatflow_info(self) -> List[Dict]:
        """加载所有chatflow信息"""
        return self.dify_manager.list_instances()
        
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
            
            # 加载当前设置
            current_chatflow = self.config.get("selected_chatflow", {})
            current_description = current_chatflow.get("description", "")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Chatflow选择
                    chatflow_info = self._load_chatflow_info()
                    descriptions = [info.get("description", "") for info in chatflow_info if info.get("description")]
                    
                    # 获取初始API Key和对话列表
                    initial_api_key = ""
                    initial_conversations = []
                    if current_description and current_description in descriptions:
                        instance = self._get_chatflow_by_description(current_description)
                        initial_api_key = instance.get("api_key", "")
                        initial_conversations = list(instance.get("conversations", {}).keys())
                    
                    selected_chatflow = gr.Dropdown(
                        choices=descriptions,
                        value=current_description if current_description in descriptions else None,
                        label="选择聊天机器人",
                        info="选择要使用的Dify聊天机器人",
                        container=True,
                        placeholder="请选择一个聊天机器人..."
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
                    current_conv = current_chatflow.get("conversation", {})
                    current_conv_name = current_conv.get("name", "")
                    
                    conversation_radio = gr.Radio(
                        choices=initial_conversations,
                        value=current_conv_name if current_conv_name in initial_conversations else None,
                        label="选择对话",
                        info="选择一个要使用的对话",
                        container=True
                    )
                    
                    # 语音设置
                    voice_enabled = gr.Checkbox(
                        value=self.config.get("voice_reply_enabled", False),
                        label="启用语音回复",
                        info="是否将AI回复转换为语音",
                        container=True
                    )
            
            # 保存按钮和结果显示
            with gr.Row():
                save_button = gr.Button("💾 保存设置", variant="primary", scale=2)
                reset_button = gr.Button("🔄 重置", variant="secondary", scale=1)
            
            result_text = gr.Textbox(
                label="操作结果",
                interactive=False,
                container=True
            )
            
            # 更新chatflow信息
            def update_chatflow_info(description: str) -> Tuple[str, List[str]]:
                if not description:
                    return "", []
                instance = self._get_chatflow_by_description(description)
                api_key = instance.get("api_key", "")
                conversations = instance.get("conversations", {})
                conversation_list = list(conversations.keys())
                return api_key, conversation_list
            
            selected_chatflow.change(
                fn=update_chatflow_info,
                inputs=[selected_chatflow],
                outputs=[api_key_text, conversation_radio],
                queue=False
            )
            
            # 保存设置
            def save_settings(description: str, conversation_name: str, voice_enabled: bool) -> str:
                if not description:
                    return "❌ 请选择一个聊天机器人"
                if not conversation_name:
                    return "❌ 请选择一个对话"
                
                # 获取完整信息
                instance = self._get_chatflow_by_description(description)
                api_key = instance.get("api_key", "")
                conversations = instance.get("conversations", {})
                conversation_id = conversations.get(conversation_name, "")
                
                if not conversation_id:
                    return "❌ 无法获取对话ID，请重新选择对话"
                
                # 更新配置
                self.config.set("selected_chatflow", {
                    "description": description,
                    "api_key": api_key,
                    "conversation": {
                        "name": conversation_name,
                        "id": conversation_id
                    }
                })
                
                # 更新语音设置
                self.config.set("voice_reply_enabled", voice_enabled)
                
                return "✅ 设置已保存！"
            
            save_button.click(
                fn=save_settings,
                inputs=[selected_chatflow, conversation_radio, voice_enabled],
                outputs=[result_text],
                queue=False
            )
            
            # 重置表单
            def reset_form():
                current_chatflow = self.config.get("selected_chatflow", {})
                description = current_chatflow.get("description", "")
                api_key = current_chatflow.get("api_key", "")
                conversation = current_chatflow.get("conversation", {})
                voice_enabled = self.config.get("voice_reply_enabled", False)
                
                # 获取对话列表
                instance = self._get_chatflow_by_description(description)
                conversations = list(instance.get("conversations", {}).keys())
                
                return (
                    description,
                    api_key,
                    conversations,
                    conversation.get("name", ""),
                    voice_enabled,
                    "🔄 已重置为当前设置"
                )
            
            reset_button.click(
                fn=reset_form,
                inputs=[],
                outputs=[
                    selected_chatflow,
                    api_key_text,
                    conversation_radio,
                    conversation_radio,
                    voice_enabled,
                    result_text
                ],
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