import json
import requests
import os
import re
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class FileInfo:
    type: str
    transfer_method: str
    url: str

class DifyChatflow:
    def __init__(self, api_key: str, description: str = None, base_url: str = "http://localhost/v1", config_file: str = None):
        """初始化DifyChatflow客户端
        
        Args:
            api_key: Dify API密钥
            description: API Key的描述信息
            base_url: Dify API基础URL
            config_file: 配置文件路径
        """
        self.api_key = api_key
        self.description = description
        self.base_url = base_url.rstrip('/')
        self.config_file = config_file or os.path.join(os.path.dirname(os.path.abspath(__file__)), "dify_config.json")
        
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.conversations = self._load_conversations()

    def _load_conversations(self) -> Dict:
        """从配置文件加载对话信息"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"chatflow": {}}

            # 确保必要的结构存在
            if "chatflow" not in data:
                data["chatflow"] = {}
            if self.description not in data["chatflow"]:
                data["chatflow"][self.description] = self._create_default_config()
            elif "conversations" not in data["chatflow"][self.description]:
                # 保留现有信息，添加缺失的字段
                current_config = data["chatflow"][self.description]
                default_config = self._create_default_config()
                default_config.update(current_config)
                data["chatflow"][self.description] = default_config

            # 更新基础URL和API Key
            data["chatflow"][self.description]["base_url"] = self.base_url
            data["chatflow"][self.description]["api_key"] = self.api_key
            
            # 保存更新后的配置
            self._save_config(data)
            return data
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return {"chatflow": {self.description: self._create_default_config()}}

    def _create_default_config(self) -> Dict:
        """创建默认配置"""
        return {
            "api_key": self.api_key,
            "created_at": self._get_current_date(),
            "base_url": self.base_url,
            "conversations": {}
        }

    def _save_config(self, data: Dict):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")

    def _get_current_date(self) -> str:
        """获取当前日期"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    def _save_conversations(self):
        """保存对话信息到配置文件"""
        self._save_config(self.conversations)


    def save_conversation(self, conversation_id: str, name: str = None):
        """保存对话信息
        
        Args:
            conversation_id: 对话ID
            name: 对话名称
        """
        if "chatflow" not in self.conversations:
            self.conversations["chatflow"] = {}
            
        if self.description not in self.conversations["chatflow"]:
            self.conversations["chatflow"][self.description] = {
                "api_key": self.api_key,
                "created_at": self._get_current_date(),
                "conversations": {}
            }
            
        # 生成对话名称
        conversation_name = name or f"对话_{len(self.conversations['chatflow'][self.description]['conversations']) + 1}"
        
        # 确保对话名称唯一
        base_name = conversation_name
        counter = 1
        while conversation_name in self.conversations["chatflow"][self.description]["conversations"]:
            counter += 1
            conversation_name = f"{base_name}_{counter}"
            
        self.conversations["chatflow"][self.description]["conversations"][conversation_name] = conversation_id
        self._save_conversations()

    def get_conversation_id(self, name: str) -> str:
        """根据对话名称获取对话ID
        
        Args:
            name: 对话名称
            
        Returns:
            str: 对话ID，如果不存在则返回None
        """
        conversations = self.conversations.get("chatflow", {}).get(self.description, {}).get("conversations", {})
        if isinstance(conversations, dict):
            return conversations.get(name)
        return None

    def get_conversation_name_by_id(self, conversation_id: str) -> str:
        """根据对话ID获取对话名称
        
        Args:
            conversation_id: 对话ID
            
        Returns:
            str: 对话名称，如果不存在则返回None
        """
        conversations = self.conversations.get("chatflow", {}).get(self.description, {}).get("conversations", {})
        for name, conv_id in conversations.items():
            if conv_id == conversation_id:
                return name
        return None

    def list_conversations(self) -> Dict[str, str]:
        """获取当前API Key下的所有对话列表
        
        Returns:
            Dict[str, str]: 对话名称到对话ID的映射
        """
        try:
            if self.description in self.conversations.get("chatflow", {}):
                conversations = self.conversations["chatflow"][self.description].get("conversations", {})
                return conversations if isinstance(conversations, dict) else {}
            return {}
        except Exception as e:
            print(f"获取对话列表失败: {str(e)}")
            return {}

    def get_api_key_info(self) -> Dict:
        """获取当前API Key的信息"""
        if "chatflow" in self.conversations and self.description in self.conversations["chatflow"]:
            return {
                "created_at": self.conversations["chatflow"][self.description].get("created_at", ""),
                "conversation_count": len(self.conversations["chatflow"][self.description].get("conversations", {}))
            }
        return {}

    def update_api_key_description(self, description: str):
        """更新API Key的描述信息"""
        if "chatflow" in self.conversations and self.description in self.conversations["chatflow"]:
            self.description = description
            self.conversations["chatflow"][self.description]["description"] = description
            self._save_conversations()

    def chat(self, 
             query: str,
             conversation_name: str = None,
             inputs: Dict = None,
             conversation_id: str = "",
             user: str = "User",
             files: List[FileInfo] = None) -> Dict:
        """发送聊天请求
        
        Args:
            query: 用户输入的问题
            conversation_name: 对话名称，如果提供，将尝试继续该对话
            inputs: 输入参数字典
            conversation_id: 会话ID（优先级高于conversation_name）
            user: 用户标识
            files: 文件列表
            
        Returns:
            响应字典
        """
        # 如果提供了对话名称且未指定conversation_id，尝试获取对应的conversation_id
        if conversation_name and not conversation_id:
            conversation_id = self.get_conversation_id(conversation_name)
            
        url = f"{self.base_url}/chat-messages"
        
        payload = {
            "inputs": inputs or {},
            "query": query,
            "response_mode": "blocking",
            "conversation_id": conversation_id,
            "user": user,
            "files": [
                {
                    "type": f.type,
                    "transfer_method": f.transfer_method,
                    "url": f.url
                } for f in (files or [])
            ]
        }
        print(f"请求参数: {payload}")
        print("正在生成回复...")

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            # 如果是新对话，保存对话信息
            if not conversation_id and result.get("conversation_id"):
                self.save_conversation(result["conversation_id"], name=conversation_name)
                
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")

    def delete_conversation(self, conversation_id: str = None, name: str = None, user: str = "User") -> bool:
        """删除指定的对话
        
        Args:
            conversation_id: 要删除的对话ID
            name: 要删除的对话名称
            user: 用户标识
            
        Returns:
            bool: 删除是否成功
        """
        # 如果提供了对话名称，根据名称获取ID
        if name and not conversation_id:
            conversation_id = self.get_conversation_id(name)
            if not conversation_id:
                raise Exception(f"未找到名称为 '{name}' 的对话")
                
        if not conversation_id:
            raise Exception("必须提供对话ID或对话名称")
            
        url = f"{self.base_url}/conversations/{conversation_id}"
        payload = {"user": user}
        
        try:
            response = requests.delete(url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            # 如果删除成功，同时从配置文件中移除
            if result.get("result") == "success":
                conversations = self.conversations.get("chatflow", {}).get(self.description, {})
                # 找到并删除对话
                name_to_delete = None
                for conv_name, conv_id in conversations.items():
                    if conv_id == conversation_id:
                        name_to_delete = conv_name
                        break
                        
                if name_to_delete:
                    del self.conversations["chatflow"][self.description]["conversations"][name_to_delete]
                    self._save_conversations()
                return True
            return False
        except requests.exceptions.RequestException as e:
            raise Exception(f"删除对话失败: {str(e)}")

    def delete_conversation_by_name(self, name: str, user: str = "User") -> bool:
        """根据对话名称删除对话
        
        Args:
            name: 要删除的对话名称
            user: 用户标识
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            Exception: 当找不到指定名称的对话时抛出异常
        """
        conversation_id = self.get_conversation_id(name)
        if not conversation_id:
            raise Exception(f"未找到名称为 '{name}' 的对话")
        
        return self.delete_conversation(conversation_id=conversation_id, user=user)
    
    @staticmethod
    def handle_response(response):
        # 假设 response 是一个字典，包含返回的内容
        content = response.get('answer', '')

        results = []

        # 检查返回的内容类型
        if '<text>' in content:
            # 提取文本内容
            text_contents = re.findall(r'<text>(.*?)</text>', content, re.DOTALL)
            if text_contents:
                for text in text_contents:
                    results.append({
                        'type': 'text',
                        'content': text.strip()
                    })

        if '<voice>' in content:
            # 提取语音内容
            voice_contents = re.findall(r'<voice>(.*?)</voice>', content, re.DOTALL)
            if voice_contents:
                for voice_url in voice_contents:
                    # 使用正则表达式提取括号里的内容
                    pattern = r'\((.*?)\)'
                    matches = re.findall(pattern, voice_url)
                    voice_file_url = f"http://localhost{matches[0]}"
                    results.append({
                        'type': 'voice',
                        'content': voice_file_url.strip()
                    })
        
        return results

if __name__ == '__main__':
    # 测试代码
    api_key = "app-s45SiU5pHsQoow16fjUfMjuq"
    base_url = "http://localhost/v1"
    
    # 初始化客户端
    client = DifyChatflow(
        api_key=api_key,
        description="voice_http_test",
        base_url=base_url
    )
    
    try:
        # # 列出当前API Key下的所有对话
        # conversations = client.list_conversations()
        # print(f"当前API Key的对话列表: {conversations}")

        # 文本<text>
        # 图片<image>
        # 语音<voice>
        # 文件<files>
        
        # 开始新对话
        # response = client.chat(query="哈喽", conversation_name="新对话")
        # print(f"AI回复: {response.get('answer')}\n")
        
        # 继续已有对话
        response = client.chat(query="不要嘛", conversation_name="新对话")
        # 使用正则表达式提取括号里的内容
        res = client.handle_response(response)

        print(res)


        # pattern = r'\((.*?)\)'
        # matches = re.findall(pattern, response.get('answer'))
        # res = f"http://localhost{matches[0]}"
        # print(f"AI回复:\n{res}")
        # http://localhost/files/tools/b1f4d8c8-48c6-44ba-b067-af16a63ebdd3.bin?timestamp=1743308351&nonce=a8ef791e3bc1e268c4a81bf5a275b4d9&sign=Q-UnUSuXHsMydF9Ymt0Ku4a8vP6fS-ZiiFPkx05vaVY=
        
        # # 再次列出对话
        # print("\n更新后的对话列表:")
        # for name, conv_id in client.list_conversations().items():
        #     print(f"名称: {name}, ID: {conv_id}")
        # print()

        
        # # 删除对话（使用新方法）
        # client.delete_conversation_by_name("测试对话_1")
            
    except Exception as e:
        print(f"错误: {str(e)}")
    