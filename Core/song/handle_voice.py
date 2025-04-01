import requests
import time
import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_dir = os.path.dirname(current_file_path)
# 添加子文件夹路径
handle_song_path = os.path.join(current_dir, 'handleSong')
bgm_path = os.path.join(handle_song_path, 'bgm_HP5')
human_path = os.path.join(handle_song_path, 'human_HP5')
bgm_last_path = os.path.join(handle_song_path, 'bgm_last')
human_last_path = os.path.join(handle_song_path, 'human_last')
songRAG_path = os.path.join(current_dir, "songRAG")

# 获取路径下的所有文件和文件夹
    
# 过滤出文件
file_len = len([item for item in os.listdir(songRAG_path) if os.path.isfile(os.path.join(songRAG_path, item))])
# 输出文件数量
print(f"路径 {songRAG_path} 下有 {file_len} 个文件。")

for i in range(file_len*2):
    response = requests.post("http://192.168.87.9:7897/run/uvr_convert", json={
    "data": [
        "HP5_only_main_vocal",
        f"{songRAG_path}",
        f"{human_path}",
        None,
        f"{bgm_path}",
        10,
        "wav",
    ]}).json()
    print(f"{i+1}/{file_len*2}")
    time.sleep(1)

for i in range(file_len*2):
    response = requests.post("http://192.168.87.9:7897/run/uvr_convert", json={
    "data": [
        "VR-DeEchoAggressive",
        f"{human_path}",
        f"{bgm_last_path}",
        None,
        f"{human_last_path}",
        10,
        "wav",
    ]}).json()
    print(f"{i+1}/{file_len*2}")
    time.sleep(1)
# data = response["data"]

# print(data)
