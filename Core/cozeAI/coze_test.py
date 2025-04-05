import os

from pathlib import Path
from cozepy import Coze, TokenAuth, BotPromptInfo, Message, ChatEventType, MessageContentType, COZE_CN_BASE_URL

class CozeAI:
    def __init__(self, api_token=None, base_url=COZE_CN_BASE_URL):
        """
        初始化 CozeAI 类实例。
        :param api_token: Coze 平台的 API 访问令牌，如果未提供，则从环境变量 COZE_API_TOKEN 获取。
        :param base_url: Coze API 的基础 URL，默认为 Coze 官方地址。
        """
        self.api_token = api_token or os.getenv("COZE_API_TOKEN")
        if not self.api_token:
            raise ValueError("API token is required but not provided or found in environment variables.")
        self.coze = Coze(auth=TokenAuth(token=self.api_token), base_url=base_url)

    def chat_with_bot(self, bot_id: str, user_id: str, user_message: str):
        """
        与智能体进行对话。
        :param bot_id: 智能体的 ID。
        :param user_id: 用户的 ID，用于标识对话的用户。
        :param user_message: 用户发送的消息。
        :return: 包含对话 ID 和智能体的回复内容的字典。
        """
        chat_iterator = self.coze.chat.stream(
            bot_id=bot_id,
            user_id=user_id,
            additional_messages=[Message.build_user_question_text(user_message)]
        )

        response = ""
        conversation_id = None
        for event in chat_iterator:
            if event.event == ChatEventType.CONVERSATION_CHAT_CREATED:
                # 获取对话的 ID
                conversation_id = event.chat.conversation_id
            elif event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                # 获取增量消息
                if event.message:
                    response += event.message.content
        return {
            "conversation_id": conversation_id,
            "response": response
        }

    def continue_chat_with_bot(self, bot_id: str, user_id: str, user_message: str, conversation_id: str):
        """
        继续与智能体进行对话。
        :param bot_id: 智能体的 ID。
        :param user_id: 用户的 ID，用于标识对话的用户。
        :param user_message: 用户发送的消息。
        :param conversation_id: 已有的对话 ID。
        :return: 包含对话 ID 和智能体的回复内容的字典。
        """
        chat_iterator = self.coze.chat.stream(
            bot_id=bot_id,
            user_id=user_id,
            conversation_id=conversation_id,
            additional_messages=[Message.build_user_question_text(user_message)]
        )

        response = ""
        for event in chat_iterator:
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                # 获取增量消息
                if event.message:
                    response += event.message.content
        return {
            "conversation_id": conversation_id,
            "response": response
        }
# 示例用法
if __name__ == "__main__":

    # 初始化 CozeAI 实例
    coze_ai = CozeAI(api_token="pat_ZhGBBo8lJwQyhdir0tZXzoBZP09KplQWnzbfTjwp6BCJ5rGRzE8Z00mkOMfJbsFO")

    # 智能体的 ID 和用户 ID
    bot_id = "7489670327732011034"
    user_id = "user123"

    # 用户发送的消息
    user_message = "你好"

    # 与智能体对话并获取回复
    result = coze_ai.chat_with_bot(bot_id=bot_id, user_id=user_id, user_message=user_message)
    print(f"Conversation ID: {result['conversation_id']}")
    print(f"Bot response: {result['response']}")

    # 继续对话
    user_message = "What's the weather like today?"
    continue_result = coze_ai.continue_chat_with_bot(
        bot_id=bot_id,
        user_id=user_id,
        user_message=user_message,
        conversation_id=result['conversation_id']
    )
    print(f"Conversation ID: {continue_result['conversation_id']}")
    print(f"Bot response: {continue_result['response']}")

