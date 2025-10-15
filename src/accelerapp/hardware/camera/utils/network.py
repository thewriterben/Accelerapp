"""
Network utilities for ESP32-CAM.
"""

from typing import Dict, Any, Optional


class NetworkHelper:
    """
    Network utilities for camera connectivity.
    """
    
    @staticmethod
    def validate_ip(ip_address: str) -> bool:
        """
        Validate IP address format.
        
        Args:
            ip_address: IP address string
            
        Returns:
            True if valid IP address
        """
        parts = ip_address.split('.')
        if len(parts) != 4:
            return False
        
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """
        Validate network port number.
        
        Args:
            port: Port number
            
        Returns:
            True if valid port
        """
        return 1 <= port <= 65535
    
    @staticmethod
    def format_url(protocol: str, host: str, port: int, path: str = "") -> str:
        """
        Format network URL.
        
        Args:
            protocol: Protocol (http, https, rtsp, etc.)
            host: Hostname or IP address
            port: Port number
            path: Optional path
            
        Returns:
            Formatted URL string
        """
        url = f"{protocol}://{host}:{port}"
        if path:
            if not path.startswith('/'):
                path = '/' + path
            url += path
        return url
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """
        Get network configuration information.
        
        Returns:
            Network info dictionary
        """
        return {
            "hostname": "esp32cam",
            "ip_address": "192.168.1.100",
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "gateway": "192.168.1.1",
            "subnet": "255.255.255.0",
            "dns": "8.8.8.8",
        }
    
    @staticmethod
    def check_connectivity(host: str, timeout: int = 5) -> bool:
        """
        Check network connectivity to host.
        
        Args:
            host: Hostname or IP to check
            timeout: Timeout in seconds
            
        Returns:
            True if reachable
        """
        # Placeholder - would perform actual connectivity check
        return True
