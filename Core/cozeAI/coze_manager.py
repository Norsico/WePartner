import os
import json
import sys
import re
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL

class CozeChatManager:
    def __init__(self, api_token, base_url=COZE_CN_BASE_URL, config_file="coze_config.json"):
        """
        初始化 CozeChatManager 类实例。
        :param api_token: Coze 平台的 API 访问令牌，如果未提供，则从环境变量 COZE_API_TOKEN 获取。
        :param base_url: Coze API 的基础 URL，默认为 Coze 官方地址。
        :param config_file: 用于存储用户对话 ID 的配置文件。
        """
        self.api_token = api_token

        self.coze = Coze(auth=TokenAuth(token=self.api_token), base_url=base_url)
        self.config_file = config_file
        self.config = self.load_config()
        # 获取当前脚本的目录路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(script_dir)
        
        # 构造配置文件的完整路径
        self.config_file = os.path.join(script_dir, config_file)
        self.config = self.load_config()
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
        # 假设 response 是一个字典，包含返回的内容
        content = response.get('response')

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

    def chat_with_bot(self, bot_id: str, wxid: str, user_message: str):
        """
        与智能体进行对话。
        :param bot_id: 智能体的 ID。
        :param wxid: 用户的微信 ID。
        :param user_message: 用户发送的消息。
        :return: 包含对话 ID 和智能体的回复内容的字典。
        """
        conversation_id = self.get_conversation_id(wxid)
        if conversation_id:
            print(f"Continuing conversation with ID: {conversation_id}")
        else:
            print("Starting a new conversation.")

        chat_iterator = self.coze.chat.stream(
            bot_id=bot_id,
            user_id=wxid,
            conversation_id=conversation_id,
            additional_messages=[Message.build_user_question_text(user_message)]
        )

        response = ""
        for event in chat_iterator:
            if event.event == ChatEventType.CONVERSATION_CHAT_CREATED or event.event == ChatEventType.CONVERSATION_CHAT_IN_PROGRESS:
                # 获取对话的 ID
                conversation_id = event.chat.conversation_id
                self.set_conversation_id(wxid, conversation_id)
            elif event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                # 获取增量消息
                if event.message:
                    response += event.message.content

        return {
            "response": response
        }

# 示例用法
if __name__ == "__main__":
    # 初始化 CozeChatManager 实例
    coze_manager = CozeChatManager(api_token="")

    # 智能体的 ID 和用户微信 ID
    bot_id = "7489710610729566242"
    wxid = "wxid_123"

    # 用户发送的消息
    user_message = "你好啊"

    # 与智能体对话并获取回复
    result = coze_manager.chat_with_bot(bot_id=bot_id, wxid=wxid, user_message=user_message)
    # print(f"Conversation ID: {result['conversation_id']}")
    print(f"Bot response: {result['response']}")

    # # 继续对话
    # user_message = "What's the weather like today?"
    # result = coze_manager.chat_with_bot(bot_id=bot_id, wxid=wxid, user_message=user_message)
    # print(f"Conversation ID: {result['conversation_id']}")
    # print(f"Bot response: {result['response']}")
