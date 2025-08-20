"""
Performance Monitor for AI Datacenter Resource Management System
"""
import time
import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import os

@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    timestamp: float
    total_cpu_utilization: float
    total_memory_utilization: float
    total_gpu_utilization: float
    total_storage_utilization: float
    active_workloads: int
    pending_workloads: int
    completed_workloads: int
    failed_workloads: int
    average_workload_accuracy: float
    average_workload_throughput: float
    average_workload_latency: float

@dataclass
class WorkloadMetrics:
    """Individual workload performance metrics"""
    workload_id: str
    workload_name: str
    workload_type: str
    timestamp: float
    accuracy: float
    throughput: float
    latency_ms: float
    cpu_utilization: float
    memory_utilization: float
    gpu_utilization: float
    resource_efficiency: float
    performance_score: float

class PerformanceMonitor:
    """Monitors and tracks system and workload performance metrics"""
    
    def __init__(self, config: Dict):
        """
        Initialize performance monitor
        
        Args:
            config (Dict): Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Monitoring configuration
        monitoring_config = config.get('monitoring', {})
        self.collection_interval = monitoring_config.get('metrics_collection_interval_seconds', 30)
        self.retention_hours = monitoring_config.get('performance_history_retention_hours', 168)
        self.alert_thresholds = monitoring_config.get('alert_thresholds', {})
        
        # Metrics storage
        self.system_metrics_history: List[SystemMetrics] = []
        self.workload_metrics_history: List[WorkloadMetrics] = []
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        self.metrics_file = 'logs/performance_metrics.jsonl'
        
        # Performance tracking
        self.last_collection_time = time.time()
        
        self.logger.info("PerformanceMonitor initialized")
    
    def collect_system_metrics(self, datacenter_resources, workload_simulator) -> SystemMetrics:
        """
        Collect current system-wide metrics
        
        Args:
            datacenter_resources: DatacenterResources instance
            workload_simulator: WorkloadSimulator instance
            
        Returns:
            SystemMetrics: Current system metrics
        """
        current_time = time.time()
        
        # Get active workloads
        active_workloads = workload_simulator.get_active_workloads()
        completed_workloads = workload_simulator.completed_workloads
        
        # Calculate average workload performance
        if active_workloads:
            avg_accuracy = sum(w.current_metrics.accuracy for w in active_workloads) / len(active_workloads)
            avg_throughput = sum(w.current_metrics.throughput for w in active_workloads) / len(active_workloads)
            avg_latency = sum(w.current_metrics.latency_ms for w in active_workloads) / len(active_workloads)
        else:
            avg_accuracy = avg_throughput = avg_latency = 0.0
        
        system_metrics = SystemMetrics(
            timestamp=current_time,
            total_cpu_utilization=datacenter_resources.cpu_utilization,
            total_memory_utilization=datacenter_resources.memory_utilization,
            total_gpu_utilization=datacenter_resources.gpu_utilization,
            total_storage_utilization=(datacenter_resources.allocated_storage_gb / 
                                     (datacenter_resources.total_storage_tb * 1024)),
            active_workloads=len(active_workloads),
            pending_workloads=0,  # Would come from a queue in a real system
            completed_workloads=len(completed_workloads),
            failed_workloads=0,  # Would track failed workloads
            average_workload_accuracy=avg_accuracy,
            average_workload_throughput=avg_throughput,
            average_workload_latency=avg_latency
        )
        
        # Store metrics
        self.system_metrics_history.append(system_metrics)
        self._cleanup_old_metrics()
        self._save_metrics_to_file(system_metrics, 'system')
        
        # Check for alerts
        self._check_system_alerts(system_metrics)
        
        return system_metrics
    
    def collect_workload_metrics(self, workload) -> WorkloadMetrics:
        """
        Collect metrics for a specific workload
        
        Args:
            workload: AIWorkload instance
            
        Returns:
            WorkloadMetrics: Workload performance metrics
        """
        current_time = time.time()
        
        # Calculate resource efficiency (performance vs allocated resources)
        resource_efficiency = self._calculate_resource_efficiency(workload)
        
        # Calculate overall performance score
        performance_score = self._calculate_performance_score(workload)
        
        workload_metrics = WorkloadMetrics(
            workload_id=workload.id,
            workload_name=workload.name,
            workload_type=workload.workload_type.value,
            timestamp=current_time,
            accuracy=workload.current_metrics.accuracy,
            throughput=workload.current_metrics.throughput,
            latency_ms=workload.current_metrics.latency_ms,
            cpu_utilization=workload.current_metrics.cpu_utilization,
            memory_utilization=workload.current_metrics.memory_utilization,
            gpu_utilization=workload.current_metrics.gpu_utilization,
            resource_efficiency=resource_efficiency,
            performance_score=performance_score
        )
        
        # Store metrics
        self.workload_metrics_history.append(workload_metrics)
        self._save_metrics_to_file(workload_metrics, 'workload')
        
        return workload_metrics
    
    def _calculate_resource_efficiency(self, workload) -> float:
        """
        Calculate resource efficiency score for a workload
        
        Args:
            workload: AIWorkload instance
            
        Returns:
            float: Resource efficiency score (0.0 - 1.0)
        """
        if not workload.allocated_resources or not workload.current_metrics:
            return 0.0
        
        # Compare performance achieved vs resources allocated
        metrics = workload.current_metrics
        
        # Normalize metrics to 0-1 scale
        accuracy_score = min(1.0, workload.current_metrics.accuracy / workload.min_accuracy)
        throughput_score = min(1.0, workload.current_metrics.throughput / workload.min_throughput)
        latency_score = min(1.0, workload.max_latency_ms / max(1.0, workload.current_metrics.latency_ms))
        
        # Average performance score
        performance = (accuracy_score + throughput_score + latency_score) / 3
        
        # Resource utilization efficiency
        resource_utilization = (metrics.cpu_utilization + 
                              metrics.memory_utilization + 
                              metrics.gpu_utilization) / 3
        
        # Resource efficiency is performance per unit of resource utilization
        if resource_utilization > 0:
            return min(1.0, performance / resource_utilization)
        else:
            return 0.0
    
    def _calculate_performance_score(self, workload) -> float:
        """
        Calculate overall performance score for a workload
        
        Args:
            workload: AIWorkload instance
            
        Returns:
            float: Performance score (0.0 - 100.0)
        """
        if not workload.current_metrics:
            return 0.0
        
        # Get workload type weights from config
        workload_config = self.config.get('workloads', {}).get(workload.workload_type.value, {})
        performance_weight = workload_config.get('performance_weight', 0.7)
        accuracy_weight = workload_config.get('accuracy_weight', 0.3)
        
        # Normalize individual metrics
        accuracy_score = min(100.0, (workload.current_metrics.accuracy / workload.min_accuracy) * 100)
        
        # Performance score based on throughput and latency
        throughput_score = min(100.0, (workload.current_metrics.throughput / workload.min_throughput) * 100)
        latency_score = min(100.0, (workload.max_latency_ms / max(1.0, workload.current_metrics.latency_ms)) * 100)
        performance_metric = (throughput_score + latency_score) / 2
        
        # Weighted overall score
        overall_score = (performance_metric * performance_weight) + (accuracy_score * accuracy_weight)
        
        return min(100.0, overall_score)
    
    def _check_system_alerts(self, metrics: SystemMetrics):
        """
        Check system metrics against alert thresholds
        
        Args:
            metrics (SystemMetrics): System metrics to check
        """
        alerts = []
        
        if metrics.total_cpu_utilization > self.alert_thresholds.get('cpu_utilization', 0.9):
            alerts.append(f"High CPU utilization: {metrics.total_cpu_utilization:.2%}")
        
        if metrics.total_memory_utilization > self.alert_thresholds.get('memory_utilization', 0.85):
            alerts.append(f"High memory utilization: {metrics.total_memory_utilization:.2%}")
        
        if metrics.total_gpu_utilization > self.alert_thresholds.get('gpu_utilization', 0.95):
            alerts.append(f"High GPU utilization: {metrics.total_gpu_utilization:.2%}")
        
        for alert in alerts:
            self.logger.warning(f"ALERT: {alert}")
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff_time = time.time() - (self.retention_hours * 3600)
        
        self.system_metrics_history = [
            m for m in self.system_metrics_history if m.timestamp > cutoff_time
        ]
        
        self.workload_metrics_history = [
            m for m in self.workload_metrics_history if m.timestamp > cutoff_time
        ]
    
    def _save_metrics_to_file(self, metrics, metrics_type: str):
        """
        Save metrics to JSON lines file
        
        Args:
            metrics: Metrics object to save
            metrics_type (str): Type of metrics ('system' or 'workload')
        """
        try:
            with open(self.metrics_file, 'a') as f:
                metrics_dict = asdict(metrics)
                metrics_dict['type'] = metrics_type
                json.dump(metrics_dict, f)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to save metrics to file: {e}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get performance summary for the last N hours
        
        Args:
            hours (int): Number of hours to look back
            
        Returns:
            Dict[str, Any]: Performance summary
        """
        cutoff_time = time.time() - (hours * 3600)
        
        # Filter recent system metrics
        recent_system_metrics = [
            m for m in self.system_metrics_history if m.timestamp > cutoff_time
        ]
        
        # Filter recent workload metrics
        recent_workload_metrics = [
            m for m in self.workload_metrics_history if m.timestamp > cutoff_time
        ]
        
        if not recent_system_metrics:
            return {"error": "No metrics available for the specified time period"}
        
        # System performance summary
        avg_cpu = sum(m.total_cpu_utilization for m in recent_system_metrics) / len(recent_system_metrics)
        avg_memory = sum(m.total_memory_utilization for m in recent_system_metrics) / len(recent_system_metrics)
        avg_gpu = sum(m.total_gpu_utilization for m in recent_system_metrics) / len(recent_system_metrics)
        
        total_workloads_completed = max((m.completed_workloads for m in recent_system_metrics), default=0)
        
        # Workload performance summary
        workload_summary = {}
        if recent_workload_metrics:
            avg_performance_score = sum(m.performance_score for m in recent_workload_metrics) / len(recent_workload_metrics)
            avg_resource_efficiency = sum(m.resource_efficiency for m in recent_workload_metrics) / len(recent_workload_metrics)
            avg_accuracy = sum(m.accuracy for m in recent_workload_metrics) / len(recent_workload_metrics)
            
            workload_summary = {
                "average_performance_score": avg_performance_score,
                "average_resource_efficiency": avg_resource_efficiency,
                "average_accuracy": avg_accuracy,
                "total_workload_metrics_collected": len(recent_workload_metrics)
            }
        
        return {
            "time_period_hours": hours,
            "system_performance": {
                "average_cpu_utilization": avg_cpu,
                "average_memory_utilization": avg_memory,
                "average_gpu_utilization": avg_gpu,
                "total_workloads_completed": total_workloads_completed,
                "total_system_metrics_collected": len(recent_system_metrics)
            },
            "workload_performance": workload_summary,
            "summary_generated_at": datetime.now().isoformat()
        }
    
    def get_latest_metrics(self) -> Dict[str, Any]:
        """
        Get the latest system and workload metrics
        
        Returns:
            Dict[str, Any]: Latest metrics
        """
        latest_system = self.system_metrics_history[-1] if self.system_metrics_history else None
        latest_workloads = self.workload_metrics_history[-10:] if self.workload_metrics_history else []
        
        return {
            "latest_system_metrics": asdict(latest_system) if latest_system else None,
            "latest_workload_metrics": [asdict(m) for m in latest_workloads],
            "timestamp": time.time()
        }