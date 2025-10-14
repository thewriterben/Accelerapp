# Accelerapp Observability Stack

This directory contains the complete observability stack for Accelerapp, including monitoring, logging, and distributed tracing.

## 🎯 Overview

The observability stack provides:
- **Metrics Collection**: Prometheus for time-series metrics
- **Visualization**: Grafana for dashboards and alerts
- **Log Aggregation**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Distributed Tracing**: Jaeger with OpenTelemetry
- **Alert Management**: AlertManager for notifications

## 📁 Directory Structure

```
observability/
├── prometheus/          # Prometheus configuration
│   ├── prometheus.yml
│   ├── alert-rules.yml
│   ├── alertmanager.yml
│   └── kubernetes-deployment.yaml
├── grafana/            # Grafana configuration
│   ├── datasource.yml
│   ├── dashboard-system-overview.json
│   └── kubernetes-deployment.yaml
├── elk/                # ELK stack configuration
│   ├── elasticsearch.yaml
│   ├── logstash.yaml
│   ├── logstash-config.conf
│   └── kibana.yaml
├── jaeger/             # Jaeger configuration
│   └── kubernetes-deployment.yaml
├── otel/               # OpenTelemetry configuration
│   ├── otel-collector-config.yaml
│   └── kubernetes-deployment.yaml
├── helm/               # Helm charts
├── playbooks/          # Incident response playbooks
│   ├── high-error-rate.md
│   └── service-down.md
├── docker-compose.yml  # Docker Compose deployment
└── README.md          # This file
```

## 🚀 Quick Start

### Docker Compose Deployment

Deploy the entire observability stack with Docker Compose:

```bash
cd deployment/observability
docker-compose up -d
```

Access the services:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Kibana: http://localhost:5601
- Jaeger UI: http://localhost:16686
- AlertManager: http://localhost:9093

### Kubernetes Deployment

Deploy to Kubernetes:

```bash
# Create observability namespace
kubectl create namespace observability

# Deploy Prometheus
kubectl apply -f prometheus/kubernetes-deployment.yaml

# Deploy Grafana
kubectl apply -f grafana/kubernetes-deployment.yaml

# Deploy ELK Stack
kubectl apply -f elk/elasticsearch.yaml
kubectl apply -f elk/logstash.yaml
kubectl apply -f elk/kibana.yaml

# Deploy Jaeger
kubectl apply -f jaeger/kubernetes-deployment.yaml

# Deploy OpenTelemetry Collector
kubectl apply -f otel/kubernetes-deployment.yaml
```

Access services (port-forward):
```bash
kubectl port-forward -n observability svc/prometheus 9090:9090
kubectl port-forward -n observability svc/grafana 3000:3000
kubectl port-forward -n observability svc/kibana 5601:5601
kubectl port-forward -n observability svc/jaeger-query 16686:16686
```

## 📊 Metrics

### Prometheus Metrics Exposed by Accelerapp

- `accelerapp_requests_total` - Total number of requests
- `accelerapp_errors_total` - Total number of errors
- `accelerapp_request_duration_seconds` - Request duration histogram
- `accelerapp_code_generation_total` - Code generation requests
- `accelerapp_code_generation_failures_total` - Failed code generations
- `accelerapp_health_check_status` - Health check status (0=healthy, 1=unhealthy)
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage

### Custom Metrics

Add custom metrics in your code:

```python
from accelerapp.monitoring import get_metrics

metrics = get_metrics()

# Counter
counter = metrics.counter("my_operation_total", "Total operations")
counter.inc()

# Gauge
gauge = metrics.gauge("active_connections", "Active connections")
gauge.set(10)

# Histogram
histogram = metrics.histogram("operation_duration", "Operation duration")
histogram.observe(0.245)
```

## 📝 Logging

### Log Formats

Accelerapp uses structured JSON logging:

```json
{
  "timestamp": "2025-10-14T21:34:05.972Z",
  "level": "INFO",
  "logger": "accelerapp.api",
  "message": "Request processed successfully",
  "correlation_id": "req-123",
  "user_id": "user456",
  "duration_ms": 245
}
```

### Sending Logs

Logs are automatically collected by:
- **Docker**: Collected by Logstash via TCP (port 5000)
- **Kubernetes**: Collected by Filebeat or Fluentd

Configure logging in your application:

