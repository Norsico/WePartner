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

from Core.Logger import Logger
from config import Config

logger = Logger()


class SettingsApp:
    def __init__(self, config_file='./config.json'):
        """
        初始化设置应用
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = Config(file_path=config_file)
        self.interface = None
        self.public_url = None
        self.ngrok_process = None
        self.settings_path = "/wxChatBot/settings"
        self.is_running = False
        
    def _load_config(self):
        """加载当前配置"""
        return self.config.data

    def _save_config(self, config_data):
        """保存配置"""
        for key, value in config_data.items():
            if key in self.config.data and self.config.data[key] == value:
                continue  # 跳过未修改的值
            self.config.set(key, value)
        return "配置已保存，所有修改已生效。"
        
    def _create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="wxChatBot 设置", theme=gr.themes.Soft()) as interface:
            gr.Markdown(
                """
                # wxChatBot 配置管理
                
                在这里您可以方便地配置和管理wxChatBot的各项设置。所有修改会立即生效，无需重启机器人。
                """
            )
            
            config_data = self._load_config()
            
            with gr.Tabs():
                with gr.TabItem("基本设置"):
                    with gr.Group():
                        gr.Markdown("### 用户设置")
                        with gr.Row():
                            master_name = gr.Textbox(
                                value=config_data.get("master_name", "filehelper"),
                                label="主人用户名",
                                info="接收通知和命令的微信账号名称"
                            )
                    
                    with gr.Group():
                        gr.Markdown("### 自动回复设置")
                        with gr.Row():
                            auto_reply_enabled = gr.Checkbox(
                                value=config_data.get("auto_reply_enabled", False),
                                label="启用自动回复",
                                info="是否自动回复普通消息"
                            )
                        
                        with gr.Row():
                            default_reply = gr.Textbox(
                                value=config_data.get("default_reply", "收到您的消息，稍后回复。"),
                                label="默认回复消息",
                                info="自动回复的默认文本",
                                lines=3
                            )
                
                with gr.TabItem("微信API设置"):
                    with gr.Group():
                        gr.Markdown("### Gewechat API配置")
                        with gr.Row():
                            gewechat_base_url = gr.Textbox(
                                value=config_data.get("gewechat_base_url", ""),
                                label="Gewechat API地址",
                                info="Gewechat服务的基础URL"
                            )
                        
                        with gr.Row():
                            gewechat_app_id = gr.Textbox(
                                value=config_data.get("gewechat_app_id", ""),
                                label="Gewechat APP ID",
                                info="Gewechat应用的ID"
                            )
                            
                            gewechat_token = gr.Textbox(
                                value=config_data.get("gewechat_token", ""),
                                label="Gewechat Token",
                                info="留空则自动获取",
                                type="password"
                            )
                    
                    with gr.Group():
                        gr.Markdown("### 回调和下载配置")
                        with gr.Row():
                            gewechat_callback_url = gr.Textbox(
                                value=config_data.get("gewechat_callback_url", ""),
                                label="回调URL",
                                info="接收微信消息的回调URL"
                            )
                        
                        with gr.Row():
                            gewechat_download_url = gr.Textbox(
                                value=config_data.get("gewechat_download_url", ""),
                                label="下载URL",
                                info="文件下载的URL"
                            )
                
                with gr.TabItem("系统设置"):
                    with gr.Group():
                        gr.Markdown("### 运行环境设置")
                        with gr.Row():
                            is_remote_server = gr.Checkbox(
                                value=config_data.get("is_remote_server", False),
                                label="远程服务器模式",
                                info="是否运行在远程服务器上（如果是本地运行，将使用Ngrok进行内网穿透）"
                            )
                        
                        with gr.Row():
                            server_host = gr.Textbox(
                                value=config_data.get("server_host", "localhost"),
                                label="服务器主机名",
                                info="远程服务器的主机名或IP，仅在远程服务器模式下使用"
                            )
                    
                    with gr.Group():
                        gr.Markdown("### Ngrok设置")
                        with gr.Row():
                            ngrok_auth_token = gr.Textbox(
                                value=config_data.get("ngrok_auth_token", ""),
                                label="Ngrok认证令牌",
                                info="用于内网穿透的Ngrok认证令牌",
                                type="password"
                            )
                
                with gr.TabItem("高级设置"):
                    with gr.Group():
                        gr.Markdown("### 日志设置")
                        with gr.Row():
                            debug_mode = gr.Checkbox(
                                value=config_data.get("debug_mode", False),
                                label="调试模式",
                                info="启用调试日志"
                            )
                        
                        with gr.Row():
                            log_level = gr.Dropdown(
                                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                                value=config_data.get("log_level", "INFO"),
                                label="日志级别",
                                info="日志记录级别"
                            )
            
            # 保存按钮和结果显示
            with gr.Row():
                save_button = gr.Button("保存配置", variant="primary", size="lg")
                reset_button = gr.Button("重置", variant="secondary")
            
            result_text = gr.Textbox(label="操作结果", interactive=False)
            
            # 提交事件
            save_button.click(
                fn=lambda m, a, d, g, ga, gt, gc, gd, r, sh, n, dm, ll: self._save_config({
                    "master_name": m,
                    "auto_reply_enabled": a,
                    "default_reply": d,
                    "gewechat_base_url": g,
                    "gewechat_app_id": ga,
                    "gewechat_token": gt,
                    "gewechat_callback_url": gc,
                    "gewechat_download_url": gd,
                    "is_remote_server": r,
                    "server_host": sh,
                    "ngrok_auth_token": n,
                    "debug_mode": dm,
                    "log_level": ll
                }),
                inputs=[
                    master_name, auto_reply_enabled, default_reply,
                    gewechat_base_url, gewechat_app_id, gewechat_token, gewechat_callback_url, gewechat_download_url,
                    is_remote_server, server_host, ngrok_auth_token, debug_mode, log_level
                ],
                outputs=result_text
            )
            
            # 重置按钮事件
            def reset_form():
                return (
                    config_data.get("master_name", "filehelper"),
                    config_data.get("auto_reply_enabled", False),
                    config_data.get("default_reply", "收到您的消息，稍后回复。"),
                    config_data.get("gewechat_base_url", ""),
                    config_data.get("gewechat_app_id", ""),
                    config_data.get("gewechat_token", ""),
                    config_data.get("gewechat_callback_url", ""),
                    config_data.get("gewechat_download_url", ""),
                    config_data.get("is_remote_server", False),
                    config_data.get("server_host", "localhost"),
                    config_data.get("ngrok_auth_token", ""),
                    config_data.get("debug_mode", False),
                    config_data.get("log_level", "INFO"),
                    "表单已重置为当前配置"
                )
                
            reset_button.click(
                fn=reset_form,
                inputs=[],
                outputs=[
                    master_name, auto_reply_enabled, default_reply,
                    gewechat_base_url, gewechat_app_id, gewechat_token, gewechat_callback_url, gewechat_download_url,
                    is_remote_server, server_host, ngrok_auth_token, debug_mode, log_level,
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
        is_remote_server = self.config.get("is_remote_server", False)
        
        if not is_remote_server:
            # 在本地模式下使用Ngrok
            ngrok_auth_token = self.config.get("ngrok_auth_token")
            
            if ngrok_auth_token:
                try:
                    # 设置Ngrok认证
                    ngrok.set_auth_token(ngrok_auth_token)
                    
                    # 启动Ngrok隧道
                    public_url = ngrok.connect(port, bind_tls=True).public_url
                    
                    # 如果路径不是/，则添加自定义路径
                    if self.settings_path and not self.settings_path == "/":
                        # 如果public_url最后有/，先去掉
                        if public_url.endswith("/"):
                            public_url = public_url[:-1]
                            
                        # 如果settings_path不是以/开头，先加上
                        if not self.settings_path.startswith("/"):
                            self.settings_path = "/" + self.settings_path
                            
                        # 组合URL
                        public_url = public_url + self.settings_path
                        
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
            server_host = self.config.get("server_host", "localhost")
            self.public_url = f"http://{server_host}:{port}"
            
        # 在新线程中启动Gradio界面
        def run_interface():
            self.interface.launch(
                server_name="0.0.0.0",
                server_port=port,
                share=False,
                inbrowser=False,
                debug=False
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