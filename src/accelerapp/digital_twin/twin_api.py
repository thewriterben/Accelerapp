"""
REST API for digital twin management.
"""

from typing import Dict, Any, Optional, Callable
from enum import Enum


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class DigitalTwinAPI:
    """
    REST API handler for digital twin operations.
    Provides endpoints for twin management and monitoring.
    """
    
    def __init__(self, twin_manager, visualizer, blockchain_loggers: Optional[Dict[str, Any]] = None):
        """
        Initialize API handler.
        
        Args:
            twin_manager: DigitalTwinManager instance
            visualizer: TwinVisualizer instance
            blockchain_loggers: Optional dict of BlockchainLogger instances by device_id
        """
        self.twin_manager = twin_manager
        self.visualizer = visualizer
        self.blockchain_loggers = blockchain_loggers or {}
        self.routes: Dict[str, Dict[HTTPMethod, Callable]] = {}
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        # Twin management
        self.register_route("/twins", HTTPMethod.GET, self._list_twins)
        self.register_route("/twins", HTTPMethod.POST, self._create_twin)
        self.register_route("/twins/{twin_id}", HTTPMethod.GET, self._get_twin)
        self.register_route("/twins/{twin_id}", HTTPMethod.DELETE, self._delete_twin)
        self.register_route("/twins/{twin_id}/state", HTTPMethod.GET, self._get_twin_state)
        self.register_route("/twins/{twin_id}/state", HTTPMethod.PUT, self._update_twin_state)
        
        # Visualization
        self.register_route("/twins/{twin_id}/dashboard", HTTPMethod.GET, self._get_dashboard)
        self.register_route("/dashboard/overview", HTTPMethod.GET, self._get_overview)
        self.register_route("/twins/{twin_id}/timeline", HTTPMethod.GET, self._get_timeline)
        
        # Blockchain
        self.register_route("/twins/{twin_id}/blockchain", HTTPMethod.GET, self._get_blockchain)
        self.register_route("/twins/{twin_id}/blockchain/verify", HTTPMethod.GET, self._verify_blockchain)
        
        # Health
        self.register_route("/health", HTTPMethod.GET, self._health_check)
    
    def register_route(self, path: str, method: HTTPMethod, handler: Callable) -> None:
        """
        Register an API route.
        
        Args:
            path: URL path
            method: HTTP method
            handler: Handler function
        """
        if path not in self.routes:
            self.routes[path] = {}
        self.routes[path][method] = handler
    
    def handle_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        Handle an API request.
        
        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional request parameters
            
        Returns:
            Response dictionary
        """
        try:
            http_method = HTTPMethod(method)
        except ValueError:
            return {"error": "Invalid HTTP method", "status_code": 400}
        
        # Find matching route
        route_handler = None
        path_params = {}
        
        for route_path, methods in self.routes.items():
            if http_method in methods:
                # Simple path matching (exact or with parameters)
                if route_path == path:
                    route_handler = methods[http_method]
                    break
                elif "{" in route_path:
                    # Extract path parameters
                    route_parts = route_path.split("/")
                    path_parts = path.split("/")
                    
                    if len(route_parts) == len(path_parts):
                        match = True
                        params = {}
                        for rp, pp in zip(route_parts, path_parts):
                            if rp.startswith("{") and rp.endswith("}"):
                                param_name = rp[1:-1]
                                params[param_name] = pp
                            elif rp != pp:
                                match = False
                                break
                        
                        if match:
                            route_handler = methods[http_method]
                            path_params = params
                            break
        
        if not route_handler:
            return {"error": "Route not found", "status_code": 404}
        
        # Call handler with path parameters and additional kwargs
        return route_handler(path_params=path_params, **kwargs)
    
    # Route handlers
    
    def _health_check(self, **kwargs) -> Dict[str, Any]:
        """Health check endpoint."""
        health = self.twin_manager.get_health_status()
        return {"status": "ok", "health": health, "status_code": 200}
    
    def _list_twins(self, **kwargs) -> Dict[str, Any]:
        """List all twins."""
        twins = self.twin_manager.list_twins()
        return {"twins": twins, "count": len(twins), "status_code": 200}
    
    def _create_twin(self, data=None, **kwargs) -> Dict[str, Any]:
        """Create a new twin."""
        if not data or "device_id" not in data:
            return {"error": "Missing device_id", "status_code": 400}
        
        device_id = data["device_id"]
        device_info = data.get("device_info", {})
        
        twin = self.twin_manager.create_twin(device_id, device_info)
        
        return {
            "device_id": device_id,
            "status": "created",
            "state": twin.get_current_state(),
            "status_code": 201,
        }
    
    def _get_twin(self, path_params=None, **kwargs) -> Dict[str, Any]:
        """Get twin information."""
        if not path_params or "twin_id" not in path_params:
            return {"error": "Missing twin_id", "status_code": 400}
        
        twin = self.twin_manager.get_twin(path_params["twin_id"])
        if not twin:
            return {"error": "Twin not found", "status_code": 404}
        
        return {
            "device_id": twin.device_id,
            "state": twin.get_current_state(),
            "status_code": 200,
        }
    
    def _delete_twin(self, path_params=None, **kwargs) -> Dict[str, Any]:
        """Delete a twin."""
        if not path_params or "twin_id" not in path_params:
            return {"error": "Missing twin_id", "status_code": 400}
        
        success = self.twin_manager.delete_twin(path_params["twin_id"])
        if success:
            return {"status": "deleted", "status_code": 200}
        return {"error": "Twin not found", "status_code": 404}
    
    def _get_twin_state(self, path_params=None, **kwargs) -> Dict[str, Any]:
        """Get current twin state."""
        if not path_params or "twin_id" not in path_params:
            return {"error": "Missing twin_id", "status_code": 400}
        
        twin = self.twin_manager.get_twin(path_params["twin_id"])
        if not twin:
            return {"error": "Twin not found", "status_code": 404}
        
        return {"state": twin.get_current_state(), "status_code": 200}
    
    def _update_twin_state(self, path_params=None, data=None, **kwargs) -> Dict[str, Any]:
        """Update twin state."""
        if not path_params or "twin_id" not in path_params:
            return {"error": "Missing twin_id", "status_code": 400}
        
        if not data:
            return {"error": "Missing state data", "status_code": 400}
        
        success = self.twin_manager.sync_from_hardware(path_params["twin_id"], data)
        if success:
            return {"status": "updated", "status_code": 200}
        return {"error": "Twin not found", "status_code": 404}
    
    def _get_dashboard(self, path_params=None, **kwargs) -> Dict[str, Any]:
        """Get device dashboard."""
        if not path_params or "twin_id" not in path_params:
            return {"error": "Missing twin_id", "status_code": 400}
        
        dashboard = self.visualizer.get_device_dashboard(path_params["twin_id"])
        if dashboard:
            return {"dashboard": dashboard, "status_code": 200}
        return {"error": "Twin not found", "status_code": 404}
    
    def _get_overview(self, **kwargs) -> Dict[str, Any]:
        """Get overview dashboard."""
        overview = self.visualizer.get_overview_dashboard()
        return {"overview": overview, "status_code": 200}
    
    def _get_timeline(self, path_params=None, params=None, **kwargs) -> Dict[str, Any]:
        """Get state timeline."""
        if not path_params or "twin_id" not in path_params:
            return {"error": "Missing twin_id", "status_code": 400}
        
        duration = int(params.get("duration", 60)) if params else 60
        timeline = self.visualizer.get_state_timeline(path_params["twin_id"], duration)
        
        if timeline:
            return {"timeline": timeline, "status_code": 200}
        return {"error": "Twin not found", "status_code": 404}
    
    def _get_blockchain(self, path_params=None, **kwargs) -> Dict[str, Any]:
        """Get blockchain log."""
        if not path_params or "twin_id" not in path_params:
            return {"error": "Missing twin_id", "status_code": 400}
        
        device_id = path_params["twin_id"]
        if device_id not in self.blockchain_loggers:
            return {"error": "Blockchain not enabled for this twin", "status_code": 404}
        
        logger = self.blockchain_loggers[device_id]
        return {
            "blockchain": logger.get_chain(),
            "stats": logger.get_chain_stats(),
            "status_code": 200,
        }
    
    def _verify_blockchain(self, path_params=None, **kwargs) -> Dict[str, Any]:
        """Verify blockchain integrity."""
        if not path_params or "twin_id" not in path_params:
            return {"error": "Missing twin_id", "status_code": 400}
        
        device_id = path_params["twin_id"]
        if device_id not in self.blockchain_loggers:
            return {"error": "Blockchain not enabled for this twin", "status_code": 404}
        
        logger = self.blockchain_loggers[device_id]
        is_valid = logger.verify_chain()
        
        return {
            "device_id": device_id,
            "is_valid": is_valid,
            "chain_length": len(logger.chain),
            "status_code": 200,
        }
