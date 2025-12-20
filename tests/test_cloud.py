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


# ============================================================
# Tests for Cloud Storage Service
# ============================================================


def test_cloud_storage_imports():
    """Test cloud storage imports."""
    from accelerapp.cloud import (
        CloudStorageService,
        CloudStorageProvider,
        LocalStorageBackend,
        StorageObject,
    )
    assert CloudStorageService is not None
    assert CloudStorageProvider is not None
    assert LocalStorageBackend is not None
    assert StorageObject is not None


def test_cloud_storage_provider_enum():
    """Test CloudStorageProvider enum values."""
    from accelerapp.cloud import CloudStorageProvider
    
    assert CloudStorageProvider.AWS_S3.value == "aws_s3"
    assert CloudStorageProvider.AZURE_BLOB.value == "azure_blob"
    assert CloudStorageProvider.GOOGLE_CLOUD.value == "google_cloud"
    assert CloudStorageProvider.LOCAL.value == "local"


def test_local_storage_backend_initialization():
    """Test local storage backend initialization."""
    from accelerapp.cloud import LocalStorageBackend
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = LocalStorageBackend(tmpdir)
        assert backend.base_path.exists()


def test_local_storage_upload_download():
    """Test upload and download with local storage."""
    from accelerapp.cloud import LocalStorageBackend
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = LocalStorageBackend(tmpdir)
        
        test_data = b"Hello, World!"
        key = "test/file.txt"
        
        # Upload
        result = backend.upload(key, test_data, "text/plain")
        assert result is True
        
        # Download
        data = backend.download(key)
        assert data == test_data


def test_local_storage_exists():
    """Test exists check with local storage."""
    from accelerapp.cloud import LocalStorageBackend
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = LocalStorageBackend(tmpdir)
        
        key = "test/exists.txt"
        
        # Should not exist initially
        assert backend.exists(key) is False
        
        # Upload and check again
        backend.upload(key, b"test", "text/plain")
        assert backend.exists(key) is True


def test_local_storage_delete():
    """Test delete with local storage."""
    from accelerapp.cloud import LocalStorageBackend
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = LocalStorageBackend(tmpdir)
        
        key = "test/delete.txt"
        backend.upload(key, b"test", "text/plain")
        
        assert backend.exists(key) is True
        
        result = backend.delete(key)
        assert result is True
        assert backend.exists(key) is False


def test_local_storage_list_objects():
    """Test listing objects with local storage."""
    from accelerapp.cloud import LocalStorageBackend
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = LocalStorageBackend(tmpdir)
        
        backend.upload("firmware/v1.bin", b"firmware1", "application/octet-stream")
        backend.upload("firmware/v2.bin", b"firmware2", "application/octet-stream")
        backend.upload("sdk/python.zip", b"sdk", "application/zip")
        
        # List all
        all_objects = backend.list_objects()
        assert len(all_objects) == 3
        
        # List with prefix
        firmware = backend.list_objects("firmware/")
        assert len(firmware) == 2


def test_local_storage_get_object_info():
    """Test getting object info with local storage."""
    from accelerapp.cloud import LocalStorageBackend
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = LocalStorageBackend(tmpdir)
        
        key = "test/info.txt"
        test_data = b"test content"
        backend.upload(key, test_data, "text/plain", {"custom": "value"})
        
        info = backend.get_object_info(key)
        assert info is not None
        assert info.key == key
        assert info.size == len(test_data)
        assert info.content_type == "text/plain"
        assert info.metadata.get("custom") == "value"


def test_storage_object_to_dict():
    """Test StorageObject to_dict method."""
    from accelerapp.cloud import StorageObject
    from datetime import datetime
    
    obj = StorageObject(
        key="test/key.txt",
        size=100,
        content_type="text/plain",
        last_modified=datetime.utcnow(),
        etag="abc123",
        metadata={"custom": "value"}
    )
    
    d = obj.to_dict()
    assert d["key"] == "test/key.txt"
    assert d["size"] == 100
    assert d["content_type"] == "text/plain"
    assert d["etag"] == "abc123"
    assert d["metadata"]["custom"] == "value"


def test_cloud_storage_service_initialization():
    """Test CloudStorageService initialization."""
    from accelerapp.cloud import CloudStorageService
    
    service = CloudStorageService()
    assert service is not None
    assert service.backends == {}
    assert service.active_provider is None


def test_cloud_storage_service_register_backend():
    """Test registering backends with CloudStorageService."""
    from accelerapp.cloud import (
        CloudStorageService,
        CloudStorageProvider,
        LocalStorageBackend,
    )
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        service = CloudStorageService()
        backend = LocalStorageBackend(tmpdir)
        
        service.register_backend(CloudStorageProvider.LOCAL, backend)
        
        assert CloudStorageProvider.LOCAL.value in service.backends
        assert service.active_provider == CloudStorageProvider.LOCAL.value


