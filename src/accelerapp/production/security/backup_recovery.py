"""
Automated backup and disaster recovery system.
Implements backup scheduling, retention policies, and recovery procedures.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json


class BackupType(Enum):
    """Backup types."""
    
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(Enum):
    """Backup operation status."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RecoveryStatus(Enum):
    """Recovery operation status."""
    
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BackupConfig:
    """Backup configuration."""
    
    config_id: str
    name: str
    backup_type: BackupType
    schedule_cron: str  # Cron expression
    retention_days: int = 30
    enabled: bool = True
    target_paths: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    compression: bool = True
    encryption: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BackupRecord:
    """Backup record."""
    
    backup_id: str
    config_id: str
    backup_type: BackupType
    status: BackupStatus
    started_at: str
    completed_at: Optional[str] = None
    size_bytes: int = 0
    files_count: int = 0
    location: str = ""
    checksum: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPlan:
    """Disaster recovery plan."""
    
    plan_id: str
    name: str
    description: str
    rto_minutes: int = 240  # Recovery Time Objective
    rpo_minutes: int = 60   # Recovery Point Objective
    steps: List[Dict[str, str]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 100
    tested_at: Optional[str] = None


@dataclass
class RecoveryOperation:
    """Recovery operation."""
    
    operation_id: str
    backup_id: str
    plan_id: Optional[str] = None
    status: RecoveryStatus = RecoveryStatus.NOT_STARTED
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    restored_files: int = 0
    failed_files: int = 0
    details: Dict[str, Any] = field(default_factory=dict)


class BackupRecoverySystem:
    """
    Automated backup and disaster recovery system.
    Manages backups, retention, and recovery procedures.
    """
    
    def __init__(self):
        """Initialize backup and recovery system."""
        self.configs: Dict[str, BackupConfig] = {}
        self.backups: Dict[str, BackupRecord] = {}
        self.recovery_plans: Dict[str, RecoveryPlan] = {}
        self.recovery_operations: Dict[str, RecoveryOperation] = {}
        self.backup_history: List[BackupRecord] = []
    
    def create_backup_config(
        self,
        config_id: str,
        name: str,
        backup_type: BackupType,
        schedule_cron: str,
        target_paths: List[str],
        retention_days: int = 30,
        exclude_patterns: Optional[List[str]] = None,
        compression: bool = True,
        encryption: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BackupConfig:
        """
        Create backup configuration.
        
        Args:
            config_id: Configuration identifier
            name: Configuration name
            backup_type: Type of backup
            schedule_cron: Cron schedule expression
            target_paths: Paths to backup
            retention_days: Days to retain backups
            exclude_patterns: File patterns to exclude
            compression: Enable compression
            encryption: Enable encryption
            metadata: Additional metadata
            
        Returns:
            BackupConfig
        """
        config = BackupConfig(
            config_id=config_id,
            name=name,
            backup_type=backup_type,
            schedule_cron=schedule_cron,
            retention_days=retention_days,
            target_paths=target_paths,
            exclude_patterns=exclude_patterns or [],
            compression=compression,
            encryption=encryption,
            metadata=metadata or {}
        )
        self.configs[config_id] = config
        return config
    
    def start_backup(
        self,
        config_id: str,
        backup_id: Optional[str] = None
    ) -> BackupRecord:
        """
        Start backup operation.
        
        Args:
            config_id: Configuration identifier
            backup_id: Optional backup identifier
            
        Returns:
            BackupRecord
        """
        config = self.configs.get(config_id)
        if not config:
            raise ValueError(f"Config {config_id} not found")
        
        if not backup_id:
            backup_id = f"backup-{datetime.utcnow().timestamp()}"
        
        record = BackupRecord(
            backup_id=backup_id,
            config_id=config_id,
            backup_type=config.backup_type,
            status=BackupStatus.IN_PROGRESS,
            started_at=datetime.utcnow().isoformat(),
            location=f"/backups/{config_id}/{backup_id}"
        )
        
        self.backups[backup_id] = record
        return record
    
    def complete_backup(
        self,
        backup_id: str,
        size_bytes: int,
        files_count: int,
        checksum: str,
        success: bool = True
    ) -> BackupRecord:
        """
        Mark backup as completed.
        
        Args:
            backup_id: Backup identifier
            size_bytes: Backup size in bytes
            files_count: Number of files backed up
            checksum: Backup checksum
            success: Whether backup succeeded
            
        Returns:
            BackupRecord
        """
        record = self.backups.get(backup_id)
        if not record:
            raise ValueError(f"Backup {backup_id} not found")
        
        record.status = BackupStatus.COMPLETED if success else BackupStatus.FAILED
        record.completed_at = datetime.utcnow().isoformat()
        record.size_bytes = size_bytes
        record.files_count = files_count
        record.checksum = checksum
        
        self.backup_history.append(record)
        return record
    
    def create_recovery_plan(
        self,
        plan_id: str,
        name: str,
        description: str,
        steps: List[Dict[str, str]],
        rto_minutes: int = 240,
        rpo_minutes: int = 60,
        dependencies: Optional[List[str]] = None,
        priority: int = 100
    ) -> RecoveryPlan:
        """
        Create disaster recovery plan.
        
        Args:
            plan_id: Plan identifier
            name: Plan name
            description: Plan description
            steps: Recovery steps
            rto_minutes: Recovery Time Objective
            rpo_minutes: Recovery Point Objective
            dependencies: Plan dependencies
            priority: Plan priority
            
        Returns:
            RecoveryPlan
        """
        plan = RecoveryPlan(
            plan_id=plan_id,
            name=name,
            description=description,
            rto_minutes=rto_minutes,
            rpo_minutes=rpo_minutes,
            steps=steps,
            dependencies=dependencies or [],
            priority=priority
        )
        self.recovery_plans[plan_id] = plan
        return plan
    
    def start_recovery(
        self,
        backup_id: str,
        operation_id: Optional[str] = None,
        plan_id: Optional[str] = None
    ) -> RecoveryOperation:
        """
        Start recovery operation.
        
        Args:
            backup_id: Backup to recover from
            operation_id: Optional operation identifier
            plan_id: Optional recovery plan to follow
            
        Returns:
            RecoveryOperation
        """
        backup = self.backups.get(backup_id)
        if not backup:
            raise ValueError(f"Backup {backup_id} not found")
        
        if not operation_id:
            operation_id = f"recovery-{datetime.utcnow().timestamp()}"
        
        operation = RecoveryOperation(
            operation_id=operation_id,
            backup_id=backup_id,
            plan_id=plan_id,
            status=RecoveryStatus.IN_PROGRESS,
            started_at=datetime.utcnow().isoformat()
        )
        
        self.recovery_operations[operation_id] = operation
        return operation
    
    def complete_recovery(
        self,
        operation_id: str,
        restored_files: int,
        failed_files: int,
        success: bool = True
    ) -> RecoveryOperation:
        """
        Mark recovery as completed.
        
        Args:
            operation_id: Operation identifier
            restored_files: Number of files restored
            failed_files: Number of files that failed
            success: Whether recovery succeeded
            
        Returns:
            RecoveryOperation
        """
        operation = self.recovery_operations.get(operation_id)
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")
        
        operation.status = RecoveryStatus.COMPLETED if success else RecoveryStatus.FAILED
        operation.completed_at = datetime.utcnow().isoformat()
        operation.restored_files = restored_files
        operation.failed_files = failed_files
        
        return operation
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """
        Clean up old backups based on retention policies.
        
        Returns:
            Cleanup result
        """
        now = datetime.utcnow()
        removed_backups = []
        
        for backup_id, backup in list(self.backups.items()):
            config = self.configs.get(backup.config_id)
            if not config:
                continue
            
            # Parse backup date
            backup_date = datetime.fromisoformat(backup.started_at)
            age_days = (now - backup_date).days
            
            if age_days > config.retention_days:
                removed_backups.append(backup_id)
                del self.backups[backup_id]
        
        return {
            "removed_count": len(removed_backups),
            "removed_backups": removed_backups
        }
    
    def verify_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Verify backup integrity.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Verification result
        """
        backup = self.backups.get(backup_id)
        if not backup:
            return {"valid": False, "reason": "Backup not found"}
        
        if backup.status != BackupStatus.COMPLETED:
            return {"valid": False, "reason": "Backup not completed"}
        
        # In real implementation, would verify checksum and file integrity
        return {
            "valid": True,
            "backup_id": backup_id,
            "size_bytes": backup.size_bytes,
            "files_count": backup.files_count,
            "checksum": backup.checksum
        }
    
    def test_recovery_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Test disaster recovery plan.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Test result
        """
        plan = self.recovery_plans.get(plan_id)
        if not plan:
            return {"success": False, "reason": "Plan not found"}
        
        # Update test timestamp
        plan.tested_at = datetime.utcnow().isoformat()
        
        # In real implementation, would execute test recovery
        return {
            "success": True,
            "plan_id": plan_id,
            "steps_tested": len(plan.steps),
            "tested_at": plan.tested_at
        }
    
    def get_backup_status(self, config_id: str) -> Dict[str, Any]:
        """
        Get backup status for configuration.
        
        Args:
            config_id: Configuration identifier
            
        Returns:
            Status information
        """
        config = self.configs.get(config_id)
        if not config:
            return {"error": "Configuration not found"}
        
        # Find backups for this config
        config_backups = [
            b for b in self.backups.values()
            if b.config_id == config_id
        ]
        
        if not config_backups:
            return {
                "config_id": config_id,
                "status": "no_backups",
                "last_backup": None
            }
        
        # Get latest backup
        latest = max(config_backups, key=lambda b: b.started_at)
        
        return {
            "config_id": config_id,
            "status": latest.status.value,
            "last_backup": latest.started_at,
            "total_backups": len(config_backups),
            "total_size_bytes": sum(b.size_bytes for b in config_backups)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get backup and recovery statistics.
        
        Returns:
            Statistics dictionary
        """
        total_backups = len(self.backups)
        completed_backups = sum(
            1 for b in self.backups.values()
            if b.status == BackupStatus.COMPLETED
        )
        failed_backups = sum(
            1 for b in self.backups.values()
            if b.status == BackupStatus.FAILED
        )
        
        total_size = sum(b.size_bytes for b in self.backups.values())
        
        total_recoveries = len(self.recovery_operations)
        successful_recoveries = sum(
            1 for r in self.recovery_operations.values()
            if r.status == RecoveryStatus.COMPLETED
        )
        
        return {
            "configurations": len(self.configs),
            "total_backups": total_backups,
            "completed_backups": completed_backups,
            "failed_backups": failed_backups,
            "total_size_bytes": total_size,
            "recovery_plans": len(self.recovery_plans),
            "total_recoveries": total_recoveries,
            "successful_recoveries": successful_recoveries
        }
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate backup compliance report.
        
        Returns:
            Compliance report
        """
        stats = self.get_statistics()
        
        # Check if all configs have recent backups
        configs_with_recent_backup = 0
        for config in self.configs.values():
            if not config.enabled:
                continue
            
            config_backups = [
                b for b in self.backups.values()
                if b.config_id == config.config_id
                and b.status == BackupStatus.COMPLETED
            ]
            
            if config_backups:
                latest = max(config_backups, key=lambda b: b.started_at)
                backup_date = datetime.fromisoformat(latest.started_at)
                age_hours = (datetime.utcnow() - backup_date).total_seconds() / 3600
                
                if age_hours < 24:
                    configs_with_recent_backup += 1
        
        compliance_rate = (
            configs_with_recent_backup / len(self.configs) * 100
            if self.configs else 0
        )
        
        # Check if recovery plans are tested
        tested_plans = sum(
            1 for p in self.recovery_plans.values()
            if p.tested_at is not None
        )
        
        return {
            "summary": stats,
            "compliance_rate": round(compliance_rate, 2),
            "configs_with_recent_backup": configs_with_recent_backup,
            "total_configs": len(self.configs),
            "tested_recovery_plans": tested_plans,
            "total_recovery_plans": len(self.recovery_plans),
            "recommendations": self._generate_recommendations(
                compliance_rate, tested_plans, len(self.recovery_plans)
            )
        }
    
    def _generate_recommendations(
        self,
        compliance_rate: float,
        tested_plans: int,
        total_plans: int
    ) -> List[str]:
        """Generate recommendations."""
        recommendations = []
        
        if compliance_rate < 80:
            recommendations.append(
                f"Backup compliance is {compliance_rate:.0f}% - review failed backups"
            )
        
        if total_plans > 0 and tested_plans < total_plans:
            recommendations.append(
                f"Test remaining {total_plans - tested_plans} recovery plans"
            )
        
        if compliance_rate >= 90 and tested_plans == total_plans:
            recommendations.append("Backup and recovery systems are healthy")
            recommendations.append("Continue regular monitoring and testing")
        
        return recommendations
