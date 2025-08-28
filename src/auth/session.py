#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 会话管理模块 - 负责用户会话的创建、维护和销毁，包括用户认证状态管理

import time
import uuid
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

from utils.logger import get_logger


class Session:
    """用户会话类"""
    
    def __init__(self, user_id: str, username: str, role: str, permissions: list = None):
        """
        初始化会话
        
        Args:
            user_id: 用户ID
            username: 用户名
            role: 用户角色
            permissions: 用户权限列表
        """
        self.session_id = str(uuid.uuid4())
        self.user_id = user_id
        self.username = username
        self.role = role
        self.permissions = permissions or []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_active = True
        
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = datetime.now()
        
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """
        检查会话是否过期
        
        Args:
            timeout_minutes: 超时时间（分钟）
            
        Returns:
            bool: 是否过期
        """
        if not self.is_active:
            return True
            
        timeout_delta = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity > timeout_delta
        
    def has_permission(self, permission: str) -> bool:
        """
        检查是否有指定权限
        
        Args:
            permission: 权限名称
            
        Returns:
            bool: 是否有权限
        """
        return permission in self.permissions
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'is_active': self.is_active
        }


class SessionManager:
    """会话管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化会话管理器
        
        Args:
            config: 配置信息
        """
        self.logger = get_logger(__name__)
        self.config = config or {}
        self.sessions: Dict[str, Session] = {}
        self.current_session: Optional[Session] = None
        
        # 会话配置
        self.session_timeout = self.config.get('auth.session_timeout', 30)  # 分钟
        self.max_sessions = self.config.get('auth.max_sessions', 100)
        
        self.logger.info("会话管理器初始化完成")
        
    def create_session(self, user_id: str, username: str, role: str, permissions: list = None) -> Session:
        """
        创建新会话
        
        Args:
            user_id: 用户ID
            username: 用户名
            role: 用户角色
            permissions: 用户权限列表
            
        Returns:
            Session: 创建的会话对象
        """
        # 清理过期会话
        self._cleanup_expired_sessions()
        
        # 检查会话数量限制
        if len(self.sessions) >= self.max_sessions:
            self.logger.warning(f"会话数量达到上限 {self.max_sessions}")
            # 清理最旧的会话
            self._cleanup_oldest_sessions()
        
        # 创建新会话
        session = Session(user_id, username, role, permissions)
        self.sessions[session.session_id] = session
        self.current_session = session
        
        self.logger.info(f"为用户 {username} 创建会话: {session.session_id}")
        return session
        
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        获取会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            Session: 会话对象，不存在或过期返回None
        """
        session = self.sessions.get(session_id)
        if session and not session.is_expired(self.session_timeout):
            session.update_activity()
            return session
        elif session:
            # 会话过期，移除
            self.destroy_session(session_id)
        return None
        
    def get_current_session(self) -> Optional[Session]:
        """
        获取当前会话
        
        Returns:
            Session: 当前活动会话
        """
        if self.current_session and not self.current_session.is_expired(self.session_timeout):
            self.current_session.update_activity()
            return self.current_session
        elif self.current_session:
            # 当前会话过期
            self.logger.info("当前会话已过期")
            self.current_session = None
        return None
        
    def destroy_session(self, session_id: str) -> bool:
        """
        销毁会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否成功销毁
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.is_active = False
            del self.sessions[session_id]
            
            # 如果是当前会话，清空当前会话
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
                
            self.logger.info(f"销毁会话: {session_id}")
            return True
        return False
        
    def logout_current_user(self) -> bool:
        """
        登出当前用户
        
        Returns:
            bool: 是否成功登出
        """
        if self.current_session:
            session_id = self.current_session.session_id
            username = self.current_session.username
            success = self.destroy_session(session_id)
            if success:
                self.logger.info(f"用户 {username} 登出")
            return success
        return False
        
    def is_authenticated(self) -> bool:
        """
        检查是否已认证
        
        Returns:
            bool: 是否已认证
        """
        return self.get_current_session() is not None
        
    def has_permission(self, permission: str) -> bool:
        """
        检查当前用户是否有指定权限
        
        Args:
            permission: 权限名称
            
        Returns:
            bool: 是否有权限
        """
        session = self.get_current_session()
        return session.has_permission(permission) if session else False
        
    def has_role(self, role: str) -> bool:
        """
        检查当前用户是否有指定角色
        
        Args:
            role: 角色名称
            
        Returns:
            bool: 是否有角色
        """
        session = self.get_current_session()
        return session.role == role if session else False
        
    def get_current_user_info(self) -> Dict[str, Any]:
        """
        获取当前用户信息
        
        Returns:
            Dict: 用户信息，未认证返回空字典
        """
        session = self.get_current_session()
        if session:
            return {
                'user_id': session.user_id,
                'username': session.username,
                'role': session.role,
                'permissions': session.permissions,
                'session_id': session.session_id
            }
        return {}
        
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有活动会话（管理员功能）
        
        Returns:
            Dict: 所有会话信息
        """
        # 清理过期会话
        self._cleanup_expired_sessions()
        
        return {
            session_id: session.to_dict() 
            for session_id, session in self.sessions.items()
        }
        
    def _cleanup_expired_sessions(self):
        """清理过期会话"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired(self.session_timeout)
        ]
        
        for session_id in expired_sessions:
            self.destroy_session(session_id)
            
        if expired_sessions:
            self.logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
            
    def _cleanup_oldest_sessions(self, count: int = 10):
        """
        清理最旧的会话
        
        Args:
            count: 要清理的会话数量
        """
        if len(self.sessions) <= count:
            return
            
        # 按创建时间排序，获取最旧的会话
        sorted_sessions = sorted(
            self.sessions.items(),
            key=lambda x: x[1].created_at
        )
        
        for i in range(count):
            if i < len(sorted_sessions):
                session_id = sorted_sessions[i][0]
                self.destroy_session(session_id)
                
        self.logger.info(f"清理了 {count} 个最旧的会话")
        
    def update_session_permissions(self, session_id: str, permissions: list) -> bool:
        """
        更新会话权限
        
        Args:
            session_id: 会话ID
            permissions: 新的权限列表
            
        Returns:
            bool: 是否成功更新
        """
        session = self.get_session(session_id)
        if session:
            session.permissions = permissions
            self.logger.info(f"更新会话 {session_id} 的权限")
            return True
        return False
        
    def get_session_stats(self) -> Dict[str, Any]:
        """
        获取会话统计信息
        
        Returns:
            Dict: 统计信息
        """
        self._cleanup_expired_sessions()
        
        total_sessions = len(self.sessions)
        active_users = len({session.user_id for session in self.sessions.values()})
        
        # 按角色统计
        role_stats = {}
        for session in self.sessions.values():
            role = session.role
            role_stats[role] = role_stats.get(role, 0) + 1
            
        return {
            'total_sessions': total_sessions,
            'active_users': active_users,
            'role_distribution': role_stats,
            'session_timeout': self.session_timeout,
            'max_sessions': self.max_sessions
        }
