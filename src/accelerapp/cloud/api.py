"""
Cloud API handler for REST endpoints.
"""

from typing import Dict, Any, Optional, Callable
from enum import Enum


class HTTPMethod(Enum):
    """HTTP methods supported by the API."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class CloudAPIHandler:
    """
    Handles REST API endpoints for cloud generation service.
    Provides routing and request handling infrastructure.
    """
    
    def __init__(self, service=None):
        """
        Initialize API handler.
        
        Args:
            service: CloudGenerationService instance
        """
        self.service = service
        self.routes: Dict[str, Dict[HTTPMethod, Callable]] = {}
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup default API routes."""
        self.register_route('/health', HTTPMethod.GET, self._health_check)
        self.register_route('/jobs', HTTPMethod.POST, self._submit_job)
        self.register_route('/jobs', HTTPMethod.GET, self._list_jobs)
        self.register_route('/jobs/{job_id}', HTTPMethod.GET, self._get_job_status)
        self.register_route('/jobs/{job_id}', HTTPMethod.DELETE, self._cancel_job)
    
    def register_route(
        self,
        path: str,
        method: HTTPMethod,
        handler: Callable
    ):
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
    
    def handle_request(
        self,
        path: str,
        method: HTTPMethod,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Handle an API request.
        
        Args:
            path: URL path
            method: HTTP method
            data: Request body data
            params: URL parameters
            
        Returns:
            Response dictionary
        """
        # Find matching route
        for route_path, methods in self.routes.items():
            if self._match_path(route_path, path):
                if method in methods:
                    handler = methods[method]
                    path_params = self._extract_path_params(route_path, path)
                    return handler(data=data, params=params, path_params=path_params)
        
        return {
            'error': 'Route not found',
            'status_code': 404
        }
    
    def _match_path(self, route: str, path: str) -> bool:
        """Check if path matches route pattern."""
        route_parts = route.split('/')
        path_parts = path.split('/')
        
        if len(route_parts) != len(path_parts):
            return False
        
        for r, p in zip(route_parts, path_parts):
            if r.startswith('{') and r.endswith('}'):
                continue
            if r != p:
                return False
        
        return True
    
    def _extract_path_params(self, route: str, path: str) -> Dict[str, str]:
        """Extract parameters from path."""
        route_parts = route.split('/')
        path_parts = path.split('/')
        params = {}
        
        for r, p in zip(route_parts, path_parts):
            if r.startswith('{') and r.endswith('}'):
                param_name = r[1:-1]
                params[param_name] = p
        
        return params
    
    def _health_check(self, **kwargs) -> Dict[str, Any]:
        """Health check endpoint."""
        if self.service:
            health = self.service.get_service_health()
            return {'status': 'ok', 'health': health, 'status_code': 200}
        return {'status': 'error', 'message': 'Service not initialized', 'status_code': 503}
    
    def _submit_job(self, data=None, **kwargs) -> Dict[str, Any]:
        """Submit job endpoint."""
        if not self.service:
            return {'error': 'Service not initialized', 'status_code': 503}
        
        if not data or 'spec' not in data:
            return {'error': 'Missing spec in request', 'status_code': 400}
        
        job_id = self.service.submit_job(
            data['spec'],
            priority=data.get('priority', 'normal')
        )
        
        return {
            'job_id': job_id,
            'status': 'queued',
            'status_code': 201
        }
    
    def _list_jobs(self, params=None, **kwargs) -> Dict[str, Any]:
        """List jobs endpoint."""
        if not self.service:
            return {'error': 'Service not initialized', 'status_code': 503}
        
        status_filter = params.get('status') if params else None
        jobs = self.service.list_jobs(status=status_filter)
        
        return {
            'jobs': jobs,
            'count': len(jobs),
            'status_code': 200
        }
    
    def _get_job_status(self, path_params=None, **kwargs) -> Dict[str, Any]:
        """Get job status endpoint."""
        if not self.service:
            return {'error': 'Service not initialized', 'status_code': 503}
        
        job_id = path_params.get('job_id') if path_params else None
        if not job_id:
            return {'error': 'Missing job_id', 'status_code': 400}
        
        job = self.service.get_job_status(job_id)
        if job:
            return {'job': job, 'status_code': 200}
        
        return {'error': 'Job not found', 'status_code': 404}
    
    def _cancel_job(self, path_params=None, **kwargs) -> Dict[str, Any]:
        """Cancel job endpoint."""
        if not self.service:
            return {'error': 'Service not initialized', 'status_code': 503}
        
        job_id = path_params.get('job_id') if path_params else None
        if not job_id:
            return {'error': 'Missing job_id', 'status_code': 400}
        
        success = self.service.cancel_job(job_id)
        if success:
            return {'message': 'Job cancelled', 'status_code': 200}
        
        return {'error': 'Job not found or cannot be cancelled', 'status_code': 404}
