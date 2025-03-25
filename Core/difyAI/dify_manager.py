import os
import json
from typing import Dict, Optional, List
from .dify_chatflow import DifyChatflow

class DifyManager:
    _instance = None
    _initialized = False

    def __new__(cls, config_dir: str = None):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_dir: str = None):
        """初始化DifyManager
        
        Args:
            config_dir: 配置文件目录，默认为当前目录
        """
        # 防止重复初始化
        if DifyManager._initialized:
            return
            
        if config_dir is None:
            config_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "dify_config.json")
        self.instances: Dict[str, DifyChatflow] = {}
        self.dify_config = {}
        self._load_config()
        DifyManager._initialized = True

    def _load_config(self):
        """加载配置文件并初始化所有已保存的DifyChatflow实例"""
        self.instances = {}  # 清空实例列表，确保重新加载
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.dify_config = config
                    if "chatflow" in config:
                        for description, info in config["chatflow"].items():
                            api_key = info.get("api_key", "")
                            base_url = info.get("base_url", "http://localhost/v1")
                            self.create_instance(api_key, description, base_url)
                print(f"加载配置文件成功，Chatflow数量: {len(self.dify_config.get('chatflow', {}))}")
                
                # 打印一下每个chatflow中的对话
                for cf_name, cf_info in self.dify_config.get('chatflow', {}).items():
                    convs = list(cf_info.get('conversations', {}).keys())
                    print(f"Chatflow={cf_name}, 对话列表={convs}")
            except Exception as e:
                print(f"加载配置文件失败: {str(e)}")
                self.dify_config = {"chatflow": {}}
    
    def get_dify_config(self):
        """获取Dify配置"""
        return self.dify_config

    def save_dify_config(self, config: Dict) -> bool:
        """保存Dify配置到文件
        
        Args:
            config: 要保存的配置字典
            
        Returns:
            bool: 是否保存成功
        """
        try:
            self.dify_config = config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 清空并重新初始化实例列表
            self.instances = {}
            if "chatflow" in config:
                for description, info in config["chatflow"].items():
                    api_key = info.get("api_key", "")
                    base_url = info.get("base_url", "http://localhost/v1")
                    self.create_instance(api_key, description, base_url)
            
            print(f"保存配置文件成功，新的Chatflow数量: {len(config.get('chatflow', {}))}")
            # 打印一下每个chatflow中的对话
            for cf_name, cf_info in config.get('chatflow', {}).items():
                convs = list(cf_info.get('conversations', {}).keys())
                print(f"保存后: Chatflow={cf_name}, 对话列表={convs}")
                
            return True
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            return False

    def create_instance(self, api_key: str, description: str = None, base_url: str = "http://localhost/v1") -> DifyChatflow:
        """创建新的DifyChatflow实例
        
        Args:
            api_key: Dify API密钥
            description: API密钥描述
            base_url: Dify API基础URL
            
        Returns:
            DifyChatflow: 创建的实例
        """
        # 检查是否已存在相同描述的实例
        existing_instance = self.get_instance_by_name(description)
        if existing_instance:
            return existing_instance
        
        instance = DifyChatflow(
            api_key=api_key,
            description=description,
            base_url=base_url,
            config_file=self.config_file
        )
        self.instances[description] = instance
        return instance

    def get_instance(self, key: str) -> Optional[DifyChatflow]:
        """获取指定的DifyChatflow实例
        
        Args:
            key: 实例描述名称或API密钥
            
        Returns:
            Optional[DifyChatflow]: 找到的实例，如果不存在返回None
        """
        # 首先尝试通过描述名称查找
        if key in self.instances:
            return self.instances[key]
        
        # 如果不是描述名称，尝试通过API Key查找
        for instance in self.instances.values():
            if instance.api_key == key:
                return instance
        
        return None

    def get_instance_by_name(self, name: str) -> Optional[DifyChatflow]:
        """通过描述名称获取DifyChatflow实例
        
        Args:
            name: 实例的描述名称
            
        Returns:
            Optional[DifyChatflow]: 找到的实例，如果不存在返回None
        """
        return self.instances.get(name)

    def get_instance_by_api_key(self, api_key: str) -> Optional[DifyChatflow]:
        """通过API密钥获取DifyChatflow实例
        
        Args:
            api_key: Dify API密钥
            
        Returns:
            Optional[DifyChatflow]: 找到的实例，如果不存在返回None
        """
        for instance in self.instances.values():
            if instance.api_key == api_key:
                return instance
        return None

    def remove_instance(self, name: str) -> bool:
        """移除指定的DifyChatflow实例
        
        Args:
            name: 要移除的实例的描述名称
            
        Returns:
            bool: 是否成功移除
        """
        if name in self.instances:
            del self.instances[name]
            return True
        return False

    def list_instances(self) -> List[Dict]:
        """列出所有DifyChatflow实例的信息
        
        Returns:
            List[Dict]: 实例信息列表
        """
        result = []
        for description, instance in self.instances.items():
            info = instance.get_api_key_info()
            info["description"] = description
            info["api_key"] = instance.api_key
            info["base_url"] = instance.base_url
            result.append(info)
        return result

    def backup_config(self, backup_path: str = None):
        """备份配置文件
        
        Args:
            backup_path: 备份文件路径，默认为在原文件名后加上时间戳
        """
        if not backup_path:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.config_file}.{timestamp}.bak"
            
        import shutil
        shutil.copy2(self.config_file, backup_path)

    def clean_config(self):
        """清理配置文件中的无效数据"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if "chatflow" in config:
                # 只保留当前实例的配置
                valid_keys = set(self.instances.keys())
                config["chatflow"] = {
                    k: v for k, v in config["chatflow"].items()
                    if k in valid_keys
                }
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

    @classmethod
    def get_instance(cls, config_dir: str = None) -> 'DifyManager':
        """获取DifyManager的单例实例
        
        Args:
            config_dir: 配置文件目录，默认为当前目录
            
        Returns:
            DifyManager: DifyManager的单例实例
        """
        if cls._instance is None:
            cls._instance = cls(config_dir)
        return cls._instance

if __name__ == "__main__":
    # 测试代码
    # 获取DifyManager实例
    manager1 = DifyManager.get_instance()
    manager2 = DifyManager.get_instance()
    
    # 验证是否是同一个实例
    print("\n验证单例模式:")
    print(f"manager1 id: {id(manager1)}")
    print(f"manager2 id: {id(manager2)}")
    print(f"是否是同一个实例: {manager1 is manager2}")
    
    # 创建测试实例
    test_instance = manager1.create_instance(
        api_key="app-test-key",
        description="测试用API Key"
    )
    
    # 列出所有实例
    instances = manager1.list_instances()
    print("\n当前所有DifyChatflow实例:")
    for instance in instances:
        print(f"API Key: {instance['api_key']}")
        print(f"描述: {instance['description']}")
        print(f"创建时间: {instance['created_at']}")
        print(f"对话数量: {instance['conversation_count']}")
        print() 