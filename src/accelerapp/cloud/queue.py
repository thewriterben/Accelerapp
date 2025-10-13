"""
Job queue system for cloud generation service.
"""

from typing import Dict, Any, Optional, List, Callable
from queue import PriorityQueue
from dataclasses import dataclass, field
from datetime import datetime
import threading


@dataclass(order=True)
class QueuedJob:
    """Represents a queued job with priority."""
    priority: int
    job_data: Dict[str, Any] = field(compare=False)
    timestamp: str = field(compare=False)


class JobQueue:
    """
    Priority-based job queue for code generation tasks.
    Supports job prioritization and worker processing.
    """
    
    PRIORITY_MAP = {
        'low': 3,
        'normal': 2,
        'high': 1,
    }
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize job queue.
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.queue = PriorityQueue()
        self.processing: Dict[str, Dict[str, Any]] = {}
        self.completed: Dict[str, Dict[str, Any]] = {}
        self.failed: Dict[str, Dict[str, Any]] = {}
        self.workers: List[threading.Thread] = []
        self.running = False
        self.lock = threading.Lock()
    
    def enqueue(
        self,
        job_id: str,
        job_data: Dict[str, Any],
        priority: str = 'normal'
    ) -> bool:
        """
        Add a job to the queue.
        
        Args:
            job_id: Unique job identifier
            job_data: Job data dictionary
            priority: Job priority (low, normal, high)
            
        Returns:
            True if enqueued successfully
        """
        priority_value = self.PRIORITY_MAP.get(priority, 2)
        
        job_data['job_id'] = job_id
        job_data['priority'] = priority
        job_data['enqueued_at'] = datetime.utcnow().isoformat()
        
        queued_job = QueuedJob(
            priority=priority_value,
            job_data=job_data,
            timestamp=job_data['enqueued_at']
        )
        
        self.queue.put(queued_job)
        return True
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Get next job from queue.
        
        Args:
            timeout: Maximum time to wait for a job
            
        Returns:
            Job data dictionary or None
        """
        try:
            queued_job = self.queue.get(timeout=timeout)
            return queued_job.job_data
        except:
            return None
    
    def start_processing(
        self,
        processor: Callable[[Dict[str, Any]], Dict[str, Any]]
    ):
        """
        Start processing jobs with worker threads.
        
        Args:
            processor: Function to process jobs
        """
        self.running = True
        
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(processor,),
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
    
    def stop_processing(self):
        """Stop all worker threads."""
        self.running = False
        
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        self.workers.clear()
    
    def _worker_loop(self, processor: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Worker thread main loop."""
        while self.running:
            job_data = self.dequeue(timeout=1.0)
            
            if job_data:
                job_id = job_data['job_id']
                
                with self.lock:
                    self.processing[job_id] = job_data
                
                try:
                    result = processor(job_data)
                    
                    with self.lock:
                        self.completed[job_id] = {
                            **job_data,
                            'result': result,
                            'completed_at': datetime.utcnow().isoformat()
                        }
                        if job_id in self.processing:
                            del self.processing[job_id]
                
                except Exception as e:
                    with self.lock:
                        self.failed[job_id] = {
                            **job_data,
                            'error': str(e),
                            'failed_at': datetime.utcnow().isoformat()
                        }
                        if job_id in self.processing:
                            del self.processing[job_id]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get queue status.
        
        Returns:
            Status dictionary
        """
        with self.lock:
            return {
                'running': self.running,
                'queued': self.queue.qsize(),
                'processing': len(self.processing),
                'completed': len(self.completed),
                'failed': len(self.failed),
                'workers': len(self.workers),
            }
    
    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get result of a completed job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job result or None
        """
        with self.lock:
            if job_id in self.completed:
                return self.completed[job_id]
            if job_id in self.failed:
                return self.failed[job_id]
        return None
