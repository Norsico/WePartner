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
from config import Config
from typing import List, Dict, Tuple

from Core.Logger import Logger
from Core.difyAI.dify_manager import DifyManager
from .settings_manager import SettingsManager

logger = Logger()

class SettingsApp:
    def __init__(self):
        """初始化设置应用"""
        self.settings_manager = SettingsManager()
        self.dify_manager = DifyManager()
        self.config = Config()
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
        instances = self._load_chatflow_info()
        for instance in instances:
            if instance.get("description") == description:
                return instance
        return {}
        
    def _create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="wxChatBot 设置", theme=gr.themes.Soft()) as interface:
            # 标题和说明
            gr.Markdown(
                """
                # 🤖 wxChatBot 配置管理
                
                在这里您可以配置wxChatBot的聊天和语音设置。所有修改会立即生效。
                """
            )
            
            # 加载当前设置
            current_settings = self.settings_manager.get_settings()
            current_chatflow = current_settings.get("selected_chatflow", {})
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Chatflow选择
                    chatflow_info = self._load_chatflow_info()
                    descriptions = [info.get("description", "") for info in chatflow_info if info.get("description")]
                    
                    selected_chatflow = gr.Dropdown(
                        choices=descriptions,
                        value=current_chatflow.get("description", ""),
                        label="选择聊天机器人",
                        info="选择要使用的Dify聊天机器人"
                    )
                    
                    # API Key显示
                    api_key_text = gr.Textbox(
                        value=current_chatflow.get("api_key", ""),
                        label="API Key",
                        info="当前选中的机器人的API Key",
                        interactive=False
                    )
                    
                    # 对话选择
                    current_conv = current_chatflow.get("conversation", {})
                    conversation_radio = gr.Radio(
                        choices=[],
                        value=current_conv.get("name", ""),
                        label="选择对话",
                        info="选择一个要使用的对话"
                    )
                    
                with gr.Column(scale=1):
                    # 语音设置
                    voice_enabled = gr.Checkbox(
                        value=current_settings.get("voice_reply_enabled", False),
                        label="启用语音回复",
                        info="是否将回复转换为语音"
                    )
            
            # 保存按钮和结果显示
            with gr.Row():
                save_button = gr.Button("💾 保存设置", variant="primary", scale=2)
                reset_button = gr.Button("🔄 重置", variant="secondary", scale=1)
            
            result_text = gr.Textbox(
                label="操作结果",
                interactive=False
            )
            
            # 更新chatflow信息
            def update_chatflow_info(description: str) -> Tuple[str, List[str]]:
                instance = self._get_chatflow_by_description(description)
                api_key = instance.get("api_key", "")
                conversations = instance.get("conversations", {})
                return api_key, list(conversations.keys())
            
            selected_chatflow.change(
                fn=update_chatflow_info,
                inputs=[selected_chatflow],
                outputs=[api_key_text, conversation_radio]
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
                
                # 更新设置
                success = self.settings_manager.update_settings({
                    "selected_chatflow": {
                        "description": description,
                        "api_key": api_key,
                        "conversation": {
                            "name": conversation_name,
                            "id": conversation_id
                        }
                    },
                    "voice_reply_enabled": voice_enabled
                })
                
                return "✅ 设置已保存！" if success else "❌ 保存设置失败，请重试"
            
            save_button.click(
                fn=save_settings,
                inputs=[selected_chatflow, conversation_radio, voice_enabled],
                outputs=[result_text]
            )
            
            # 重置表单
            def reset_form():
                current_settings = self.settings_manager.get_settings()
                current_chatflow = current_settings.get("selected_chatflow", {})
                description = current_chatflow.get("description", "")
                api_key = current_chatflow.get("api_key", "")
                conversation = current_chatflow.get("conversation", {})
                
                # 获取对话列表
                instance = self._get_chatflow_by_description(description)
                conversations = list(instance.get("conversations", {}).keys())
                
                return (
                    description,
                    api_key,
                    conversations,
                    conversation.get("name", ""),
                    current_settings.get("voice_reply_enabled", False),
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
                ]
            )
            
        return interface
    
    def get_public_url(self):
        """获取公共访问URL"""
        if not self.is_running:
            return None
            
        return self.public_url
        
    def start(self, port=7860):
        """
        启动设置应用
        
        Args:
            port: 服务器端口
        """
        if self.is_running:
            return self.public_url
            
        # 创建界面
        self.interface = self._create_interface()
        
        # 检查是否需要使用Ngrok
        # is_remote_server = self.settings_manager.get_settings().get("is_remote_server", False)
        is_remote_server = self.config.get("is_remote_server", False)
        
        if not is_remote_server:
            # 在本地模式下使用Ngrok
            # ngrok_auth_token = self.settings_manager.get_settings().get("ngrok_auth_token")
            
            ngrok_auth_token = self.config.get("ngrok_auth_token")
            
            if ngrok_auth_token:
                try:
                    # 设置Ngrok认证
                    ngrok.set_auth_token(ngrok_auth_token)
                    
                    # 先关闭所有现有的Ngrok隧道，避免多会话错误
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
                            break  # 成功连接，跳出循环
                        except Exception as connect_err:
                            retry_count += 1
                            if retry_count >= max_retries:
                                raise  # 重试次数用完，抛出异常
                            logger.warning(f"Ngrok连接失败，正在重试 ({retry_count}/{max_retries}): {str(connect_err)}")
                            time.sleep(2)  # 等待2秒后重试
                    
                    # 设置公共URL，不需要手动添加路径
                    self.public_url = public_url
                    logger.success(f"Ngrok隧道已建立，公共URL: {self.public_url}")
                except Exception as e:
                    logger.error(f"Ngrok隧道建立失败: {str(e)}")
                    # 如果Ngrok失败，使用本地URL
                    self.public_url = f"http://localhost:{port}"
            else:
                logger.warning("未设置Ngrok认证令牌，使用本地URL")
                self.public_url = f"http://localhost:{port}"
        else:
            # 在远程服务器模式下，直接使用服务器URL
            # server_host = self.settings_manager.get_settings().get("server_host", "localhost")
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
        
        # 等待服务器启动
        time.sleep(2)
        
        self.is_running = True
        logger.success(f"设置界面已启动，访问URL: {self.public_url}")
        
        return self.public_url
        
    def stop(self):
        """停止设置应用"""
        if not self.is_running:
            return
            
        # 关闭Ngrok隧道
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