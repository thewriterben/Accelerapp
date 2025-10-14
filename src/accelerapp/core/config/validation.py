"""
Configuration validation utilities.
"""

from typing import Any, Dict, List, Optional
from pydantic import ValidationError


class ConfigValidator:
    """
    Validates configuration values and structure.
    
    Features:
    - Schema validation
    - Custom validation rules
    - Validation error reporting
    """
    
    def __init__(self):
        """Initialize configuration validator."""
        self._custom_validators: Dict[str, callable] = {}
    
    def register_validator(self, key: str, validator: callable) -> None:
        """
        Register a custom validator for a configuration key.
        
        Args:
            key: Configuration key path
            validator: Validation function that returns True if valid
        """
        self._custom_validators[key] = validator
    
    def validate_value(self, key: str, value: Any) -> bool:
        """
        Validate a specific configuration value.
        
        Args:
            key: Configuration key
            value: Value to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if key in self._custom_validators:
            validator = self._custom_validators[key]
            if not validator(value):
                raise ValueError(f"Validation failed for key '{key}' with value '{value}'")
        
        return True
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate entire configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        for key, validator in self._custom_validators.items():
            try:
                value = self._get_nested_value(config, key)
                if value is not None and not validator(value):
                    errors.append(f"Validation failed for '{key}'")
            except KeyError:
                pass  # Key doesn't exist, skip
            except Exception as e:
                errors.append(f"Error validating '{key}': {e}")
        
        return errors
    
    def _get_nested_value(self, config: Dict[str, Any], key: str) -> Any:
        """Get a nested configuration value."""
        keys = key.split(".")
        value = config
        
        for k in keys:
            if isinstance(value, dict):
                value = value[k]
            else:
                raise KeyError(f"Key '{key}' not found")
        
        return value
