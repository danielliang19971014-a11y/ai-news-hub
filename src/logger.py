import logging
import logging.handlers
from config.settings import settings

def setup_logger(name: str = __name__):
    """设置日志系统"""
    import os as _os
    _log_dir = _os.path.dirname(settings.log_file)
    if _log_dir:
        _os.makedirs(_log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)

    # 创建文件处理器（日志文件每天轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        settings.log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger("AI-News-Hub")
