"""
Shared context management for agent collaboration.
Provides shared state and context synchronization across agents.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import threading


class ContextScope(Enum):
    """Scope levels for context data."""
    GLOBAL = "global"      # Shared across all agents and tasks
    TASK = "task"         # Scoped to specific task
    AGENT = "agent"       # Private to specific agent
    SESSION = "session"   # Scoped to generation session


class SharedContext:
    """
    Shared context manager for agent collaboration.
    Provides thread-safe access to shared state and context data.
    """
    
    def __init__(self):
        """Initialize shared context."""
        self.contexts: Dict[str, Dict[str, Any]] = {
            ContextScope.GLOBAL.value: {},
            ContextScope.TASK.value: {},
            ContextScope.AGENT.value: {},
            ContextScope.SESSION.value: {}
        }
        self._locks: Dict[str, threading.RLock] = {
            scope.value: threading.RLock()
            for scope in ContextScope
        }
        self.history: List[Dict[str, Any]] = []
    
    def set(
        self,
        key: str,
        value: Any,
        scope: ContextScope = ContextScope.GLOBAL,
        scope_id: Optional[str] = None
    ) -> None:
        """
        Set a value in the shared context.
        
        Args:
            key: Context key
            value: Value to store
            scope: Context scope
            scope_id: Optional ID for task/agent scoped data
        """
        scope_key = self._get_scope_key(scope, scope_id)
        
        with self._locks[scope.value]:
            if scope_key not in self.contexts[scope.value]:
                self.contexts[scope.value][scope_key] = {}
            
            self.contexts[scope.value][scope_key][key] = value
            
            # Record change in history
            self.history.append({
                "action": "set",
                "scope": scope.value,
                "scope_id": scope_id,
                "key": key,
                "timestamp": datetime.now().isoformat()
            })
    
    def get(
        self,
        key: str,
        scope: ContextScope = ContextScope.GLOBAL,
        scope_id: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """
        Get a value from the shared context.
        
        Args:
            key: Context key
            scope: Context scope
            scope_id: Optional ID for task/agent scoped data
            default: Default value if not found
            
        Returns:
            Context value or default
        """
        scope_key = self._get_scope_key(scope, scope_id)
        
        with self._locks[scope.value]:
            scope_data = self.contexts[scope.value].get(scope_key, {})
            return scope_data.get(key, default)
    
    def update(
        self,
        data: Dict[str, Any],
        scope: ContextScope = ContextScope.GLOBAL,
        scope_id: Optional[str] = None
    ) -> None:
        """
        Update multiple values in context.
        
        Args:
            data: Dictionary of key-value pairs
            scope: Context scope
            scope_id: Optional ID for task/agent scoped data
        """
        for key, value in data.items():
            self.set(key, value, scope, scope_id)
    
    def delete(
        self,
        key: str,
        scope: ContextScope = ContextScope.GLOBAL,
        scope_id: Optional[str] = None
    ) -> bool:
        """
        Delete a key from context.
        
        Args:
            key: Context key
            scope: Context scope
            scope_id: Optional ID for task/agent scoped data
            
        Returns:
            True if deleted, False if not found
        """
        scope_key = self._get_scope_key(scope, scope_id)
        
        with self._locks[scope.value]:
            scope_data = self.contexts[scope.value].get(scope_key, {})
            if key in scope_data:
                del scope_data[key]
                return True
            return False
    
    def get_all(
        self,
        scope: ContextScope = ContextScope.GLOBAL,
        scope_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all context data for a scope.
        
        Args:
            scope: Context scope
            scope_id: Optional ID for task/agent scoped data
            
        Returns:
            Dictionary of context data
        """
        scope_key = self._get_scope_key(scope, scope_id)
        
        with self._locks[scope.value]:
            return self.contexts[scope.value].get(scope_key, {}).copy()
    
    def clear(
        self,
        scope: Optional[ContextScope] = None,
        scope_id: Optional[str] = None
    ) -> None:
        """
        Clear context data.
        
        Args:
            scope: Optional scope to clear (clears all if None)
            scope_id: Optional ID for task/agent scoped data
        """
        if scope is None:
            # Clear all scopes
            for s in ContextScope:
                with self._locks[s.value]:
                    self.contexts[s.value].clear()
        else:
            scope_key = self._get_scope_key(scope, scope_id)
            with self._locks[scope.value]:
                if scope_key in self.contexts[scope.value]:
                    self.contexts[scope.value][scope_key].clear()
    
    def _get_scope_key(
        self,
        scope: ContextScope,
        scope_id: Optional[str]
    ) -> str:
        """
        Get internal scope key.
        
        Args:
            scope: Context scope
            scope_id: Optional scope ID
            
        Returns:
            Scope key string
        """
        if scope == ContextScope.GLOBAL or scope == ContextScope.SESSION:
            return "default"
        return scope_id or "default"
    
    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get context change history.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of history entries
        """
        return self.history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get context statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "total_scopes": len(self.contexts),
            "history_size": len(self.history),
            "scope_stats": {}
        }
        
        for scope, scope_data in self.contexts.items():
            total_keys = sum(len(data) for data in scope_data.values())
            stats["scope_stats"][scope] = {
                "namespaces": len(scope_data),
                "total_keys": total_keys
            }
        
        return stats
