import os

from Core.Logger import Logger

logger = Logger()

try:
    from pydub import AudioSegment
except ImportError:
    logger.warning("import pydub failed, wechat voice conversion will not be supported. Try: pip install pydub")

try:
    import pilk
except ImportError:
    logger.warning("import pilk failed, silk voice conversion will not be supported. Try: pip install pilk")


def wav_to_silk(wav_path: str, silk_path: str) -> int:
    """Convert MP3 file to SILK format
    Args:
        mp3_path: Path to input MP3 file
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


def wav_to_mp3(wav_path: str, bitrate: str = "192k") -> int:
    """将 WAV 文件转换为 MP3 格式并覆盖原文件
    
    Args:
        wav_path: 输入 WAV 文件的路径
        bitrate: MP3 文件的比特率，默认为 "192k"
        
    Returns:
        MP3 文件的时长（毫秒）
    """
    try:
        # 生成输出MP3文件路径（替换扩展名）
        mp3_path = os.path.splitext(wav_path)[0] + '.mp3'
        
        # 加载 WAV 文件
        audio = AudioSegment.from_wav(wav_path)
        
        # 导出为 MP3 格式
        audio.export(mp3_path, format="mp3", bitrate=bitrate)
        
        # 删除原始 WAV 文件
        os.remove(wav_path)
        
        # 返回路径
        return mp3_path
    except Exception as e:
        logger.error(f"WAV 转 MP3 失败: {str(e)}")
        return 0
wav_to_mp3("E:/Cursor-Main/wxChatBot/test_voice.wav")