def test_cloud_storage_service_upload_download():
    """Test upload and download artifacts with CloudStorageService."""
    from accelerapp.cloud import (
        CloudStorageService,
        CloudStorageProvider,
        LocalStorageBackend,
    )
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        service = CloudStorageService()
        service.register_backend(CloudStorageProvider.LOCAL, LocalStorageBackend(tmpdir))
        
        # Upload
        result = service.upload_artifact(
            artifact_id="test-artifact-001",
            data=b"Generated code content",
            artifact_type="generated_code",
            metadata={"version": "1.0"}
        )
        
        assert result["success"] is True
        assert result["artifact_id"] == "test-artifact-001"
        
        # Download
        data = service.download_artifact(
            artifact_id="test-artifact-001",
            artifact_type="generated_code"
        )
        
        assert data == b"Generated code content"


def test_cloud_storage_service_list_artifacts():
    """Test listing artifacts with CloudStorageService."""
    from accelerapp.cloud import (
        CloudStorageService,
        CloudStorageProvider,
        LocalStorageBackend,
    )
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        service = CloudStorageService()
        service.register_backend(CloudStorageProvider.LOCAL, LocalStorageBackend(tmpdir))
        
        # Upload multiple artifacts
        service.upload_artifact("fw-001", b"firmware1", "firmware")
        service.upload_artifact("fw-002", b"firmware2", "firmware")
        service.upload_artifact("sdk-001", b"sdk1", "sdk")
        
        # List all
        all_artifacts = service.list_artifacts()
        assert len(all_artifacts) == 3
        
        # List by type
        firmware = service.list_artifacts(artifact_type="firmware")
        assert len(firmware) == 2


def test_cloud_storage_service_delete_artifact():
    """Test deleting artifacts with CloudStorageService."""
    from accelerapp.cloud import (
        CloudStorageService,
        CloudStorageProvider,
        LocalStorageBackend,
    )
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        service = CloudStorageService()
        service.register_backend(CloudStorageProvider.LOCAL, LocalStorageBackend(tmpdir))
        
        service.upload_artifact("delete-test", b"content", "generated_code")
        assert service.artifact_exists("delete-test", "generated_code") is True
        
        result = service.delete_artifact("delete-test", "generated_code")
        assert result is True
        assert service.artifact_exists("delete-test", "generated_code") is False


def test_cloud_storage_service_status():
    """Test getting service status."""
    from accelerapp.cloud import (
        CloudStorageService,
        CloudStorageProvider,
        LocalStorageBackend,
    )
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        service = CloudStorageService({"bucket_name": "test-bucket"})
        service.register_backend(CloudStorageProvider.LOCAL, LocalStorageBackend(tmpdir))
        
        status = service.get_service_status()
        
        assert status["active_provider"] == "local"
        assert status["bucket_name"] == "test-bucket"
        assert "local" in status["registered_backends"]
        assert status["available"] is True


# ============================================================
# Tests for Cloud Sync Service
# ============================================================


def test_cloud_sync_imports():
    """Test cloud sync imports."""
    from accelerapp.cloud import (
        CloudSyncService,
        SyncStatus,
        SyncDirection,
        SyncRecord,
    )
    assert CloudSyncService is not None
    assert SyncStatus is not None
    assert SyncDirection is not None
    assert SyncRecord is not None


def test_sync_status_enum():
    """Test SyncStatus enum values."""
    from accelerapp.cloud import SyncStatus
    
    assert SyncStatus.PENDING.value == "pending"
    assert SyncStatus.IN_PROGRESS.value == "in_progress"
    assert SyncStatus.COMPLETED.value == "completed"
    assert SyncStatus.FAILED.value == "failed"
    assert SyncStatus.CONFLICT.value == "conflict"


def test_sync_direction_enum():
    """Test SyncDirection enum values."""
    from accelerapp.cloud import SyncDirection
    
    assert SyncDirection.UPLOAD.value == "upload"
    assert SyncDirection.DOWNLOAD.value == "download"
    assert SyncDirection.BIDIRECTIONAL.value == "bidirectional"


def test_sync_record_to_dict():
    """Test SyncRecord to_dict method."""
    from accelerapp.cloud import SyncRecord, SyncStatus, SyncDirection
    
    record = SyncRecord(
        record_id="sync-001",
        resource_type="configuration",
        resource_id="config-001",
        direction=SyncDirection.UPLOAD,
        status=SyncStatus.COMPLETED
    )
    
    d = record.to_dict()
    assert d["record_id"] == "sync-001"
    assert d["resource_type"] == "configuration"
    assert d["resource_id"] == "config-001"
    assert d["direction"] == "upload"
    assert d["status"] == "completed"


def test_cloud_sync_service_initialization():
    """Test CloudSyncService initialization."""
    from accelerapp.cloud import CloudSyncService
    
    service = CloudSyncService()
    assert service is not None
    assert service.sync_records == {}
    assert service.sync_handlers == {}


def test_cloud_sync_register_handler():
    """Test registering sync handlers."""
    from accelerapp.cloud import CloudSyncService, SyncDirection
    
    service = CloudSyncService()
    
    def test_handler(resource_id, direction):
        return {"success": True}
    
    service.register_sync_handler("test_resource", test_handler)
    
    assert "test_resource" in service.sync_handlers


