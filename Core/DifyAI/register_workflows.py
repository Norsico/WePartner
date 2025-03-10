"""
工作流注册示例
用于批量注册不同类型和功能的工作流
"""
from .workflow_registry import WorkflowRegistry, WorkflowType, WorkflowFeature
from Core.Logger import Logger

logger = Logger()

def register_base_workflows(force_update=False):
    """
    注册基础工作流配置
    这些是系统必需的基础工作流
    
    Args:
        force_update: 是否强制更新已存在的工作流
        
    Returns:
        int: 成功注册的工作流数量
    """
    registry = WorkflowRegistry()
    
    # 基础工作流配置
    base_workflows = [
        # 基础聊天工作流 - 必需
        {
            "id": "chat",
            "name": "聊天",
            "api_key": "app-RXrYhNCVHOCRJal6eVyzJyWy",
            "type": WorkflowType.CHAT,
            "features": [WorkflowFeature.TEXT_INPUT, WorkflowFeature.STREAMING],
            "description": "用于处理普通对话的工作流"
        },
        # 文档处理工作流 - 必需
        {
            "id": "document",
            "name": "文档处理",
            "api_key": "app-V8tQlVW1Aw6R0yrFNILjfAbq",
            "type": WorkflowType.DOCUMENT,
            "features": [
                WorkflowFeature.TEXT_INPUT, 
                WorkflowFeature.FILE_UPLOAD
            ],
            "description": "用于处理文档的工作流"
        }
    ]
    
    count = registry.register_workflows(base_workflows, force_update)
    logger.success(f"已注册 {count} 个基础工作流")
    return count

def register_default_workflows(force_update=False):
    """
    注册默认的工作流配置
    包括基础工作流和扩展工作流
    
    Args:
        force_update: 是否强制更新已存在的工作流
        
    Returns:
        int: 成功注册的工作流数量
    """
    # 先注册基础工作流
    base_count = register_base_workflows(force_update)
    
    registry = WorkflowRegistry()
    
    # 扩展工作流配置
    extended_workflows = [
        # 数据分析工作流
        {
            "id": "analysis",
            "name": "数据分析",
            "api_key": "app-XXXXXXXXXXXXXXXX",  # 替换为实际的API密钥
            "type": WorkflowType.ANALYSIS,
            "features": [
                WorkflowFeature.TEXT_INPUT, 
                WorkflowFeature.FILE_UPLOAD
            ],
            "description": "用于数据分析的工作流"
        },
        # 带聊天历史的高级聊天工作流
        {
            "id": "chat_with_history",
            "name": "带历史的聊天",
            "api_key": "app-YYYYYYYYYYYYYYYY",  # 替换为实际的API密钥
            "type": WorkflowType.CHAT,
            "features": [
                WorkflowFeature.TEXT_INPUT, 
                WorkflowFeature.CHAT_HISTORY, 
                WorkflowFeature.STREAMING
            ],
            "description": "支持聊天历史的高级聊天工作流"
        },
        # 图片处理工作流
        {
            "id": "image_processing",
            "name": "图片处理",
            "api_key": "app-ZZZZZZZZZZZZZZZZ",  # 替换为实际的API密钥
            "type": WorkflowType.CUSTOM,
            "features": [
                WorkflowFeature.TEXT_INPUT, 
                WorkflowFeature.IMAGE_INPUT
            ],
            "description": "用于处理和分析图片的工作流"
        }
    ]
    
    extended_count = registry.register_workflows(extended_workflows, force_update)
    logger.success(f"已注册 {extended_count} 个扩展工作流")
    
    return base_count + extended_count


if __name__ == "__main__":
    # 直接运行此脚本可以注册默认工作流
    count = register_default_workflows(force_update=True)
    print(f"成功注册 {count} 个工作流") 