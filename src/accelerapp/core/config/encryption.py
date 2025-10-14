"""
Configuration encryption for sensitive values.
"""

import base64
from typing import Any, Dict, Optional
import hashlib


class ConfigEncryption:
    """
    Handles encryption/decryption of sensitive configuration values.
    
    Note: This is a basic implementation. For production use, consider
    using proper encryption libraries like cryptography.
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize configuration encryption.
        
        Args:
            secret_key: Secret key for encryption
        """
        self._secret_key = secret_key or "default-key-change-in-production"
    
    def encrypt(self, value: str) -> str:
        """
        Encrypt a configuration value.
        
        Args:
            value: Plain text value
            
        Returns:
            Encrypted value (base64 encoded)
        """
        # Simple XOR encryption (NOT for production use!)
        key_hash = hashlib.sha256(self._secret_key.encode()).digest()
        encrypted = bytearray()
        
        for i, char in enumerate(value.encode()):
            encrypted.append(char ^ key_hash[i % len(key_hash)])
        
        return base64.b64encode(bytes(encrypted)).decode()
    
    def decrypt(self, encrypted_value: str) -> str:
        """
        Decrypt a configuration value.
        
        Args:
            encrypted_value: Encrypted value (base64 encoded)
            
        Returns:
            Decrypted plain text value
        """
        # Simple XOR decryption
        key_hash = hashlib.sha256(self._secret_key.encode()).digest()
        encrypted_bytes = base64.b64decode(encrypted_value.encode())
        decrypted = bytearray()
        
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key_hash[i % len(key_hash)])
        
        return bytes(decrypted).decode()
    
    def encrypt_config_values(
        self,
        config: Dict[str, Any],
        keys_to_encrypt: list
    ) -> Dict[str, Any]:
        """
        Encrypt specific configuration values.
        
        Args:
            config: Configuration dictionary
            keys_to_encrypt: List of keys to encrypt
            
        Returns:
            Configuration with encrypted values
        """
        encrypted_config = config.copy()
        
        for key in keys_to_encrypt:
            value = self._get_nested_value(config, key)
            if value and isinstance(value, str):
                encrypted_value = self.encrypt(value)
                self._set_nested_value(encrypted_config, key, f"encrypted:{encrypted_value}")
        
        return encrypted_config
    
    def decrypt_config_values(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt configuration values marked with 'encrypted:' prefix.
        
        Args:
            config: Configuration dictionary with encrypted values
            
        Returns:
            Configuration with decrypted values
        """
        decrypted_config = config.copy()
        self._decrypt_recursive(decrypted_config)
        return decrypted_config
    
    def _decrypt_recursive(self, config: Any) -> None:
        """Recursively decrypt configuration values."""
        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, str) and value.startswith("encrypted:"):
                    encrypted_value = value[10:]  # Remove 'encrypted:' prefix
                    config[key] = self.decrypt(encrypted_value)
                elif isinstance(value, (dict, list)):
                    self._decrypt_recursive(value)
        elif isinstance(config, list):
            for i, item in enumerate(config):
                if isinstance(item, str) and item.startswith("encrypted:"):
                    encrypted_value = item[10:]
                    config[i] = self.decrypt(encrypted_value)
                elif isinstance(item, (dict, list)):
                    self._decrypt_recursive(item)
    
    def _get_nested_value(self, config: Dict[str, Any], key: str) -> Any:
        """Get a nested configuration value."""
        keys = key.split(".")
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], key: str, value: Any) -> None:
        """Set a nested configuration value."""
        keys = key.split(".")
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
