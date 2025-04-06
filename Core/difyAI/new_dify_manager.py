import os
import json
import sys
import re
import requests

class NewDifyManager:
    def __init__(self,project_config, config_file="new_dify_config.json"):
        """
        初始化 NewDifyManager 类实例。
        :param project_config: 项目配置。
        :param config_file: 用于存储用户对话 ID 的配置文件。
        """
        
        # 获取当前脚本的目录路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(script_dir)
        
        # 构造配置文件的完整路径
        self.config_file = os.path.join(script_dir, config_file)
        self.config = self.load_config()
        self.project_config = project_config
        self.api_key = self.project_config.get("dify_api_key")

        # Dify API 基础URL
        self.base_url = f"https://{self.project_config.get('dify_server_ip')}/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def load_config(self):
        """
        加载配置文件，如果文件不存在则创建一个空的配置。
        :return: 配置字典。
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_config(self):
        """
        保存配置文件。
        """
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_conversation_id(self, wxid):
        """
        根据 wxid 获取 conversation_id，如果不存在则返回 None。
        :param wxid: 用户的微信 ID。
        :return: conversation_id 或 None。
        """
        return self.config.get(wxid)

    def set_conversation_id(self, wxid, conversation_id):
        """
        为 wxid 设置 conversation_id，并保存到配置文件中。
        :param wxid: 用户的微信 ID。
        :param conversation_id: 对话 ID。
        """
        self.config[wxid] = conversation_id
        self.save_config()

    def handle_response(self, response):
        """
        处理API响应，提取文本和语音内容
        :param response: API响应对象
        :return: 处理后的响应内容列表
        """
        content = response.get('answer', '')
        results = []
        print("handle response...")
        
        # 检查返回的内容类型
        if '<text>' in content:
            print("提取文本内容")
            text_contents = re.findall(r'<text>(.*?)</text>', content, re.DOTALL)
            if text_contents:
                for text in text_contents:
                    results.append({
                        'type': 'text',
                        'content': text.strip()
                    })
        else:
            # 如果没有特定标记，将整个内容视为文本
            results.append({
                'type': 'text',
                'content': content.strip()
            })

        if '<voice>' in content:
            print("提取语音内容")
            voice_contents = re.findall(r'<voice>(.*?)</voice>', content, re.DOTALL)
            if voice_contents:
                for voice_url in voice_contents:
                    results.append({
                        'type': 'voice',
                        'content': voice_url.strip()
                    })

        print(f"results:{results}")
        return results

    def chat_with_bot(self, wxid=None, user_message=None):
        """
        与Dify应用进行对话
        :param wxid: 用户微信ID
        :param user_message: 用户消息内容
        :return: 包含回复内容的字典
        """
        if not wxid or not user_message:
            raise ValueError("wxid和user_message参数不能为空")
            
        conversation_id = self.get_conversation_id(wxid)
        endpoint = f"{self.base_url}/chat-messages"
        
        payload = {
            "inputs": {},
            "query": user_message,
            "response_mode": "streaming"
        }
        
        if conversation_id:
            print(f"继续对话，ID: {conversation_id}")
            payload["conversation_id"] = conversation_id
        else:
            print("开始新对话")
            
        try:
            response = requests.post(endpoint, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # 提取并保存conversation_id
            if "conversation_id" in data:
                self.set_conversation_id(wxid, data["conversation_id"])
                
            return data
        except Exception as e:
            print(f"API请求失败: {e}")
            if hasattr(e, 'response'):
                print(f"服务器响应: {e.response.text}")
            return {"answer": f"对话请求失败: {str(e)}"}

# 示例用法
if __name__ == "__main__":
    # 初始化 NewDifyManager 实例
    dify_manager = NewDifyManager()

    # 用户微信ID
    wxid = "wxid_test123"

    # 用户发送的消息
    user_message = "你好，请介绍一下自己"

    # 与Dify应用对话并获取回复
    result = dify_manager.chat_with_bot(wxid=wxid, user_message=user_message)
    print(f"回复: {result.get('answer', '无回复')}")
