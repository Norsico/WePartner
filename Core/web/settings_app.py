"""
基于Gradio的设置界面
提供图形化的配置管理
"""
import os
import sys
import gradio as gr
import threading
import time
from pyngrok import ngrok
from typing import List, Dict
from pydantic import BaseModel
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import Config
from Core.Logger import Logger
from Core.difyAI.dify_manager import DifyManager
from Core.web.settings_manager import SettingsManager

# 配置Pydantic模型
class Settings(BaseModel):
    class Config:
        arbitrary_types_allowed = True

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
        self.chatflow_info = self.dify_manager.get_dify_config()
        self.settings = self.settings_manager.get_settings()

    def _get_default_chatflow(self):
        """获取默认chatflow"""
        return self.settings.get('selected_chatflow', {}).get('description')

    def _get_default_conversation(self):
        """获取默认对话"""
        return self.settings.get('selected_chatflow', {}).get('conversation', {}).get('name')

        
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
        def initialize_state():
            """初始化状态，获取最新的settings"""
            return {
                "selected_chatflow": self._get_default_chatflow(),
                "selected_conversation": self._get_default_conversation()
            }
        
        def update_conversations(chatflow_name):
            """根据选择的chatflow更新对话列表"""
            if not chatflow_name:
                return gr.Radio(choices=[], value=None)
            conversations = self.chatflow_info.get('chatflow', {}).get(chatflow_name, {}).get('conversations', {})
            return gr.Radio(choices=list(conversations.keys()), value=None)
            
        def save_settings(chatflow_name, conversation_name):
            """保存设置到配置文件"""
            if not chatflow_name or not conversation_name:
                return "错误：请选择Chatflow和对话"
                
            # 获取chatflow数据
            chatflow_info = self.chatflow_info.get('chatflow', {}).get(chatflow_name, {})
            
            if not chatflow_info:
                return "错误：无法获取所选Chatflow的信息"
                
            # 获取对话ID
            conversation_id = chatflow_info.get('conversations', {}).get(conversation_name)
            if not conversation_id:
                return "错误：无法获取所选对话的ID"
                
            # 获取API Key
            api_key = chatflow_info.get('api_key')
            if not api_key:
                return "错误：无法获取所选Chatflow的API Key"
                
            # 保存设置
            success = self.settings_manager.set_selected_chatflow(
                description=chatflow_name,
                api_key=api_key,
                conversation_name=conversation_name,
                conversation_id=conversation_id
            )

            # 更新settings
            self.settings = self.settings_manager.get_settings()

            if success:
                logger.success(f"已保存设置：chatflow={chatflow_name}, conversation={conversation_name}")
                return f"设置保存成功！\nChatflow: {chatflow_name}\n对话: {conversation_name}"
            else:
                return "设置保存失败，请检查日志"
                
        def save_voice_settings(voice_enabled):
            """保存语音设置"""
            success = self.settings_manager.set_voice_reply_enabled(voice_enabled)
            if success:
                logger.success(f"已保存语音设置：启用={voice_enabled}")
                return "语音设置保存成功！"
            else:
                return "语音设置保存失败，请检查日志"

        with gr.Blocks(title="wxChatBot 设置", theme=gr.themes.Soft(), analytics_enabled=False) as interface:

            # 动态初始化状态
            state = gr.State(value=initialize_state)

            # 标题和说明
            gr.Markdown(
                """
                # 🤖 wxChatBot 配置管理
                
                在这里您可以配置wxChatBot的各项设置。所有修改会立即生效。
                """
            )
            
            # 创建选项卡
            with gr.Tabs():
                # 聊天设置页面
                with gr.Tab("💬 聊天设置"):
                    # 获取chatflow数据和默认选中值
                    chatflow_names = list(self.chatflow_info.get('chatflow', {}).keys())
                    
                    with gr.Column():
                        # Chatflow选择
                        gr.Markdown("### 选择Chatflow")
                        chatflow_radio = gr.Radio(
                            choices=chatflow_names,
                            value=state.value["selected_chatflow"],
                            label="可用的Chatflow列表"
                        )
                    
                        # 对话列表
                        gr.Markdown("### 选择对话")
                        conversation_radio = gr.Radio(
                            choices=list(self.chatflow_info.get('chatflow', {}).get(state.value["selected_chatflow"], {}).get('conversations', {}).keys()),
                            value=state.value["selected_conversation"],
                            label="可用的对话列表"
                        )
                        
                        # 保存按钮和结果显示
                        save_btn = gr.Button("保存聊天设置", variant="primary", size="lg")
                        chat_result = gr.Textbox(label="保存结果", interactive=False)
                
                # 语音设置页面
                with gr.Tab("🔊 语音设置"):
                    with gr.Column():
                        gr.Markdown(
                            """
                            ### 语音回复设置
                            
                            您可以选择是否启用AI回复的语音播放功能。
                            """
                        )
                        
                        # 获取当前语音设置
                        voice_enabled = self.settings.get('voice_reply_enabled', False)
                        
                        # 语音开关
                        voice_checkbox = gr.Checkbox(
                            value=voice_enabled,
                            label="启用语音回复",
                            info="开启后，AI的回复将会以语音方式播放"
                        )
                        
                        # 保存按钮和结果显示
                        voice_save_btn = gr.Button("保存语音设置", variant="primary", size="lg")
                        voice_result = gr.Textbox(label="保存结果", interactive=False)
            
            # 事件处理
            chatflow_radio.change(
                fn=update_conversations,
                inputs=[chatflow_radio],
                outputs=[conversation_radio]
            )
            
            save_btn.click(
                fn=save_settings,
                inputs=[chatflow_radio, conversation_radio],
                outputs=[chat_result]
            )
            
            voice_save_btn.click(
                fn=save_voice_settings,
                inputs=[voice_checkbox],
                outputs=[voice_result]
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
                root_path=self.settings_path if self.settings_path != "/" else None,
                show_error=True,
                allowed_paths=[],
                ssl_verify=False
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

if __name__ == "__main__":
    app = get_settings_app()
    app.start()
    # 一直运行
    while True:
        time.sleep(1)
