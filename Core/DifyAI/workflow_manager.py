from typing import Dict, List, Optional
from .dify_bot import Dify
from .workflow_registry import WorkflowRegistry, WorkflowType, WorkflowFeature
from .register_workflows import register_base_workflows
from Core.Logger import Logger

logger = Logger()

class WorkflowManager:
    """
    工作流管理器，用于管理多个Dify工作流实例
    使用单例模式确保全局只有一个实例
    """
    # 单例实例
    _instance = None
    # 是否已经初始化
    _initialized = False
    # 是否已经注册了基础工作流
    _base_workflows_registered = False
    # 是否已经加载了工作流
    _workflows_loaded = False
    
    def __new__(cls, base_url: str = None):
        """
        创建或返回单例实例
        
        Args:
            base_url: Dify服务的基础URL，只在第一次创建实例时需要
        """
        if cls._instance is None:
            if base_url is None:
                raise ValueError("首次创建WorkflowManager实例时必须提供base_url")
            cls._instance = super(WorkflowManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, base_url: str = None):
        """
        初始化工作流管理器
        
        Args:
            base_url: Dify服务的基础URL，只在第一次初始化时需要
        """
        # 避免重复初始化
        if self._initialized:
            return
            
        if base_url is None:
            raise ValueError("首次创建WorkflowManager实例时必须提供base_url")
            
        self.base_url = base_url
        self._workflows: Dict[str, Dify] = {}  # 工作流名称 -> Dify实例的映射
        self.registry = WorkflowRegistry()
        
        # 初始化注册表并注册基础工作流
        self._ensure_base_workflows()
        
        # 加载所有工作流
        self._load_workflows()
        
        # 标记为已初始化
        self._initialized = True
        
    def _ensure_base_workflows(self) -> None:
        """确保基础工作流已注册，但只注册一次"""
        if not WorkflowManager._base_workflows_registered:
            register_base_workflows()
            WorkflowManager._base_workflows_registered = True
            logger.info("已完成基础工作流注册")
        
    def _load_workflows(self) -> None:
        """从注册表加载所有工作流，但只加载一次"""
        if not WorkflowManager._workflows_loaded:
            workflows = self.registry.get_all_workflows()
            for workflow_id, workflow_config in workflows.items():
                if workflow_id not in self._workflows:  # 只添加不存在的工作流
                    self._workflows[workflow_id] = Dify(base_url=self.base_url, api_key=workflow_config['api_key'])
                    logger.debug(f"已加载工作流 '{workflow_id}'")  # 改用debug级别的日志
            WorkflowManager._workflows_loaded = True
            logger.info("已完成所有工作流加载")
        
    def add_workflow(self, name: str, api_key: str) -> None:
        """
        添加一个新的工作流
        
        Args:
            name: 工作流名称
            api_key: 工作流的API密钥
        """
        if name not in self._workflows:  # 只在工作流不存在时添加
            self._workflows[name] = Dify(base_url=self.base_url, api_key=api_key)
            logger.debug(f"已添加新工作流 '{name}'")  # 改用debug级别的日志
        
    @classmethod
    def get_instance(cls, base_url: str = None) -> 'WorkflowManager':
        """
        获取WorkflowManager实例
        
        Args:
            base_url: Dify服务的基础URL，只在第一次创建实例时需要
            
        Returns:
            WorkflowManager: 工作流管理器实例
        """
        return cls(base_url)
        
    def remove_workflow(self, name: str) -> bool:
        """
        移除指定的工作流
        
        Args:
            name: 工作流名称
            
        Returns:
            bool: 是否成功移除
        """
        if name in self._workflows:
            del self._workflows[name]
            logger.success(f"成功移除工作流 '{name}'")
            return True
        logger.warning(f"工作流 '{name}' 不存在")
        return False
        
    def get_workflow(self, name: str) -> Dify:
        """
        获取指定名称的工作流实例
        
        Args:
            name: 工作流名称
            
        Returns:
            Dify: 工作流实例
            
        Raises:
            KeyError: 如果工作流不存在
        """
        if name not in self._workflows:
            raise KeyError(f"工作流 '{name}' 不存在")
        return self._workflows[name]
        
    def get_workflow_by_type(self, workflow_type: str, default_id: str = None) -> Optional[Dify]:
        """
        获取指定类型的工作流实例
        
        Args:
            workflow_type: 工作流类型
            default_id: 如果找不到指定类型的工作流，则使用此ID
            
        Returns:
            Optional[Dify]: 工作流实例，如果找不到则返回None
        """
        workflows = self.registry.get_workflows_by_type(workflow_type)
        if not workflows and default_id:
            try:
                return self.get_workflow(default_id)
            except KeyError:
                return None
                
        # 如果有多个符合条件的工作流，返回第一个
        if workflows:
            workflow_id = next(iter(workflows.keys()))
            return self.get_workflow(workflow_id)
            
        return None
        
    def get_workflow_by_feature(self, feature: str, default_id: str = None) -> Optional[Dify]:
        """
        获取支持指定功能的工作流实例
        
        Args:
            feature: 功能标记
            default_id: 如果找不到支持指定功能的工作流，则使用此ID
            
        Returns:
            Optional[Dify]: 工作流实例，如果找不到则返回None
        """
        workflows = self.registry.get_workflows_by_feature(feature)
        if not workflows and default_id:
            try:
                return self.get_workflow(default_id)
            except KeyError:
                return None
                
        # 如果有多个符合条件的工作流，返回第一个
        if workflows:
            workflow_id = next(iter(workflows.keys()))
            return self.get_workflow(workflow_id)
            
        return None
        
    def get_workflow_for_task(self, task_type: str, required_features: List[str] = None, default_id: str = None) -> Optional[Dify]:
        """
        获取适合特定任务的工作流实例
        
        Args:
            task_type: 任务类型，对应工作流类型
            required_features: 任务所需的功能列表
            default_id: 如果找不到合适的工作流，则使用此ID
            
        Returns:
            Optional[Dify]: 工作流实例，如果找不到则返回None
        """
        if required_features is None:
            required_features = []
            
        # 先按类型筛选
        workflows = self.registry.get_workflows_by_type(task_type)
        
        # 再按功能筛选
        if required_features:
            filtered_workflows = {}
            for workflow_id, workflow in workflows.items():
                if all(feature in workflow.get("features", []) for feature in required_features):
                    filtered_workflows[workflow_id] = workflow
            workflows = filtered_workflows
            
        # 如果没有找到合适的工作流，使用默认工作流
        if not workflows and default_id:
            try:
                return self.get_workflow(default_id)
            except KeyError:
                return None
                
        # 如果有多个符合条件的工作流，返回第一个
        if workflows:
            workflow_id = next(iter(workflows.keys()))
            return self.get_workflow(workflow_id)
            
        return None
        
    def list_workflows(self) -> list[str]:
        """
        获取所有工作流名称列表
        
        Returns:
            list[str]: 工作流名称列表
        """
        return list(self._workflows.keys())
