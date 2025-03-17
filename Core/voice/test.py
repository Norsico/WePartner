from pydub import AudioSegment
import os
import subprocess

def check_ffmpeg():
    """检查 FFmpeg 是否已安装并可用"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def wav_to_mp3(wav_path: str, bitrate: str = "192k") -> int:
    """将 WAV 文件转换为 MP3 格式并覆盖原文件
    
    Args:
        wav_path: 输入 WAV 文件的路径
        bitrate: MP3 文件的比特率，默认为 "192k"
        
    Returns:
        MP3 文件的时长（毫秒），失败返回0
    """
    # 首先检查 FFmpeg 是否可用
    if not check_ffmpeg():
        print("错误：FFmpeg 未安装或不在 PATH 中。请安装 FFmpeg 并确保它在系统 PATH 中。")
        return 0
        
    try:
        # 检查文件是否存在
        if not os.path.exists(wav_path):
            print(f"错误：文件不存在 - {wav_path}")
            return 0
            
        # 生成输出MP3文件路径（替换扩展名）
        mp3_path = os.path.splitext(wav_path)[0] + '.mp3'
        
        # 加载 WAV 文件
        audio = AudioSegment.from_wav(wav_path)
        
        # 导出为 MP3 格式
        audio.export(mp3_path, format="mp3", bitrate=bitrate)
        
        # 删除原始 WAV 文件
        os.remove(wav_path)
        
        # 返回音频时长（毫秒）
        return len(audio)
    except Exception as e:
        print(f"WAV 转 MP3 失败: {str(e)}")
        return 0
    

# 测试代码
print(f"FFmpeg 是否可用: {check_ffmpeg()}")
test_file = r"E:\Cursor-Main\wxChatBot\Core\voice\test_voice.wav"
print(f"检查文件是否存在: {os.path.exists(test_file)}")
result = wav_to_mp3(test_file)
print(f"转换结果: {result}")