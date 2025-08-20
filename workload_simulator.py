"""
AI Workload Simulator for Datacenter Resource Management
"""
import random
import time
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class WorkloadType(Enum):
    """Types of AI workloads"""
    TRAINING = "training"
    INFERENCE = "inference"
    DATA_PROCESSING = "data_processing"

class WorkloadStatus(Enum):
    """Status of AI workloads"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ResourceRequirements:
    """Resource requirements for a workload"""
    cpu_cores: int
    memory_gb: float
    gpu_count: int
    storage_gb: float
    network_bandwidth_mbps: int = 100

@dataclass
class PerformanceMetrics:
    """Performance metrics for a workload"""
    accuracy: float = 0.0
    throughput: float = 0.0  # operations per second
    latency_ms: float = 0.0
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    gpu_utilization: float = 0.0

@dataclass
class AIWorkload:
    """Represents an AI workload in the datacenter"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    workload_type: WorkloadType = WorkloadType.INFERENCE
    status: WorkloadStatus = WorkloadStatus.PENDING
    priority: int = 1  # 1-5, higher is more important
    
    # Resource requirements
    resource_requirements: ResourceRequirements = field(default_factory=ResourceRequirements)
    
    # Performance requirements
    min_accuracy: float = 0.95
    max_latency_ms: float = 100.0
    min_throughput: float = 10.0
    
    # Runtime information
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    estimated_duration_hours: float = 1.0
    
    # Performance metrics
    current_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    
    # Resource allocation (assigned by resource manager)
    allocated_resources: Optional[ResourceRequirements] = None

