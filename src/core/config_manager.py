#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块

提供应用程序配置的加载、保存和管理功能
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import get_logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.logger = get_logger(__name__)
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        self._config = {}
        self._load_config()
    
    def _get_default_config_path(self) -> Path:
        """获取默认配置文件路径"""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        return config_dir / "app_config.json"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app": {
                "name": "Flow Farm",
                "version": "1.0.0",
                "debug": False,
                "log_level": "INFO"
            },
            "adb": {
                "path": "adb",
                "timeout": 30,
                "port": 5037
            },
            "device": {
                "max_devices": 10,
                "connection_timeout": 30,
                "operation_timeout": 30,
                "retry_count": 3
            },
            "gui": {
                "theme": "system",
                "window_width": 1200,
                "window_height": 800,
                "font_family": "微软雅黑",
                "font_size": 12
            },
            "security": {
                "session_timeout": 30,
                "auto_logout": True,
                "encryption_enabled": True
            },
            "platforms": {
                "xiaohongshu": {
                    "app_package": "com.xingin.xhs",
                    "main_activity": "com.xingin.xhs.index.v2.IndexActivityV2",
                    "max_follows_per_session": 50,
                    "operation_delay_min": 3,
                    "operation_delay_max": 8
                },
                "douyin": {
                    "app_package": "com.ss.android.ugc.aweme",
                    "main_activity": "com.ss.android.ugc.aweme.splash.SplashActivity",
                    "max_follows_per_session": 30,
                    "operation_delay_min": 2,
                    "operation_delay_max": 6
                }
            },
            "database": {
                "path": "data/flow_farm.db",
                "pool_size": 5,
                "timeout": 30
            },
            "logging": {
                "dir": "logs",
                "max_size": "10MB",
                "backup_count": 5,
                "retention_days": 30
            }
        }
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                self.logger.info(f"配置文件加载成功: {self.config_path}")
            else:
                self.logger.info("配置文件不存在，使用默认配置")
                self._config = self._get_default_config()
                self.save_config()
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            self.logger.info("使用默认配置")
            self._config = self._get_default_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            self.logger.info(f"配置文件保存成功: {self.config_path}")
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            raise
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self._config.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键，支持 "app.name" 格式
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键，支持 "app.name" 格式
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 导航到最后一个键的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        self.logger.debug(f"配置已更新: {key} = {value}")
    
    def update(self, new_config: Dict[str, Any]):
        """
        更新配置
        
        Args:
            new_config: 新配置字典
        """
        def deep_update(base: dict, update: dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value
        
        deep_update(self._config, new_config)
        self.logger.info("配置已更新")
    
    def reset_to_default(self):
        """重置为默认配置"""
        self._config = self._get_default_config()
        self.save_config()
        self.logger.info("配置已重置为默认值")
    
    def validate_config(self) -> bool:
        """
        验证配置有效性
        
        Returns:
            bool: 配置是否有效
        """
        try:
            # 检查必需的配置项
            required_keys = [
                'app.name',
                'app.version',
                'adb.path',
                'device.max_devices'
            ]
            
            for key in required_keys:
                if self.get(key) is None:
                    self.logger.error(f"缺少必需的配置项: {key}")
                    return False
            
            # 检查数值范围
            max_devices = self.get('device.max_devices', 0)
            if not isinstance(max_devices, int) or max_devices <= 0:
                self.logger.error("device.max_devices 必须是大于0的整数")
                return False
            
            # 检查路径
            adb_path = self.get('adb.path')
            if adb_path and adb_path != 'adb':
                if not Path(adb_path).exists():
                    self.logger.warning(f"ADB路径不存在: {adb_path}")
            
            self.logger.info("配置验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
    
    def get_adb_path(self) -> str:
        """获取ADB路径"""
        adb_path = self.get('adb.path', 'adb')
        
        # 如果是相对路径，尝试在常见位置查找
        if adb_path == 'adb':
            # Windows常见ADB位置
            if os.name == 'nt':
                common_paths = [
                    r"C:\Program Files\Android\android-sdk\platform-tools\adb.exe",
                    r"C:\Android\sdk\platform-tools\adb.exe",
                    r"D:\Android\sdk\platform-tools\adb.exe",
                    r"D:\leidian\LDPlayer9\adb.exe"
                ]
                
                for path in common_paths:
                    if Path(path).exists():
                        self.logger.info(f"找到ADB: {path}")
                        return path
        
        return adb_path
    
    def export_config(self, export_path: str):
        """
        导出配置到指定路径
        
        Args:
            export_path: 导出路径
        """
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"配置导出成功: {export_file}")
            
        except Exception as e:
            self.logger.error(f"配置导出失败: {e}")
            raise
    
    def import_config(self, import_path: str):
        """
        从指定路径导入配置
        
        Args:
            import_path: 导入路径
        """
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                raise FileNotFoundError(f"配置文件不存在: {import_file}")
            
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            self.update(imported_config)
            self.save_config()
            
            self.logger.info(f"配置导入成功: {import_file}")
            
        except Exception as e:
            self.logger.error(f"配置导入失败: {e}")
            raise