```python
from accelerapp.monitoring import setup_logging, get_logger

# Setup structured logging
setup_logging(level="INFO", structured=True)

# Get logger with correlation ID
logger = get_logger(__name__, correlation_id="req-123")
logger.info("Operation completed", extra_fields={"user_id": 456})
```

### Searching Logs in Kibana

1. Open Kibana: http://localhost:5601
2. Create index pattern: `accelerapp-logs-*`
3. Use queries:
   - `level:ERROR` - All errors
   - `correlation_id:"req-123"` - Specific request
   - `app:accelerapp AND level:ERROR` - App errors

## 🔍 Distributed Tracing

### Trace Collection

Traces are collected via:
- OpenTelemetry SDK (recommended)
- Jaeger SDK (legacy)

### Instrumenting Code

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("operation_name")
def my_operation():
    span = trace.get_current_span()
    span.set_attribute("user.id", 123)
    span.set_attribute("operation.type", "code_generation")
    
    try:
        # Your code here
        result = do_work()
        span.set_status(Status(StatusCode.OK))
        return result
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.record_exception(e)
        raise
```

### Viewing Traces

1. Open Jaeger UI: http://localhost:16686
2. Select service: `accelerapp`
3. Find traces by:
   - Operation name
   - Tags (e.g., `error=true`)
   - Duration
   - Time range

## 🚨 Alerts

### Configured Alerts

1. **HighErrorRate** - Error rate > 5% for 5 minutes
2. **ServiceDown** - Service unavailable for 2 minutes
3. **HighMemoryUsage** - Memory > 85% for 5 minutes
4. **HighCPUUsage** - CPU > 80% for 5 minutes
5. **SlowResponseTime** - P95 latency > 1s for 5 minutes
6. **LLMServiceUnavailable** - Ollama down for 2 minutes
7. **CodeGenerationFailures** - Failure rate > 10% for 5 minutes

### Alert Routing

Alerts are routed based on severity:
- **Critical**: Email + Slack + PagerDuty (immediate)
- **High**: Email + Slack (within 30 min)
- **Warning**: Email + Slack (within 1 hour)
- **Info**: Webhook only

### Configuring Alerts

Edit `prometheus/alertmanager.yml`:

```yaml
receivers:
  - name: 'critical-alerts'
    email_configs:
      - to: 'ops-team@example.com'
    slack_configs:
      - api_url: 'YOUR_WEBHOOK_URL'
        channel: '#alerts'
    pagerduty_configs:
      - service_key: 'YOUR_KEY'
```

## 📊 Dashboards

### Pre-built Grafana Dashboards

1. **System Overview** - Service status, request rate, errors, latency
2. **Resource Usage** - CPU, memory, disk
3. **Application Metrics** - Code generation, success rate
4. **Alerts** - Active alerts and history

### Creating Custom Dashboards

1. Open Grafana: http://localhost:3000
2. Click "+" → "Dashboard"
3. Add panel with PromQL query
4. Example queries:
   ```promql
   # Request rate
   rate(accelerapp_requests_total[5m])
   
   # Error percentage
   rate(accelerapp_errors_total[5m]) / rate(accelerapp_requests_total[5m]) * 100
   
   # P95 latency
   histogram_quantile(0.95, rate(accelerapp_request_duration_seconds_bucket[5m]))
   ```

## 🔧 Configuration

### Prometheus Retention

Adjust data retention in `prometheus.yml`:
```yaml
storage.tsdb.retention.time: 30d  # Keep data for 30 days
```

### Log Retention

Elasticsearch index lifecycle:
```bash
# Set retention policy
curl -X PUT "localhost:9200/_ilm/policy/accelerapp-logs" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {}
      },
      "delete": {
        "min_age": "30d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'
```

### Trace Sampling

Configure sampling in `otel-collector-config.yaml`:
```yaml
processors:
  probabilistic_sampler:
    sampling_percentage: 10  # Sample 10% of traces
```

## 📚 Incident Response

See the `playbooks/` directory for detailed incident response procedures:

- [High Error Rate](playbooks/high-error-rate.md)
- [Service Down](playbooks/service-down.md)

## 🔗 Useful Links

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)

## 🤝 Contributing

To add new alerts, dashboards, or playbooks:

1. Create/update configuration files
2. Test in staging environment
3. Document changes in this README
4. Submit pull request

## 📞 Support

For issues with the observability stack:
- Check logs: `kubectl logs -n observability <pod-name>`
- Review alerts: http://prometheus:9090/alerts
- Contact: ops-team@accelerapp.example.com
