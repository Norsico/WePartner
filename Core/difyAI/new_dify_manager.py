import os
import json
import sys
import re
import requests

# 获取项目根目录
current_file_path = os.path.abspath(__file__)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
sys.path.append(root_dir)

from config import Config


class NewDifyManager:
    def __init__(self,project_config=Config(), config_file="new_dify_config.json"):
        """
        初始化 NewDifyManager 类实例。
        :param project_config: 项目配置。
        :param config_file: 用于存储用户对话 ID 的配置文件。
        """
        
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构造配置文件的完整路径（与当前文件同级）
        self.config_file = os.path.join(current_dir, config_file)
        print(f"配置文件路径: {self.config_file}")
        
        self.config = self.load_config()
        self.project_config = project_config
        self.api_key = self.project_config.get("dify_api_key")

        # Dify API 基础URL - 使用http而不是https
        server_ip = self.project_config.get('dify_server_ip')
        self.dify_server_ip = server_ip
        self.base_url = f"http://{server_ip}/v1" if not server_ip.startswith(('http://', 'https://')) else f"{server_ip}/v1"
        print(f"Dify API URL: {self.base_url}")
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
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return {}
        else:
            print(f"配置文件不存在，将创建新文件: {self.config_file}")
            return {}

    def save_config(self):
        """
        保存配置文件。
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")

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

    def clear_all_conversations(self):
        """
        清除所有对话记录，重置配置文件
        """
        print("正在清除所有对话记录...")
        self.config = {}
        self.save_config()
        print("所有对话记录已清除")

    def handle_response(self, response):
        """
        处理API响应，提取文本和语音内容
        :param response: API响应对象
        :return: 处理后的响应内容列表
        """
        results = []
        content = response.get('answer', '')
        
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

        if '<voice>' in content:
            print("提取语音内容")
            # 使用正则表达式提取Dify格式的语音URL
            voice_pattern = r'\[.*?\]\((.*?)\)'
            voice_contents = re.findall(voice_pattern, content, re.DOTALL)
            if voice_contents:
                for voice_url in voice_contents:
                    # 构建完整的URL
                    full_url = f"http://{self.dify_server_ip}{voice_url}"
                    results.append({
                        'type': 'voice',
                        'content': full_url
                    })

        if '<emoji>' in content:
            print("提取表情包内容")
            emoji_contents = re.findall(r'<emoji>(.*?)</emoji>', content, re.DOTALL)
            if emoji_contents:
                for emoji_path in emoji_contents:
                    # 从完整路径中提取文件名（不包含扩展名）
                    emoji_name = os.path.splitext(os.path.basename(emoji_path))[0]
                    results.append({
                        'type': 'emoji',
                        'content': emoji_name
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
            "response_mode": "blocking",  # 改为blocking模式
            "user": wxid  # 添加用户标识
        }
        
        if conversation_id:
            print(f"继续对话，ID: {conversation_id}")
            payload["conversation_id"] = conversation_id
        else:
            print("开始新对话")
            
        try:
            print(f"发送请求到: {endpoint}")
            print(f"请求参数: {payload}")
            response = requests.post(endpoint, headers=self.headers, json=payload, verify=False)  # 添加verify=False
            
            if response.status_code != 200:
                error_msg = f"API请求失败: 状态码 {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f", 错误信息: {error_data}"
                except:
                    error_msg += f", 响应内容: {response.text}"
                print(error_msg)
                return {"answer": error_msg}
            
            data = response.json()
            print(f"API响应: {data}")
            
            # 提取并保存conversation_id
            if "conversation_id" in data:
                self.set_conversation_id(wxid, data["conversation_id"])
                
            return data
        except requests.exceptions.RequestException as e:
            error_msg = f"请求异常: {str(e)}"
            print(error_msg)
            return {"answer": error_msg}
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(error_msg)
            return {"answer": error_msg}

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
