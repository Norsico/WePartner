import subprocess
import os

def check_ffmpeg():
    """检查 FFmpeg 是否已安装并可用"""
    ffmpeg_path = "./voice_model/ffmpeg/bin"
    # 更新环境变量 PATH
    os.environ["PATH"] = f"{ffmpeg_path};{os.environ['PATH']}"
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

print(check_ffmpeg())
