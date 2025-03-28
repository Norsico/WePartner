import os
import json
from typing import Dict, Optional, List

class SettingsManager:
    def __init__(self, settings_file: str = None):
        """初始化设置管理器
        
        Args:
            settings_file: 设置文件路径，默认为web目录下的settings.json
        """
        if settings_file is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.settings_file = os.path.join(current_dir, "settings.json")
        else:
            self.settings_file = settings_file
            
        self.settings = self._load_settings()
        
    def _load_settings(self) -> Dict:
        """加载设置文件"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载设置文件失败: {str(e)}")
                return self._get_default_settings()
        else:
            # 创建默认设置
            default_settings = self._get_default_settings()
            self._save_settings(default_settings)
            return default_settings
            
    def _save_settings(self, settings: Dict):
        """保存设置到文件"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置文件失败: {str(e)}")
            
    def _get_default_settings(self) -> Dict:
        """获取默认设置"""
        return {
            "selected_chatflow": {
                "description": "",  # 选中的chatflow描述
                "api_key": "",      # 选中的chatflow的API Key
                "conversation": {    # 选中的单个对话
                    "name": "",     # 对话名称
                    "id": ""        # 对话ID
                }
            },
            "voice_reply_enabled": False,  # 是否启用语音回复
            "timer_seconds": 5  # 消息聚合等待时间（秒）
        }
        
    def get_settings(self) -> Dict:
        """获取当前设置"""
        return self.settings
        
    def update_settings(self, settings: Dict) -> bool:
        """更新设置
        
        Args:
            settings: 新的设置数据
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 更新内存中的设置
            self.settings.update(settings)
            # 保存到文件
            self._save_settings(self.settings)
            return True
        except Exception as e:
            print(f"更新设置失败: {str(e)}")
            return False
            
    def get_selected_chatflow(self) -> Dict:
        """获取当前选中的chatflow信息"""
        return self.settings.get("selected_chatflow", {})
        
    def set_selected_chatflow(self, description: str, api_key: str, conversation_name: str = "", conversation_id: str = "") -> bool:
        """设置选中的chatflow和对话
        
        Args:
            description: chatflow描述
            api_key: API Key
            conversation_name: 选中的对话名称
            conversation_id: 选中的对话ID
            
        Returns:
            bool: 是否设置成功
        """
        try:
            self.settings["selected_chatflow"] = {
                "description": description,
                "api_key": api_key,
                "conversation": {
                    "name": conversation_name,
                    "id": conversation_id
                }
            }
            self._save_settings(self.settings)
            return True
        except Exception as e:
            print(f"设置chatflow失败: {str(e)}")
            return False
            
    def is_voice_reply_enabled(self) -> bool:
        """获取是否启用语音回复"""
        return self.settings.get("voice_reply_enabled", False)
        
    def set_voice_reply_enabled(self, enabled: bool) -> bool:
        """设置是否启用语音回复
        
        Args:
            enabled: 是否启用
            
        Returns:
            bool: 是否设置成功
        """
        try:
            self.settings["voice_reply_enabled"] = enabled
            self._save_settings(self.settings)
            return True
        except Exception as e:
            print(f"设置语音回复失败: {str(e)}")
            return False
            
    def set_setting(self, key: str, value: any) -> bool:
        """设置单个配置项
        
        Args:
            key: 配置项键名
            value: 配置项值
            
        Returns:
            bool: 是否设置成功
        """
        try:
            self.settings[key] = value
            self._save_settings(self.settings)
            return True
        except Exception as e:
            print(f"设置配置项失败: {str(e)}")
            return False 