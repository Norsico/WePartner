import json
from typing import Dict, Any, Optional, List, Union

import requests

from Core.Logger import Logger

logger = Logger()


class Dify:
    def __init__(self, base_url="http://192.168.43.236/v1", api_key="your_api_key"):
        """
        初始化 Dify 类
        :param base_url: Dify 服务的 API 基础 URL
        :param api_key: Dify 的 API 密钥
        """
        self.base_url = base_url
        self.api_key = api_key
        self.workflow_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.upload_headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def upload_file(self, file_path: str, type: str, user: str) -> Optional[str]:
        """
        上传文件到 Dify
        :param file_path: 文件路径
        :param type: 文件类型
        :param user: 用户标识
        :return: 文件 ID 或 None
        """
        upload_url = f"{self.base_url}/files/upload"
        try:
            with open(file_path, 'rb') as file:
                files = {
                    'file': (file_path, file, 'text/plain')  # 确保文件以适当的 MIME 类型上传
                }
                data = {
                    "user": user,
                    "type": type  # 设置文件类型
                }
                response = requests.post(upload_url, headers=self.upload_headers, files=files, data=data)
                if response.status_code == 201:  # 201 表示创建成功
                    logger.success("文件上传成功")
                    return response.json().get("id")  # 获取上传的文件 ID
                else:
                    logger.error(f"文件上传失败，状态码: {response.status_code}")
        except Exception as e:
            logger.error(f"发生错误: {str(e)}")
        return None

    def run_workflow(self, data: Union[Dict, str], user: str, streaming: bool = False) -> Any:
        """
        运行工作流
        :param data: 工作流输入数据，可以是字典或字符串
        :param user: 用户标识
        :param streaming: 是否使用流式输出
        :return: 工作流执行结果
        """
        # 如果输入是字符串，假设是简单的文本消息
        if isinstance(data, str):
            data = {"message": data}
            
        # 如果输入是包含message键的字典，转换为Dify API需要的格式
        if isinstance(data, dict) and "message" in data:
            data = {"message": data["message"]}
            
        return self._run_workflow_internal(data, user, streaming)
        
    def run_workflow_with_file(self, message: str, file_path: str, file_type: str, user: str, streaming: bool = False) -> Any:
        """
        运行带文件的工作流
        :param message: 消息文本
        :param file_path: 文件路径
        :param file_type: 文件类型
        :param user: 用户标识
        :param streaming: 是否使用流式输出
        :return: 工作流执行结果
        """
        # 先上传文件
        file_id = self.upload_file(file_path, file_type, user)
        if not file_id:
            return {"status": "error", "message": "文件上传失败"}
            
        # 构建包含文件的输入数据
        data = {
            "message": message,
            "files": [
                {
                    "transfer_method": "local_file",
                    "upload_file_id": file_id,
                    "type": file_type
                }
            ]
        }
        
        return self._run_workflow_internal(data, user, streaming)
        
    def run_workflow_with_image(self, message: str, image_path: str, user: str, streaming: bool = False) -> Any:
        """
        运行带图片的工作流
        :param message: 消息文本
        :param image_path: 图片路径
        :param user: 用户标识
        :param streaming: 是否使用流式输出
        :return: 工作流执行结果
        """
        return self.run_workflow_with_file(message, image_path, "image", user, streaming)
        
    def run_workflow_with_history(self, message: str, history: List[Dict], user: str, streaming: bool = False) -> Any:
        """
        运行带聊天历史的工作流
        :param message: 消息文本
        :param history: 聊天历史，格式为[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        :param user: 用户标识
        :param streaming: 是否使用流式输出
        :return: 工作流执行结果
        """
        data = {
            "message": message,
            "history": history
        }
        
        return self._run_workflow_internal(data, user, streaming)

    def _run_workflow_internal(self, data: Dict, user: str, streaming: bool = False) -> Any:
        """
        内部方法：运行工作流
        :param data: 工作流输入数据
        :param user: 用户标识
        :param streaming: 是否使用流式输出
        :return: 工作流执行结果
        """
        workflow_url = f"{self.base_url}/workflows/run"
        if streaming:
            request_data = {
                "inputs": data,
                "response_mode": "streaming",
                "user": user
            }
            try:
                response = requests.post(workflow_url, headers=self.workflow_headers, json=request_data, stream=True)
                if response.status_code == 200:
                    logger.success("工作流执行成功，开始流式输出：")
                    full_text = ""  # 用于存储完整的文本内容
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith("data: "):
                                event_data = json.loads(decoded_line[6:])  # 去掉前缀 "data: "
                                if event_data["event"] == "text_chunk":
                                    text_chunk = event_data["data"]["text"]
                                    full_text += text_chunk  # 拼接文本片段
                                    print(text_chunk, end="")  # 实时打印文本片段
                    return full_text
                else:
                    logger.error(f"工作流执行失败，状态码: {response.status_code}")
                    logger.debug(f"API Response: {response.text}")
                    return {"status": "error",
                            "message": f"Failed to execute workflow, status code: {response.status_code}"}
            except Exception as e:
                logger.error(f"发生错误: {str(e)}")
                return {"status": "error", "message": str(e)}
        else:
            request_data = {
                "inputs": data,
                "response_mode": "blocking",
                "user": user
            }
            logger.info("开始运行工作流：")
            try:
                response = requests.post(workflow_url, headers=self.workflow_headers, json=request_data)
                if response.status_code == 200:
                    logger.success("工作流执行成功")
                    return response.json()['data']['outputs']['text']
                else:
                    logger.error(f"工作流执行失败，状态码: {response.status_code}")
                    logger.debug(f"API Response: {response.text}")
                    return {"status": "error",
                            "message": f"Failed to execute workflow, status code: {response.status_code}"}
            except Exception as e:
                logger.error(f"发生错误: {str(e)}")
                return {"status": "error", "message": str(e)}


# 使用示例
if __name__ == "__main__":
    file_path = "./test.txt"  # 待上传的文件路径
    user = "difyuser"

    dify = Dify(api_key="app-V8tQlVW1Aw6R0yrFNILjfAbq")  # 初始化 DifyAPI 类
    
    # 示例1：简单文本消息
    result1 = dify.run_workflow("你好，请介绍一下自己", user)
    print(f"文本消息结果: {result1}")
    
    # 示例2：上传文件并处理
    result2 = dify.run_workflow_with_file("请分析这个文件", file_path, "TXT", user)
    print(f"文件处理结果: {result2}")
    
    # 示例3：带聊天历史的对话
    history = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么我可以帮助你的吗？"}
    ]
    result3 = dify.run_workflow_with_history("继续我们的对话", history, user)
    print(f"带历史的对话结果: {result3}")
