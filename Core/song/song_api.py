from http.server import BaseHTTPRequestHandler, HTTPServer
from pydub import AudioSegment
from datetime import datetime
import os
import urllib.parse
import json

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_dir = os.path.dirname(current_file_path)
bgm_dir = os.path.join(current_dir, r"handleSong\bgm_HP5")
human_dir = os.path.join(current_dir, r"handleSong\human_last")
# 获取当前文件所在的tmp目录
tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))), "tmp")

def mix_audio(audio1_path, audio2_path, output_path):
    # 加载两个音频文件
    audio1 = AudioSegment.from_file(audio1_path)
    audio2 = AudioSegment.from_file(audio2_path)

    # 获取两个音频的时长
    duration1 = len(audio1)
    duration2 = len(audio2)

    # 如果时长不同，裁剪较长的音频
    if duration1 > duration2:
        audio1 = audio1[:duration2]
    elif duration2 > duration1:
        audio2 = audio2[:duration1]

    # 混合两个音频
    mixed_audio = audio1.overlay(audio2)

    # 保存混合后的音频
    mixed_audio.export(output_path, format="wav")  # 可以根据需要选择格式

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/find_song'):
            try:
                # 解析URL参数
                parsed_url = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed_url.query)
                
                # 获取歌曲名称参数
                if 'name' not in params:
                    print("错误: 未提供歌曲名称参数")
                    self._send_response({"error": "未提供歌曲名称参数"})
                    return
                
                song_name = params['name'][0]
                
                # 构建要查找的文件路径
                song_file = os.path.join(human_dir, f"{song_name}.wav")
                
                # 检查文件是否存在
                if os.path.exists(song_file):
                    abs_path = os.path.abspath(song_file)
                    print(f"找到歌曲: {abs_path}")
                    # 返回分离人声后的音频 human_dir
                    
                    self._send_response(abs_path)
                else:
                    print(f"未找到歌曲: {song_name}")
                    self._send_response({"error": "未找到歌曲"})
            except Exception as e:
                print(f"处理请求时出错: {str(e)}")
                self._send_response({"error": str(e)})
        
        if self.path.startswith('/return_wav_file'):
            # 解析 URL 中的查询参数
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)

            # 获取文件路径参数
            file_path = query_params.get('path', [None])[0]
            if not file_path:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing 'path' parameter.")
                return

            # 将路径中的反斜杠替换为正斜杠
            file_path = file_path.replace("\\", "/")

            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found.")
                return

            # 读取文件内容并返回
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.end_headers()
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())

        if self.path.startswith('/get_qrcode'):
            pass
        
        if self.path.startswith('/merge_voice'):
            # 解析 URL 中的查询参数
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            # 获取文件路径参数
            human_path = query_params.get('human_path', [None])[0]
            voice_name = query_params.get('voice_name', [None])[0]
            
            # 打印获取的参数
            print(f"human_path: {human_path}")
            print(f"voice_name: {voice_name}")

            # 在bgm_dir文件夹下寻找对应的bgm
            audio_bgm = os.path.join(bgm_dir, f"{voice_name}.wav")

            # 获取当前时间戳（秒级时间戳）
            timestamp = datetime.now().timestamp()

            output_path = os.path.join(tmp_dir, f"{timestamp}.wav")

            mix_audio(human_path, audio_bgm, output_path)

            # self._send_response({
            #     "human_path": human_path,
            #     "voice_name": voice_name,
            #     "out": output_path
            # })
            self._send_response(output_path)

    def _send_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')  # 指定编码为 UTF-8
        self.end_headers()
        if isinstance(data, str):
            self.wfile.write(data.encode('utf-8'))
        else:
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))  # 确保中文字符正确编码

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8001):
    server_address = ('0.0.0.0', port)  # 绑定到所有网络接口
    httpd = server_class(server_address, handler_class)
    print(f"HTTP服务器已启动，监听端口: {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()