"""
基于Gradio的设置界面
提供图形化的配置管理
"""
import os
import sys
import gradio as gr
import threading
import time
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import Config
from Core.Logger import Logger
from Core.difyAI.dify_manager import DifyManager
from Core.web_app.settings_manager import SettingsManager
from Core.difyAI.dify_chatflow import DifyChatflow


logger = Logger()

class SettingsApp:
    def __init__(self):
        """初始化设置应用"""
        self.config = Config()
        self.settings_manager = SettingsManager()
        # 强制创建新的DifyManager实例，确保从磁盘加载最新配置
        DifyManager._instance = None
        DifyManager._initialized = False
        self.dify_manager = DifyManager()
        self.interface = None
        self.public_url = None
        self.settings_path = "/wxChatBot/settings"
        self.is_running = False
        self.chatflow_info = self.dify_manager.get_dify_config()
        self.settings = self.settings_manager.get_settings()
        logger.debug(f"SettingsApp初始化，加载的对话列表: {self.chatflow_info}")
        
    def _create_interface(self):
        """创建Gradio界面"""
        # 强制重新初始化dify_manager以确保获取最新配置
        DifyManager._instance = None
        DifyManager._initialized = False
        self.dify_manager = DifyManager()
        self.chatflow_info = self.dify_manager.get_dify_config()
        
        def refresh_data():
            """刷新数据，重新从配置文件加载配置"""
            # 强制从磁盘重新读取配置
            DifyManager._instance = None
            DifyManager._initialized = False
            self.dify_manager = DifyManager()
            self.chatflow_info = self.dify_manager.get_dify_config()
            self.settings = self.settings_manager.get_settings()
            chatflow_names = list(self.chatflow_info.get('chatflow', {}).keys())
            
            # 为每个需要刷新的组件生成对应的选项
            # 尝试保留当前选择的值
            current_chatflow = chatflow_radio.value
            current_del_chatflow = delete_chatflow_radio.value
            current_conv_chatflow = conv_chatflow_radio.value
            current_del_conv_chatflow = del_conv_chatflow_radio.value
            
            chatflow_radio_updated = gr.Radio(
                choices=chatflow_names, 
                value=current_chatflow if current_chatflow in chatflow_names else None
            )
            delete_chatflow_radio_updated = gr.Radio(
                choices=chatflow_names, 
                value=current_del_chatflow if current_del_chatflow in chatflow_names else None
            )
            conv_chatflow_radio_updated = gr.Radio(
                choices=chatflow_names, 
                value=current_conv_chatflow if current_conv_chatflow in chatflow_names else None
            )
            del_conv_chatflow_radio_updated = gr.Radio(
                choices=chatflow_names, 
                value=current_del_conv_chatflow if current_del_conv_chatflow in chatflow_names else None
            )
            
            # 更新聊天设置中的对话列表
            selected_chatflow = current_chatflow or self.settings.get('selected_chatflow', {}).get('description')
            
            if selected_chatflow in chatflow_names:
                conversations = list(self.chatflow_info.get('chatflow', {}).get(selected_chatflow, {}).get('conversations', {}).keys())
                conversation_radio_updated = gr.Radio(choices=conversations, value=None)
            else:
                conversation_radio_updated = gr.Radio(choices=[], value=None)
            
            # 更新语音设置
            voice_enabled = self.settings.get('voice_reply_enabled', False)
            voice_checkbox_updated = gr.Checkbox(value=voice_enabled)
            
            # 更新等待时间设置
            timer_seconds = self.settings.get('timer_seconds', 5)
            timer_slider_updated = gr.Slider(
                minimum=1,
                maximum=30,
                value=timer_seconds,
                step=1,
                label="等待时间（秒）",
                info="设置范围：1-30秒"
            )
            
            return (
                chatflow_radio_updated,
                delete_chatflow_radio_updated,
                conv_chatflow_radio_updated,
                del_conv_chatflow_radio_updated,
                "数据已刷新",
                conversation_radio_updated,
                voice_checkbox_updated,
                timer_slider_updated
            )

        def update_conversations(chatflow_name):
            """根据选择的chatflow更新对话列表"""
            if not chatflow_name:
                return gr.Radio(choices=[], value=None)
            
            # 强制从磁盘重新读取配置    
            DifyManager._instance = None
            DifyManager._initialized = False
            self.dify_manager = DifyManager()
            # 重新从配置加载数据，确保获取最新信息
            self.chatflow_info = self.dify_manager.get_dify_config()
            conversations = self.chatflow_info.get('chatflow', {}).get(chatflow_name, {}).get('conversations', {})
            conv_list = list(conversations.keys())
            
            return gr.Radio(choices=conv_list, value=None)
            
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

        def create_chatflow(description, api_key, base_url):
            """创建新的DifyChatflow客户端"""
            try:
                if not description or not api_key:
                    return "错误：描述和API Key不能为空"
                
                # 创建新的DifyChatflow实例
                client = DifyChatflow(
                    api_key=api_key,
                    description=description,
                    base_url=base_url or "http://localhost/v1"
                )
                
                # 更新chatflow信息
                self.chatflow_info = self.dify_manager.get_dify_config()
                
                # 更新界面
                chatflow_names = list(self.chatflow_info.get('chatflow', {}).keys())
                
                return f"成功创建Chatflow客户端：{description}"
            except Exception as e:
                return f"创建失败：{str(e)}"

        def delete_chatflow(chatflow_name):
            """删除DifyChatflow客户端"""
            try:
                if not chatflow_name:
                    return "错误：请选择要删除的Chatflow"
                
                # 从配置文件中删除
                if chatflow_name in self.chatflow_info.get('chatflow', {}):
                    del self.chatflow_info['chatflow'][chatflow_name]
                    self.dify_manager.save_dify_config(self.chatflow_info)
                    
                    return f"成功删除Chatflow：{chatflow_name}"
                return "未找到指定的Chatflow"
            except Exception as e:
                return f"删除失败：{str(e)}"

        def create_conversation(chatflow_name, conversation_name, initial_message):
            """创建新的对话"""
            try:
                if not chatflow_name:
                    return "错误：请选择Chatflow"
                
                chatflow_info = self.chatflow_info.get('chatflow', {}).get(chatflow_name, {})
                if not chatflow_info:
                    return "错误：未找到选择的Chatflow"
                
                # 创建DifyChatflow实例
                client = DifyChatflow(
                    api_key=chatflow_info['api_key'],
                    description=chatflow_name,
                    base_url=chatflow_info.get('base_url', "http://localhost/v1")
                )
                
                # 发送初始消息创建对话
                response = client.chat(
                    query=initial_message or "你好",
                    conversation_name=conversation_name
                )
                
                if response.get('conversation_id'):
                    # 更新chatflow信息
                    self.chatflow_info = self.dify_manager.get_dify_config()
                    
                    return f"成功创建对话：{conversation_name}\nAI回复：{response.get('answer')}"
                return "创建对话失败"
            except Exception as e:
                return f"创建失败：{str(e)}"

        def delete_conversation(chatflow_name, conversation_name):
            """删除指定Chatflow下的对话"""
            try:
                if not chatflow_name or not conversation_name:
                    return "错误：请选择Chatflow和对话"
                
                # 强制从磁盘重新读取配置
                DifyManager._instance = None
                DifyManager._initialized = False
                self.dify_manager = DifyManager()
                self.chatflow_info = self.dify_manager.get_dify_config()
                
                # 检查chatflow是否存在
                if chatflow_name not in self.chatflow_info.get('chatflow', {}):
                    return "错误：未找到选择的Chatflow"
                
                # 检查对话是否存在
                conversations = self.chatflow_info['chatflow'][chatflow_name].get('conversations', {})
                if conversation_name not in conversations:
                    return "错误：未找到选择的对话"
                
                # 直接从配置中删除对话
                del self.chatflow_info['chatflow'][chatflow_name]['conversations'][conversation_name]
                
                # 保存更新后的配置
                success = self.dify_manager.save_dify_config(self.chatflow_info)
                if success:
                    return f"成功删除对话：{conversation_name}"
                else:
                    return "删除失败：保存配置时出错"
            except Exception as e:
                return f"删除失败：{str(e)}"

        def create_conversation_and_reset(chatflow_name, conversation_name, initial_message):
            """创建新对话并重置表单"""
            if not chatflow_name or not conversation_name:
                return "错误：Chatflow和对话名称不能为空", conversation_name, initial_message
                
            result = create_conversation(chatflow_name, conversation_name, initial_message)
            
            # 返回结果和重置的表单值
            return result, "", "你好"

        def save_timer_settings(timer_value):
            """保存等待时间设置"""
            try:
                self.settings_manager.set_setting('timer_seconds', int(timer_value))
                logger.success(f"已保存等待时间设置：{timer_value}秒")
                return f"等待时间设置保存成功！当前设置为{timer_value}秒"
            except Exception as e:
                logger.error(f"保存等待时间设置失败：{str(e)}")
                return "保存失败，请检查日志"

        with gr.Blocks(title="wxChatBot 设置", theme=gr.themes.Soft(), analytics_enabled=False) as interface:
            # 标题和说明
            with gr.Row():
                with gr.Column(scale=10):
                    gr.Markdown(
                        """
                        # 🤖 wxChatBot 配置管理
                        
                        在这里您可以配置wxChatBot的各项设置。所有修改会立即生效。
                        """
                    )
                with gr.Column(scale=1):
                    refresh_btn = gr.Button("🔄 刷新数据", variant="primary")
                    refresh_result = gr.Textbox(label="刷新结果", interactive=False, visible=False)
            
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
                            value=self.settings.get('selected_chatflow', {}).get('description'),
                            label="可用的Chatflow列表"
                        )
                    
                        # 对话列表
                        gr.Markdown("### 选择对话")
                        conversation_radio = gr.Radio(
                            choices=list(self.chatflow_info.get('chatflow', {}).get(self.settings.get('selected_chatflow', {}).get('description'), {}).get('conversations', {}).keys()),
                            value=self.settings.get('selected_chatflow', {}).get('conversation', {}).get('name'),
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

                # 其他设置页面
                with gr.Tab("⚙️ 其他设置"):
                    with gr.Column():
                        gr.Markdown(
                            """
                            ### 消息聚合设置
                            
                            设置接收消息时的等待时间，在此时间内如果收到新消息，将重置计时器并将消息合并处理。
                            """
                        )
                        
                        # 获取当前timer_seconds设置
                        timer_seconds = self.settings.get('timer_seconds', 5)
                        
                        # 等待时间设置
                        timer_slider = gr.Slider(
                            minimum=1,
                            maximum=30,
                            value=timer_seconds,
                            step=1,
                            label="等待时间（秒）",
                            info="设置范围：1-30秒"
                        )
                        
                        # 保存按钮和结果显示
                        timer_save_btn = gr.Button("保存等待时间设置", variant="primary", size="lg")
                        timer_result = gr.Textbox(label="保存结果", interactive=False)

                # Chatflow管理页面
                with gr.Tab("🔧 Chatflow管理"):
                    with gr.Column():
                        gr.Markdown("### 创建新的Chatflow客户端")
                        
                        # 创建Chatflow的表单
                        with gr.Group():
                            description = gr.Textbox(
                                label="描述",
                                placeholder="输入Chatflow的描述名称"
                            )
                            api_key = gr.Textbox(
                                label="API Key",
                                placeholder="输入Dify API Key"
                            )
                            base_url = gr.Textbox(
                                label="Base URL",
                                value="http://localhost/v1",
                                placeholder="输入Dify API基础URL"
                            )
                            create_btn = gr.Button("创建Chatflow", variant="primary")
                            create_result = gr.Textbox(label="创建结果", interactive=False)
                        
                        gr.Markdown("### 删除现有Chatflow")
                        # 删除Chatflow的表单
                        with gr.Group():
                            delete_chatflow_radio = gr.Radio(
                                choices=chatflow_names,
                                label="选择要删除的Chatflow"
                            )
                            delete_btn = gr.Button("删除Chatflow", variant="secondary")
                            delete_result = gr.Textbox(label="删除结果", interactive=False)

                # 对话管理页面
                with gr.Tab("💭 对话管理"):
                    with gr.Column():
                        gr.Markdown("### 创建新对话")
                        
                        # 创建对话的表单
                        with gr.Group():
                            conv_chatflow_radio = gr.Radio(
                                choices=chatflow_names,
                                label="选择Chatflow"
                            )
                            conv_name = gr.Textbox(
                                label="对话名称",
                                placeholder="输入新对话的名称"
                            )
                            initial_message = gr.Textbox(
                                label="初始消息",
                                placeholder="输入开始对话的消息",
                                value="你好"
                            )
                            create_conv_btn = gr.Button("创建对话", variant="primary")
                            create_conv_result = gr.Textbox(label="创建结果", interactive=False)

                        gr.Markdown("### 删除对话")
                        # 删除对话的表单
                        with gr.Group():
                            del_conv_chatflow_radio = gr.Radio(
                                choices=chatflow_names,
                                label="选择Chatflow"
                            )
                            del_conv_radio = gr.Radio(
                                choices=[],
                                label="选择要删除的对话"
                            )
                            del_conv_btn = gr.Button("删除对话", variant="secondary")
                            del_conv_result = gr.Textbox(label="删除结果", interactive=False)
            
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

            # 等待时间设置事件
            timer_save_btn.click(
                fn=save_timer_settings,
                inputs=[timer_slider],
                outputs=[timer_result]
            )

            # 刷新按钮事件
            refresh_btn.click(
                fn=refresh_data,
                inputs=[],
                outputs=[
                    chatflow_radio, 
                    delete_chatflow_radio, 
                    conv_chatflow_radio, 
                    del_conv_chatflow_radio,
                    refresh_result,
                    conversation_radio,
                    voice_checkbox,
                    timer_slider
                ]
            ).then(
                fn=update_conversations,
                inputs=[del_conv_chatflow_radio],
                outputs=[del_conv_radio]
            )

            # Chatflow管理事件
            create_btn.click(
                fn=create_chatflow,
                inputs=[description, api_key, base_url],
                outputs=[create_result]
            ).then(
                fn=refresh_data,
                inputs=[],
                outputs=[
                    chatflow_radio, 
                    delete_chatflow_radio, 
                    conv_chatflow_radio, 
                    del_conv_chatflow_radio,
                    refresh_result,
                    conversation_radio,
                    voice_checkbox,
                    timer_slider
                ]
            )

            delete_btn.click(
                fn=delete_chatflow,
                inputs=[delete_chatflow_radio],
                outputs=[delete_result]
            ).then(
                fn=refresh_data,
                inputs=[],
                outputs=[
                    chatflow_radio, 
                    delete_chatflow_radio, 
                    conv_chatflow_radio, 
                    del_conv_chatflow_radio,
                    refresh_result,
                    conversation_radio,
                    voice_checkbox,
                    timer_slider
                ]
            )

            # 对话管理事件
            create_conv_btn.click(
                fn=create_conversation_and_reset,
                inputs=[conv_chatflow_radio, conv_name, initial_message],
                outputs=[create_conv_result, conv_name, initial_message]
            ).then(
                fn=refresh_data,
                inputs=[],
                outputs=[
                    chatflow_radio, 
                    delete_chatflow_radio, 
                    conv_chatflow_radio, 
                    del_conv_chatflow_radio,
                    refresh_result,
                    conversation_radio,
                    voice_checkbox,
                    timer_slider
                ]
            )

            # 删除对话相关事件
            del_conv_chatflow_radio.change(
                fn=update_conversations,
                inputs=[del_conv_chatflow_radio],
                outputs=[del_conv_radio]
            )

            del_conv_btn.click(
                fn=delete_conversation,
                inputs=[del_conv_chatflow_radio, del_conv_radio],
                outputs=[del_conv_result]
            ).then(
                fn=refresh_data,
                inputs=[],
                outputs=[
                    chatflow_radio, 
                    delete_chatflow_radio, 
                    conv_chatflow_radio, 
                    del_conv_chatflow_radio,
                    refresh_result,
                    conversation_radio,
                    voice_checkbox,
                    timer_slider
                ]
            ).then(
                fn=update_conversations,
                inputs=[del_conv_chatflow_radio],
                outputs=[del_conv_radio]
            )
            
            # 页面加载时自动刷新数据
            interface.load(
                fn=refresh_data,
                inputs=[],
                outputs=[
                    chatflow_radio, 
                    delete_chatflow_radio, 
                    conv_chatflow_radio, 
                    del_conv_chatflow_radio,
                    refresh_result,
                    conversation_radio,
                    voice_checkbox,
                    timer_slider
                ]
            ).then(
                fn=update_conversations,
                inputs=[del_conv_chatflow_radio],
                outputs=[del_conv_radio]
            )
            
        return interface
        
    def start(self, port=7863):
        """启动设置应用"""
        if self.is_running:
            return self.public_url
            
        # 强制从磁盘重新加载最新配置
        DifyManager._instance = None
        DifyManager._initialized = False
        self.dify_manager = DifyManager()
        self.chatflow_info = self.dify_manager.get_dify_config()
        self.settings = self.settings_manager.get_settings()
        
        # 创建界面
        self.interface = self._create_interface()

        # 在远程服务器模式下，直接使用服务器URL
        server_host = self.config.get("server_host", "localhost")
        self.public_url = f"http://{server_host}:{port}"
            
        # 在新线程中启动Gradio界面
        def run_interface():
            self.interface.launch(
                server_name="0.0.0.0",
                server_port=port,
                share=True,
                inbrowser=False,
                debug=False,
                root_path=self.settings_path if self.settings_path != "/" else None
            )
            
        thread = threading.Thread(target=run_interface, daemon=True)
        thread.start()
        
        time.sleep(5)
        self.is_running = True
        logger.success(f"设置界面已启动，访问URL: {self.public_url} \n或者 {self.interface.share_url}")

        self.public_url = self.interface.share_url
        
        return self.interface.share_url
        
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