class WorkloadSimulator:
    """Simulates various AI workloads with realistic resource consumption patterns"""
    
    def __init__(self, config: Dict):
        """
        Initialize workload simulator
        
        Args:
            config (Dict): Configuration dictionary
        """
        self.config = config
        self.active_workloads: Dict[str, AIWorkload] = {}
        self.completed_workloads: List[AIWorkload] = []
        
    def generate_workload(self, workload_type: WorkloadType, 
                         custom_config: Optional[Dict] = None) -> AIWorkload:
        """
        Generate a realistic AI workload
        
        Args:
            workload_type (WorkloadType): Type of workload to generate
            custom_config (Optional[Dict]): Custom configuration overrides
            
        Returns:
            AIWorkload: Generated workload
        """
        workload_config = self.config.get('workloads', {}).get(workload_type.value, {})
        
        # Apply custom configuration if provided
        if custom_config:
            workload_config.update(custom_config)
        
        # Generate resource requirements with some randomization
        cpu_cores = self._add_variance(
            workload_config.get('default_cpu_requirement', 4), 0.2
        )
        memory_gb = self._add_variance(
            workload_config.get('default_memory_gb', 16), 0.2
        )
        gpu_count = max(0, int(self._add_variance(
            workload_config.get('default_gpu_requirement', 1), 0.3
        )))
        storage_gb = self._add_variance(50, 0.4)  # Base storage requirement
        
        resource_requirements = ResourceRequirements(
            cpu_cores=int(cpu_cores),
            memory_gb=memory_gb,
            gpu_count=gpu_count,
            storage_gb=storage_gb,
            network_bandwidth_mbps=random.randint(50, 500)
        )
        
        # Generate performance requirements
        workload = AIWorkload(
            name=f"{workload_type.value}_{uuid.uuid4().hex[:8]}",
            workload_type=workload_type,
            priority=random.randint(1, 5),
            resource_requirements=resource_requirements,
            min_accuracy=max(0.8, random.uniform(0.85, 0.99)),
            max_latency_ms=random.uniform(50, 200),
            min_throughput=random.uniform(5, 50),
            estimated_duration_hours=self._add_variance(
                workload_config.get('default_duration_hours', 1), 0.3
            )
        )
        
        return workload
    
    def simulate_workload_performance(self, workload: AIWorkload) -> PerformanceMetrics:
        """
        Simulate realistic performance metrics based on allocated resources
        
        Args:
            workload (AIWorkload): Workload to simulate
            
        Returns:
            PerformanceMetrics: Simulated performance metrics
        """
        if not workload.allocated_resources:
            # No resources allocated - poor performance
            return PerformanceMetrics(
                accuracy=0.0,
                throughput=0.0,
                latency_ms=float('inf'),
                cpu_utilization=0.0,
                memory_utilization=0.0,
                gpu_utilization=0.0
            )
        
        # Calculate performance based on resource allocation vs requirements
        cpu_ratio = min(1.0, workload.allocated_resources.cpu_cores / 
                       workload.resource_requirements.cpu_cores)
        memory_ratio = min(1.0, workload.allocated_resources.memory_gb / 
                          workload.resource_requirements.memory_gb)
        gpu_ratio = min(1.0, workload.allocated_resources.gpu_count / 
                       max(1, workload.resource_requirements.gpu_count))
        
        # Overall resource satisfaction ratio
        resource_ratio = (cpu_ratio + memory_ratio + gpu_ratio) / 3
        
        # Simulate performance based on resource allocation
        base_accuracy = workload.min_accuracy
        accuracy = min(0.99, base_accuracy + (1 - base_accuracy) * resource_ratio * 0.8)
        
        base_throughput = workload.min_throughput
        throughput = base_throughput * resource_ratio * random.uniform(0.8, 1.2)
        
        base_latency = workload.max_latency_ms
        latency = base_latency * (2 - resource_ratio) * random.uniform(0.8, 1.2)
        
        # Resource utilization patterns
        cpu_util = min(0.95, cpu_ratio * random.uniform(0.6, 0.9))
        memory_util = min(0.95, memory_ratio * random.uniform(0.5, 0.8))
        gpu_util = min(0.95, gpu_ratio * random.uniform(0.7, 0.95)) if gpu_ratio > 0 else 0.0
        
        return PerformanceMetrics(
            accuracy=accuracy,
            throughput=throughput,
            latency_ms=latency,
            cpu_utilization=cpu_util,
            memory_utilization=memory_util,
            gpu_utilization=gpu_util
        )
    
    def update_workload_metrics(self, workload_id: str):
        """
        Update performance metrics for a running workload
        
        Args:
            workload_id (str): ID of workload to update
        """
        if workload_id not in self.active_workloads:
            return
        
        workload = self.active_workloads[workload_id]
        if workload.status == WorkloadStatus.RUNNING:
            workload.current_metrics = self.simulate_workload_performance(workload)
    
    def start_workload(self, workload: AIWorkload):
        """
        Start a workload
        
        Args:
            workload (AIWorkload): Workload to start
        """
        workload.status = WorkloadStatus.RUNNING
        workload.start_time = time.time()
        self.active_workloads[workload.id] = workload
    
    def complete_workload(self, workload_id: str):
        """
        Complete a workload
        
        Args:
            workload_id (str): ID of workload to complete
        """
        if workload_id in self.active_workloads:
            workload = self.active_workloads.pop(workload_id)
            workload.status = WorkloadStatus.COMPLETED
            workload.end_time = time.time()
            self.completed_workloads.append(workload)
    
    def get_active_workloads(self) -> List[AIWorkload]:
        """Get list of active workloads"""
        return list(self.active_workloads.values())
    
    def get_workload_by_id(self, workload_id: str) -> Optional[AIWorkload]:
        """Get workload by ID"""
        return self.active_workloads.get(workload_id)
    
    def _add_variance(self, base_value: float, variance: float) -> float:
        """Add random variance to a base value"""
        return base_value * (1 + random.uniform(-variance, variance))
    
    def generate_batch_workloads(self, count: int = 10) -> List[AIWorkload]:
        """
        Generate a batch of diverse workloads for testing
        
        Args:
            count (int): Number of workloads to generate
            
        Returns:
            List[AIWorkload]: List of generated workloads
        """
        workloads = []
        workload_types = list(WorkloadType)
        
        for _ in range(count):
            workload_type = random.choice(workload_types)
            workload = self.generate_workload(workload_type)
            workloads.append(workload)
        
        return workloads