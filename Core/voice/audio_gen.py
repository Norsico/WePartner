import os
import sys
import requests
import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../.."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from Core.bridge.temp_dir import TmpDir
from config import Config

class AudioGen:
    
    def __init__(self):
        self.config = Config()
        self.voice_url = self.config.get("GPT-SoVITS_url")
        self.language = self.config.get("text_language")
        self.tmp_dir = TmpDir()


    def generate_voice(self, text):
        # 获取tmp文件夹路径
        temp_dir = self.tmp_dir.path()
        # 生成语音文件名
        timestamp = self.get_current_timestamp()
        relative_voice_file = f"voice_{timestamp}.wav"
        voice_file = os.path.join(temp_dir, relative_voice_file)
        # 发送语音请求
        data = {
            'text': text,
            'text_language': self.language
        }
        try:
            response = requests.post(self.voice_url, json=data)
            if response.status_code == 200:
                # 保存语音文件
                with open(voice_file, "wb") as f:
                    f.write(response.content)
                print("语音文件已生成")
                # 返回绝对路径
                return os.path.abspath(voice_file)
            else:
                print(f"语音生成失败，状态码：{response.status_code}")
                return None
        except Exception as e:
            print(f"语音生成失败，错误信息：{e}")
            return None
            
    @staticmethod
    def get_current_timestamp():
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

if __name__ == '__main__':
    gen_audio = AudioGen()
    audio_path = gen_audio.generate_voice("快点下课吧")
    print(f"生成的音频文件绝对路径: {audio_path}")