def test_cloud_sync_resource():
    """Test syncing a resource."""
    from accelerapp.cloud import CloudSyncService, SyncDirection, SyncStatus
    
    service = CloudSyncService()
    
    def test_handler(resource_id, direction):
        return {"success": True, "remote_hash": "abc123"}
    
    service.register_sync_handler("configuration", test_handler)
    
    record = service.sync_resource(
        resource_type="configuration",
        resource_id="config-001",
        direction=SyncDirection.UPLOAD,
        data={"key": "value"}
    )
    
    assert record.status == SyncStatus.COMPLETED
    assert record.resource_id == "config-001"


def test_cloud_sync_resource_no_handler():
    """Test syncing without handler fails gracefully."""
    from accelerapp.cloud import CloudSyncService, SyncDirection, SyncStatus
    
    service = CloudSyncService()
    
    record = service.sync_resource(
        resource_type="unknown_type",
        resource_id="resource-001",
        direction=SyncDirection.UPLOAD
    )
    
    assert record.status == SyncStatus.FAILED
    assert "No handler" in record.error_message


def test_cloud_sync_configuration():
    """Test syncing configuration."""
    from accelerapp.cloud import CloudSyncService, SyncDirection, SyncStatus
    
    service = CloudSyncService()
    
    def config_handler(resource_id, direction):
        return {"success": True}
    
    service.register_sync_handler("configuration", config_handler)
    
    record = service.sync_configuration(
        config_id="app-config",
        config_data={"setting": "value"},
        direction=SyncDirection.UPLOAD
    )
    
    assert record.resource_type == "configuration"
    assert record.resource_id == "app-config"


def test_cloud_sync_deployment():
    """Test syncing deployment state."""
    from accelerapp.cloud import CloudSyncService, SyncDirection, SyncStatus
    
    service = CloudSyncService()
    
    def deployment_handler(resource_id, direction):
        return {"success": True}
    
    service.register_sync_handler("deployment", deployment_handler)
    
    record = service.sync_deployment(
        deployment_id="deploy-001",
        deployment_data={"status": "running"},
        direction=SyncDirection.UPLOAD
    )
    
    assert record.resource_type == "deployment"
    assert record.resource_id == "deploy-001"


def test_cloud_sync_list_records():
    """Test listing sync records."""
    from accelerapp.cloud import CloudSyncService, SyncDirection, SyncStatus
    
    service = CloudSyncService()
    
    def test_handler(resource_id, direction):
        return {"success": True}
    
    service.register_sync_handler("config", test_handler)
    service.register_sync_handler("deploy", test_handler)
    
    service.sync_resource("config", "c1", SyncDirection.UPLOAD)
    service.sync_resource("config", "c2", SyncDirection.UPLOAD)
    service.sync_resource("deploy", "d1", SyncDirection.UPLOAD)
    
    # List all
    all_records = service.list_sync_records()
    assert len(all_records) == 3
    
    # List by type
    config_records = service.list_sync_records(resource_type="config")
    assert len(config_records) == 2
    
    # List by status
    completed = service.list_sync_records(status=SyncStatus.COMPLETED)
    assert len(completed) == 3


def test_cloud_sync_get_status():
    """Test getting sync record status."""
    from accelerapp.cloud import CloudSyncService, SyncDirection
    
    service = CloudSyncService()
    
    def test_handler(resource_id, direction):
        return {"success": True}
    
    service.register_sync_handler("test", test_handler)
    
    record = service.sync_resource("test", "r1", SyncDirection.UPLOAD)
    
    fetched = service.get_sync_status(record.record_id)
    assert fetched is not None
    assert fetched.record_id == record.record_id


def test_cloud_sync_service_status():
    """Test getting service status."""
    from accelerapp.cloud import CloudSyncService, SyncDirection
    
    service = CloudSyncService({"sync_interval": 120})
    
    def test_handler(resource_id, direction):
        return {"success": True}
    
    service.register_sync_handler("config", test_handler)
    service.sync_resource("config", "c1", SyncDirection.UPLOAD)
    
    status = service.get_service_status()
    
    assert status["sync_interval"] == 120
    assert "config" in status["registered_handlers"]
    assert status["total_records"] == 1
    assert status["completed_count"] == 1


def test_cloud_sync_clear_completed():
    """Test clearing completed records."""
    from accelerapp.cloud import CloudSyncService, SyncDirection
    
    service = CloudSyncService()
    
    def test_handler(resource_id, direction):
        return {"success": True}
    
    service.register_sync_handler("test", test_handler)
    
    service.sync_resource("test", "r1", SyncDirection.UPLOAD)
    service.sync_resource("test", "r2", SyncDirection.UPLOAD)
    
    # Clear with 0 hours (immediate)
    cleared = service.clear_completed_records(older_than_hours=0)
    assert cleared == 2
    
    records = service.list_sync_records()
    assert len(records) == 0
