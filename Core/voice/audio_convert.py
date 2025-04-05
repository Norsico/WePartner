import os

from pydub import AudioSegment
import subprocess
import shutil



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

def audio_to_silk(audio_path: str, silk_path: str) -> int:
    """Convert MP3 file to SILK format
    Args:
        wav_path: Path to input WAV file
        silk_path: Path to output SILK file
    Returns:
        Duration of the SILK file in milliseconds
    """

    # load the audio file
    audio = AudioSegment.from_file(audio_path)
    
    # Convert to mono and set sample rate to 24000Hz
    # TODO: 下面的参数可能需要调整
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(24000)
    
    print("Export to PCM")
    pcm_path = os.path.splitext(audio_path)[0] + '.pcm'
    print(pcm_path)
    audio.export(pcm_path, format='s16le')
    
    print("Convert PCM to SILK")
    pilk.encode(pcm_path, silk_path, pcm_rate=24000, tencent=True)
    
    print("Clean up temporary PCM file")
    os.remove(pcm_path)
    
    print("Get duration of the SILK file")
    duration = pilk.get_duration(silk_path)
    return duration
    
if __name__ == "__main__":
    # test_file = r".\test_voice.wav"
    # wav_to_mp3(test_file)
    print(check_ffmpeg())
    