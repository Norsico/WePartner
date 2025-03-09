import json

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

    def upload_file(self, file_path: str, type: str, user: str):
        """
        上传文件到 Dify
        :param file_path: 文件路径
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

    def run_workflow(self, data, user, streaming=False):
        """
        内部方法：运行工作流
        :param data: 工作流输入数据
        :param user: 用户标识
        :return: 工作流执行结果
        """
        workflow_url = f"{self.base_url}/workflows/run"
        if streaming:
            data = {
                "inputs": data,
                "response_mode": "streaming",
                "user": user
            }
            try:
                response = requests.post(workflow_url, headers=self.workflow_headers, json=data, stream=True)
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
            data = {
                "inputs": data,
                "response_mode": "blocking",
                "user": user
            }
            logger.info("开始运行工作流：")
            try:
                response = requests.post(workflow_url, headers=self.workflow_headers, json=data)
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
    file_id = dify.upload_file(file_path, "TXT", user)  # 上传文件

    if file_id:
        # 文件上传成功，运行工作流
        data = {
            "input": [
                {
                    "transfer_method": "local_file",
                    "upload_file_id": file_id,
                    "type": "document"
                }
            ]
        }
        result_blocking = dify.run_workflow(data, user, streaming=True)
        print(result_blocking)

    else:
        logger.error("文件上传失败，无法执行工作流")
