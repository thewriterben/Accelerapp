#!/usr/bin/env python3
"""
Monitoring web service for Accelerapp.
Provides HTTP endpoints for health checks and metrics.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import sys
import os

# Add parent directory to path to import health_check
sys.path.insert(0, os.path.dirname(__file__))
import health_check


class MonitoringHandler(BaseHTTPRequestHandler):
    """HTTP request handler for monitoring endpoints."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.handle_health()
        elif parsed_path.path == '/metrics':
            self.handle_metrics()
        elif parsed_path.path == '/status':
            self.handle_status()
        else:
            self.send_error(404, 'Endpoint not found')
    
    def handle_health(self):
        """Handle health check endpoint."""
        try:
            health_data = health_check.get_system_health()
            
            # Determine HTTP status code based on health
            if health_data['overall_status'] == 'healthy':
                status_code = 200
            elif health_data['overall_status'] == 'degraded':
                status_code = 200  # Still return 200 but with warning
            else:
                status_code = 503  # Service Unavailable
            
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health_data, indent=2).encode())
        except Exception as e:
            self.send_error(500, f'Internal error: {str(e)}')
    
    def handle_metrics(self):
        """Handle metrics endpoint (Prometheus-like format)."""
        try:
            health_data = health_check.get_system_health()
            checks = health_data.get('checks', {})
            
            metrics = []
            
            # Disk metrics
            disk = checks.get('disk_space', {})
            if 'total_gb' in disk:
                metrics.append(f'accelerapp_disk_total_gb {disk["total_gb"]}')
                metrics.append(f'accelerapp_disk_used_gb {disk["used_gb"]}')
                metrics.append(f'accelerapp_disk_free_gb {disk["free_gb"]}')
                metrics.append(f'accelerapp_disk_percent_used {disk["percent_used"]}')
            
            # Memory metrics
            memory = checks.get('memory', {})
            if 'total_mb' in memory:
                metrics.append(f'accelerapp_memory_total_mb {memory["total_mb"]}')
                metrics.append(f'accelerapp_memory_used_mb {memory["used_mb"]}')
                metrics.append(f'accelerapp_memory_available_mb {memory["available_mb"]}')
                metrics.append(f'accelerapp_memory_percent_used {memory["percent_used"]}')
            
            # LLM service
            llm = checks.get('llm_service', {})
            llm_healthy = 1 if llm.get('status') == 'healthy' else 0
            metrics.append(f'accelerapp_llm_service_healthy {llm_healthy}')
            if 'models_available' in llm:
                metrics.append(f'accelerapp_llm_models_available {llm["models_available"]}')
            
            # Overall health
            health_status = {'healthy': 1, 'degraded': 0.5, 'unhealthy': 0}.get(
                health_data.get('overall_status', 'unhealthy'), 0
            )
            metrics.append(f'accelerapp_health_status {health_status}')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('\n'.join(metrics).encode())
        except Exception as e:
            self.send_error(500, f'Internal error: {str(e)}')
    
    def handle_status(self):
        """Handle simple status endpoint."""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {
                "service": "accelerapp-monitoring",
                "status": "running",
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(status, indent=2).encode())
        except Exception as e:
            self.send_error(500, f'Internal error: {str(e)}')
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=8080):
    """Run the monitoring HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MonitoringHandler)
    print(f'Starting monitoring service on port {port}...')
    print(f'Available endpoints:')
    print(f'  - http://localhost:{port}/health')
    print(f'  - http://localhost:{port}/metrics')
    print(f'  - http://localhost:{port}/status')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down monitoring service...')
        httpd.shutdown()


if __name__ == '__main__':
    port = int(os.environ.get('MONITOR_PORT', 8080))
    run_server(port)
