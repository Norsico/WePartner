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


def mp3_to_silk(mp3_path: str, silk_path: str) -> int:
    """Convert MP3 file to SILK format
    Args:
        mp3_path: Path to input MP3 file
        silk_path: Path to output SILK file
    Returns:
        Duration of the SILK file in milliseconds
    """
    # First load the MP3 file
    audio = AudioSegment.from_file(mp3_path)
    
    # Convert to mono and set sample rate to 24000Hz
    # TODO: 下面的参数可能需要调整
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(24000)
    
    # Export to PCM
    pcm_path = os.path.splitext(mp3_path)[0] + '.pcm'
    audio.export(pcm_path, format='s16le')
    
    # Convert PCM to SILK
    pilk.encode(pcm_path, silk_path, pcm_rate=24000, tencent=True)
    
    # Clean up temporary PCM file
    os.remove(pcm_path)
    
    # Get duration of the SILK file
    duration = pilk.get_duration(silk_path)
    return duration
