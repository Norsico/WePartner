import os

from pydub import AudioSegment
import subprocess


try:
    from pydub import AudioSegment
except ImportError:
    print("import pydub failed, wechat voice conversion will not be supported. Try: pip install pydub")

try:
    import pilk
except ImportError:
    print("import pilk failed, silk voice conversion will not be supported. Try: pip install pilk")

def check_ffmpeg():
    """检查 FFmpeg 是否已安装并可用"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


try:
    if not check_ffmpeg():
        ffmpeg_path = "./voice_model/ffmpeg/bin"
        # 更新环境变量 PATH
        os.environ["PATH"] = f"{ffmpeg_path};{os.environ['PATH']}"
        if not check_ffmpeg():
            print("ffmpeg path will not be set. need /voice_model/ffmpeg/bin")
except ImportError:
    print("ffmpeg path will not be set. need /voice_model/ffmpeg/bin")

def wav_to_silk(wav_path: str, silk_path: str) -> int:
    """Convert MP3 file to SILK format
    Args:
        wav_path: Path to input WAV file
        silk_path: Path to output SILK file
    Returns:
        Duration of the SILK file in milliseconds
    """

    # 将wav文件转换为mp3文件
    mp3_path = wav_to_mp3(wav_path)
    # load the MP3 file
    audio = AudioSegment.from_file(mp3_path)
    
    # Convert to mono and set sample rate to 24000Hz
    # TODO: 下面的参数可能需要调整
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(24000)
    
    print("Export to PCM")
    pcm_path = os.path.splitext(mp3_path)[0] + '.pcm'
    print(pcm_path)
    audio.export(pcm_path, format='s16le')
    
    print("Convert PCM to SILK")
    pilk.encode(pcm_path, silk_path, pcm_rate=24000, tencent=True)
    
    print("Clean up temporary PCM file")
    os.remove(pcm_path)
    
    print("Get duration of the SILK file")
    duration = pilk.get_duration(silk_path)
    return duration


def wav_to_mp3(wav_path: str, bitrate: str = "192k") -> str:
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

        
    try:
        # 检查文件是否存在
        if not os.path.exists(wav_path):
            print(f"错误：文件不存在 - {wav_path}")
            return None

        # 检查是否是.wav文件
        if not wav_path.endswith('.wav'):
            print(f"错误：文件不是.wav文件 - {wav_path}")
            return None
            
        # 生成输出MP3文件路径（替换扩展名）
        mp3_path = os.path.splitext(wav_path)[0] + '.mp3'
        
        # 加载 WAV 文件
        audio = AudioSegment.from_wav(wav_path)
        
        # 导出为 MP3 格式
        audio.export(mp3_path, format="mp3", bitrate=bitrate)
        
        # 删除原始 WAV 文件
        os.remove(wav_path)
        
        # 返回MP3文件路径
        return mp3_path
    except Exception as e:
        print(f"WAV 转 MP3 失败: {str(e)}")
        return None
    
if __name__ == "__main__":
    # test_file = r".\test_voice.wav"
    # wav_to_mp3(test_file)
    print(check_ffmpeg())
    