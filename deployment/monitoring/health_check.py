#!/usr/bin/env python3
"""
Health check and monitoring service for Accelerapp.
Provides system status, metrics, and health endpoints.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any
import urllib.request
import urllib.error


def check_python_environment() -> Dict[str, Any]:
    """Check Python environment status."""
    try:
        import accelerapp
        return {
            "status": "healthy",
            "version": accelerapp.__version__ if hasattr(accelerapp, '__version__') else "0.1.0",
            "python_version": sys.version
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def check_llm_service(ollama_host: str = "http://localhost:11434") -> Dict[str, Any]:
    """Check LLM service availability."""
    try:
        url = f"{ollama_host}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            return {
                "status": "healthy",
                "models_available": len(data.get('models', [])),
                "host": ollama_host
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "host": ollama_host
        }


def check_disk_space() -> Dict[str, Any]:
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        return {
            "status": "healthy" if free > 1024**3 else "warning",  # Warn if < 1GB
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round((used / total) * 100, 1)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def check_memory() -> Dict[str, Any]:
    """Check memory usage."""
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = {}
            for line in f:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = int(parts[1].strip().split()[0])
                    meminfo[key] = value
        
        total = meminfo.get('MemTotal', 0) / 1024  # MB
        available = meminfo.get('MemAvailable', 0) / 1024  # MB
        used = total - available
        
        return {
            "status": "healthy" if available > 512 else "warning",  # Warn if < 512MB
            "total_mb": round(total, 2),
            "used_mb": round(used, 2),
            "available_mb": round(available, 2),
            "percent_used": round((used / total) * 100, 1)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def get_system_health() -> Dict[str, Any]:
    """Get overall system health status."""
    checks = {
        "timestamp": time.time(),
        "python_environment": check_python_environment(),
        "llm_service": check_llm_service(),
        "disk_space": check_disk_space(),
        "memory": check_memory()
    }
    
    # Determine overall status
    statuses = [check["status"] for check in checks.values() if isinstance(check, dict) and "status" in check]
    if any(s == "unhealthy" or s == "error" for s in statuses):
        overall_status = "unhealthy"
    elif any(s == "warning" for s in statuses):
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    return {
        "overall_status": overall_status,
        "checks": checks
    }


def main():
    """Main health check routine."""
    health = get_system_health()
    
    # Output as JSON
    print(json.dumps(health, indent=2))
    
    # Exit with appropriate code
    if health["overall_status"] == "unhealthy":
        sys.exit(1)
    elif health["overall_status"] == "degraded":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
