"""
Tests for cloud generation service.
"""

import pytest
from accelerapp.cloud import (
    CloudGenerationService,
    CloudAPIHandler,
    AuthenticationManager,
    JobQueue,
)
from accelerapp.cloud.api import HTTPMethod


def test_cloud_service_import():
    """Test cloud service imports."""
    assert CloudGenerationService is not None
    assert CloudAPIHandler is not None
    assert AuthenticationManager is not None
    assert JobQueue is not None


def test_cloud_service_initialization():
    """Test cloud service initialization."""
    service = CloudGenerationService()
    assert service is not None
    assert service.active is False
    assert len(service.jobs) == 0


def test_cloud_service_start_stop():
    """Test starting and stopping cloud service."""
    service = CloudGenerationService()
    
    assert service.start() is True
    assert service.active is True
    
    assert service.stop() is True
    assert service.active is False


def test_cloud_service_submit_job():
    """Test job submission."""
    service = CloudGenerationService()
    service.start()
    
    spec = {'device_name': 'Test Device', 'platform': 'arduino'}
    job_id = service.submit_job(spec, priority='normal')
    
    assert job_id is not None
    assert len(service.jobs) == 1
    
    job = service.get_job_status(job_id)
    assert job is not None
    assert job['status'] == 'queued'
    assert job['spec'] == spec


def test_cloud_service_list_jobs():
    """Test listing jobs."""
    service = CloudGenerationService()
    
    service.submit_job({'device': 'test1'})
    service.submit_job({'device': 'test2'})
    
    jobs = service.list_jobs()
    assert len(jobs) == 2
    
    # Test filtering
    jobs = service.list_jobs(status='queued')
    assert len(jobs) == 2


def test_cloud_service_cancel_job():
    """Test job cancellation."""
    service = CloudGenerationService()
    
    job_id = service.submit_job({'device': 'test'})
    
    assert service.cancel_job(job_id) is True
    
    job = service.get_job_status(job_id)
    assert job['status'] == 'cancelled'


def test_cloud_service_health():
    """Test service health check."""
    service = CloudGenerationService()
    
    health = service.get_service_health()
    assert 'active' in health
    assert 'total_jobs' in health
    assert health['total_jobs'] == 0


def test_api_handler_initialization():
    """Test API handler initialization."""
    service = CloudGenerationService()
    api = CloudAPIHandler(service)
    
    assert api is not None
    assert api.service == service
    assert len(api.routes) > 0


def test_api_handler_health_check():
    """Test health check endpoint."""
    service = CloudGenerationService()
    service.start()
    api = CloudAPIHandler(service)
    
    response = api.handle_request('/health', HTTPMethod.GET)
    
    assert response['status_code'] == 200
    assert response['status'] == 'ok'


def test_api_handler_submit_job():
    """Test job submission endpoint."""
    service = CloudGenerationService()
    api = CloudAPIHandler(service)
    
    data = {'spec': {'device': 'test'}, 'priority': 'high'}
    response = api.handle_request('/jobs', HTTPMethod.POST, data=data)
    
    assert response['status_code'] == 201
    assert 'job_id' in response


def test_api_handler_list_jobs():
    """Test list jobs endpoint."""
    service = CloudGenerationService()
    api = CloudAPIHandler(service)
    
    service.submit_job({'device': 'test'})
    
    response = api.handle_request('/jobs', HTTPMethod.GET)
    
    assert response['status_code'] == 200
    assert 'jobs' in response
    assert response['count'] == 1


def test_api_handler_get_job_status():
    """Test get job status endpoint."""
    service = CloudGenerationService()
    api = CloudAPIHandler(service)
    
    job_id = service.submit_job({'device': 'test'})
    
    response = api.handle_request(f'/jobs/{job_id}', HTTPMethod.GET)
    
    assert response['status_code'] == 200
    assert 'job' in response


def test_authentication_create_user():
    """Test user creation."""
    auth = AuthenticationManager()
    
    assert auth.create_user('testuser', 'password123', roles=['user']) is True
    assert auth.create_user('testuser', 'password456') is False  # Duplicate


def test_authentication_authenticate():
    """Test user authentication."""
    auth = AuthenticationManager()
    auth.create_user('testuser', 'password123')
    
    token = auth.authenticate('testuser', 'password123')
    assert token is not None
    
    invalid_token = auth.authenticate('testuser', 'wrongpassword')
    assert invalid_token is None


def test_authentication_validate_token():
    """Test token validation."""
    auth = AuthenticationManager()
    auth.create_user('testuser', 'password123')
    
    token = auth.authenticate('testuser', 'password123')
    
    token_info = auth.validate_token(token)
    assert token_info is not None
    assert token_info['username'] == 'testuser'


def test_authentication_revoke_token():
    """Test token revocation."""
    auth = AuthenticationManager()
    auth.create_user('testuser', 'password123')
    
    token = auth.authenticate('testuser', 'password123')
    
    assert auth.revoke_token(token) is True
    assert auth.validate_token(token) is None


def test_authentication_check_permission():
    """Test permission checking."""
    auth = AuthenticationManager()
    auth.create_user('testuser', 'password123', roles=['user', 'admin'])
    
    token = auth.authenticate('testuser', 'password123')
    
    assert auth.check_permission(token, 'user') is True
    assert auth.check_permission(token, 'admin') is True
    assert auth.check_permission(token, 'superadmin') is False


def test_job_queue_enqueue():
    """Test job enqueueing."""
    queue = JobQueue()
    
    success = queue.enqueue('job1', {'data': 'test'}, priority='normal')
    assert success is True


def test_job_queue_dequeue():
    """Test job dequeueing."""
    queue = JobQueue()
    
    queue.enqueue('job1', {'data': 'test1'}, priority='normal')
    queue.enqueue('job2', {'data': 'test2'}, priority='high')
    
    # High priority should come first
    job = queue.dequeue(timeout=1.0)
    assert job is not None
    assert job['job_id'] == 'job2'


def test_job_queue_status():
    """Test queue status."""
    queue = JobQueue()
    
    queue.enqueue('job1', {'data': 'test'})
    
    status = queue.get_status()
    assert status['queued'] == 1
    assert status['processing'] == 0
    assert status['running'] is False


def test_job_queue_processing():
    """Test job processing."""
    queue = JobQueue()
    
    def processor(job_data):
        return {'result': 'success'}
    
    queue.enqueue('job1', {'data': 'test'})
    queue.start_processing(processor)
    
    import time
    time.sleep(2)
    
    queue.stop_processing()
    
    result = queue.get_job_result('job1')
    assert result is not None
