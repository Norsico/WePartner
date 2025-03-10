"""
工作流注册模块
用于批量注册和管理工作流
"""
from typing import Dict, List, Set, Optional
import json
import os
from Core.Logger import Logger

logger = Logger()

# 定义工作流类型常量
class WorkflowType:
    CHAT = "chat"  # 聊天型工作流
    DOCUMENT = "document"  # 文档处理型工作流
    ANALYSIS = "analysis"  # 数据分析型工作流
    CUSTOM = "custom"  # 自定义型工作流

# 定义工作流功能标记
class WorkflowFeature:
    TEXT_INPUT = "text_input"  # 支持文本输入
    FILE_UPLOAD = "file_upload"  # 支持文件上传
    CHAT_HISTORY = "chat_history"  # 支持聊天历史
    IMAGE_INPUT = "image_input"  # 支持图片输入
    STREAMING = "streaming"  # 支持流式输出
    FUNCTION_CALL = "function_call"  # 支持函数调用

class WorkflowRegistry:
    """
    工作流注册表
    用于注册和管理工作流配置
    """
    def __init__(self, config_file: str = None):
        """
        初始化工作流注册表
        
        Args:
            config_file: 工作流配置文件路径，默认为当前目录下的workflows.json
        """
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), 'workflows.json')
        self._workflows: Dict = {}
        self._load_workflows()
        
    def _load_workflows(self) -> None:
        """从配置文件加载工作流配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._workflows = json.load(f)
                logger.success(f"已从 {self.config_file} 加载 {len(self._workflows)} 个工作流配置")
            else:
                logger.warning(f"工作流配置文件 {self.config_file} 不存在，将创建新文件")
                self._save_workflows()
        except Exception as e:
            logger.error(f"加载工作流配置失败: {str(e)}")
            self._workflows = {}
            
    def _save_workflows(self) -> None:
        """保存工作流配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._workflows, f, ensure_ascii=False, indent=2)
            logger.success(f"已保存工作流配置到 {self.config_file}")
        except Exception as e:
            logger.error(f"保存工作流配置失败: {str(e)}")
            
    def exists(self, workflow_id: str) -> bool:
        """
        检查工作流是否已存在
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            bool: 工作流是否已存在
        """
        return workflow_id in self._workflows
            
    def register_workflow(self, 
                         workflow_id: str, 
                         name: str, 
                         api_key: str, 
                         workflow_type: str = WorkflowType.CHAT,
                         features: List[str] = None,
                         description: str = "",
                         force_update: bool = False) -> bool:
        """
        注册单个工作流
        
        Args:
            workflow_id: 工作流ID
            name: 工作流名称
            api_key: API密钥
            workflow_type: 工作流类型，默认为聊天型
            features: 工作流支持的功能列表
            description: 工作流描述
            force_update: 是否强制更新已存在的工作流
            
        Returns:
            bool: 是否成功注册（新注册或更新）
        """
        if features is None:
            features = [WorkflowFeature.TEXT_INPUT]  # 默认至少支持文本输入
            
        # 检查工作流是否已存在
        if self.exists(workflow_id) and not force_update:
            logger.info(f"工作流 '{workflow_id}' 已存在，跳过注册")
            return False
            
        self._workflows[workflow_id] = {
            "name": name,
            "api_key": api_key,
            "type": workflow_type,
            "features": features,
            "description": description
        }
        self._save_workflows()
        
        if self.exists(workflow_id) and force_update:
            logger.success(f"已更新工作流: {workflow_id}")
        else:
            logger.success(f"已注册工作流: {workflow_id}")
            
        return True
        
    def register_workflows(self, workflows: List[Dict], force_update: bool = False) -> int:
        """
        批量注册工作流
        
        Args:
            workflows: 工作流配置列表，每个配置包含id、name、api_key、type、features和description
            force_update: 是否强制更新已存在的工作流
            
        Returns:
            int: 成功注册的工作流数量
        """
        success_count = 0
        for workflow in workflows:
            result = self.register_workflow(
                workflow["id"],
                workflow["name"],
                workflow["api_key"],
                workflow.get("type", WorkflowType.CHAT),
                workflow.get("features", [WorkflowFeature.TEXT_INPUT]),
                workflow.get("description", ""),
                force_update
            )
            if result:
                success_count += 1
                
        logger.success(f"已批量注册 {success_count} 个工作流")
        return success_count
        
    def get_workflow(self, workflow_id: str) -> Dict:
        """
        获取工作流配置
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            Dict: 工作流配置
            
        Raises:
            KeyError: 如果工作流不存在
        """
        if workflow_id not in self._workflows:
            raise KeyError(f"工作流 '{workflow_id}' 不存在")
        return self._workflows[workflow_id]
        
    def get_all_workflows(self) -> Dict:
        """
        获取所有工作流配置
        
        Returns:
            Dict: 所有工作流配置
        """
        return self._workflows.copy()
        
    def get_workflows_by_type(self, workflow_type: str) -> Dict:
        """
        获取指定类型的所有工作流
        
        Args:
            workflow_type: 工作流类型
            
        Returns:
            Dict: 指定类型的工作流配置
        """
        return {k: v for k, v in self._workflows.items() if v.get("type") == workflow_type}
        
    def get_workflows_by_feature(self, feature: str) -> Dict:
        """
        获取支持指定功能的所有工作流
        
        Args:
            feature: 功能标记
            
        Returns:
            Dict: 支持指定功能的工作流配置
        """
        return {k: v for k, v in self._workflows.items() if feature in v.get("features", [])}
        
    def has_feature(self, workflow_id: str, feature: str) -> bool:
        """
        检查工作流是否支持指定功能
        
        Args:
            workflow_id: 工作流ID
            feature: 功能标记
            
        Returns:
            bool: 是否支持指定功能
        """
        try:
            workflow = self.get_workflow(workflow_id)
            return feature in workflow.get("features", [])
        except KeyError:
            return False
        
    def remove_workflow(self, workflow_id: str) -> bool:
        """
        移除工作流
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            bool: 是否成功移除
        """
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            self._save_workflows()
            logger.success(f"已移除工作流: {workflow_id}")
            return True
        logger.warning(f"工作流 '{workflow_id}' 不存在")
        return False