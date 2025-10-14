"""
Prometheus metrics exporter for Accelerapp.
Integrates with existing metrics collector to export to Prometheus.
"""

import time
from typing import Optional


class PrometheusMetricsExporter:
    """
    Exports Accelerapp metrics in Prometheus format.
    """
    
    def __init__(self, metrics_collector=None):
        """
        Initialize metrics exporter.
        
        Args:
            metrics_collector: MetricsCollector instance (from accelerapp.monitoring)
        """
        if metrics_collector is None:
            from accelerapp.monitoring import get_metrics
            metrics_collector = get_metrics()
        
        self.metrics_collector = metrics_collector
        self._start_time = time.time()
    
    def generate_prometheus_metrics(self) -> str:
        """
        Generate metrics in Prometheus text format.
        
        Returns:
            Metrics in Prometheus exposition format
        """
        lines = []
        
        # Get all metrics from collector
        all_metrics = self.metrics_collector.get_all_metrics()
        
        # Export uptime
        lines.append("# HELP accelerapp_uptime_seconds Application uptime in seconds")
        lines.append("# TYPE accelerapp_uptime_seconds gauge")
        lines.append(f"accelerapp_uptime_seconds {all_metrics['uptime_seconds']:.2f}")
        lines.append("")
        
        # Export counters
        for name, value in all_metrics.get("counters", {}).items():
            metric_name = f"accelerapp_{name}"
            lines.append(f"# HELP {metric_name} Counter metric")
            lines.append(f"# TYPE {metric_name} counter")
            lines.append(f"{metric_name} {value}")
            lines.append("")
        
        # Export gauges
        for name, value in all_metrics.get("gauges", {}).items():
            metric_name = f"accelerapp_{name}"
            lines.append(f"# HELP {metric_name} Gauge metric")
            lines.append(f"# TYPE {metric_name} gauge")
            lines.append(f"{metric_name} {value}")
            lines.append("")
        
        # Export histograms
        for name, histogram_data in all_metrics.get("histograms", {}).items():
            metric_name = f"accelerapp_{name}"
            
            # Histogram samples
            lines.append(f"# HELP {metric_name} Histogram metric")
            lines.append(f"# TYPE {metric_name} histogram")
            
            # Buckets
            buckets = histogram_data.get("buckets", [])
            cumulative_count = 0
            
            for le, count in buckets:
                cumulative_count += count
                lines.append(f'{metric_name}_bucket{{le="{le}"}} {cumulative_count}')
            
            # +Inf bucket
            lines.append(f'{metric_name}_bucket{{le="+Inf"}} {cumulative_count}')
            
            # Sum and count
            lines.append(f"{metric_name}_sum {histogram_data.get('sum', 0)}")
            lines.append(f"{metric_name}_count {histogram_data.get('count', 0)}")
            lines.append("")
        
        return "\n".join(lines)
    
    def export_to_file(self, filepath: str) -> None:
        """
        Export metrics to a file.
        
        Args:
            filepath: Path to output file
        """
        metrics = self.generate_prometheus_metrics()
        with open(filepath, 'w') as f:
            f.write(metrics)


def setup_metrics_export(port: int = 8000, path: str = "/metrics"):
    """
    Setup HTTP endpoint for Prometheus metrics scraping.
    
    Args:
        port: Port to listen on
        path: URL path for metrics endpoint
        
    Note:
        This is a simple implementation. For production, use a proper
        web framework or the prometheus_client library.
    """
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from accelerapp.monitoring import get_metrics
        
        metrics_collector = get_metrics()
        exporter = PrometheusMetricsExporter(metrics_collector)
        
        class MetricsHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == path:
                    metrics = exporter.generate_prometheus_metrics()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain; version=0.0.4')
                    self.end_headers()
                    self.wfile.write(metrics.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        server = HTTPServer(('0.0.0.0', port), MetricsHandler)
        print(f"Metrics endpoint available at http://0.0.0.0:{port}{path}")
        
        # Run in background thread
        import threading
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        
        return server
        
    except Exception as e:
        print(f"Warning: Failed to setup metrics endpoint: {e}")
        return None
