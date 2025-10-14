"""
Configuration migration utilities for version compatibility.
"""

from typing import Any, Dict, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ConfigMigration:
    """
    Handles configuration migrations between versions.
    
    Features:
    - Version-based migrations
    - Automatic migration application
    - Migration validation
    """
    
    def __init__(self):
        """Initialize configuration migration manager."""
        self._migrations: Dict[str, Callable] = {}
        self._migration_order: List[str] = []
    
    def register_migration(
        self,
        from_version: str,
        to_version: str,
        migration_func: Callable[[Dict], Dict]
    ) -> None:
        """
        Register a migration function.
        
        Args:
            from_version: Source version
            to_version: Target version
            migration_func: Migration function
        """
        key = f"{from_version}->{to_version}"
        self._migrations[key] = migration_func
        
        if key not in self._migration_order:
            self._migration_order.append(key)
        
        logger.info(f"Registered migration: {key}")
    
    def migrate(
        self,
        config: Dict[str, Any],
        from_version: str,
        to_version: str
    ) -> Dict[str, Any]:
        """
        Migrate configuration from one version to another.
        
        Args:
            config: Configuration to migrate
            from_version: Current version
            to_version: Target version
            
        Returns:
            Migrated configuration
        """
        current_version = from_version
        migrated_config = config.copy()
        
        # Find migration path
        while current_version != to_version:
            migration_key = self._find_migration(current_version, to_version)
            
            if not migration_key:
                raise ValueError(
                    f"No migration path found from {current_version} to {to_version}"
                )
            
            # Apply migration
            migration_func = self._migrations[migration_key]
            migrated_config = migration_func(migrated_config)
            
            # Update version in config
            migrated_config["version"] = migration_key.split("->")[1]
            current_version = migrated_config["version"]
            
            logger.info(f"Applied migration: {migration_key}")
        
        return migrated_config
    
    def _find_migration(self, from_version: str, to_version: str) -> Optional[str]:
        """Find a direct migration or next step in migration path."""
        # Try direct migration first
        direct_key = f"{from_version}->{to_version}"
        if direct_key in self._migrations:
            return direct_key
        
        # Find next step in migration chain
        for key in self._migration_order:
            if key.startswith(f"{from_version}->"):
                return key
        
        return None
    
    def get_available_migrations(self) -> List[str]:
        """
        Get list of available migrations.
        
        Returns:
            List of migration keys
        """
        return self._migration_order.copy()


# Example migrations
def migrate_1_0_to_2_0(config: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate configuration from v1.0 to v2.0."""
    migrated = config.copy()
    
    # Add new v2.0 fields with defaults
    if "security" not in migrated:
        migrated["security"] = {
            "enable_encryption": True,
            "enable_rbac": False,
        }
    
    if "events" not in migrated:
        migrated["events"] = {
            "enabled": True,
            "event_store": "memory",
        }
    
    # Rename old fields if needed
    if "cache_enabled" in migrated.get("performance", {}):
        migrated["performance"]["enable_caching"] = migrated["performance"].pop("cache_enabled")
    
    return migrated
