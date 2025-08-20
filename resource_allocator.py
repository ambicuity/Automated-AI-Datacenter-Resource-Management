"""
Resource Allocator for AI Datacenter Management System
"""
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from workload_simulator import AIWorkload, ResourceRequirements, WorkloadStatus

@dataclass
class DatacenterResources:
    """Represents the total resources available in the datacenter"""
    total_cpu_cores: int
    total_memory_gb: float
    total_gpu_count: int
    total_storage_tb: float
    
    # Current allocations
    allocated_cpu_cores: int = 0
    allocated_memory_gb: float = 0.0
    allocated_gpu_count: int = 0
    allocated_storage_gb: float = 0.0
    
    @property
    def available_cpu_cores(self) -> int:
        """Get available CPU cores"""
        return self.total_cpu_cores - self.allocated_cpu_cores
    
    @property
    def available_memory_gb(self) -> float:
        """Get available memory in GB"""
        return self.total_memory_gb - self.allocated_memory_gb
    
    @property
    def available_gpu_count(self) -> int:
        """Get available GPU count"""
        return self.total_gpu_count - self.allocated_gpu_count
    
    @property
    def available_storage_gb(self) -> float:
        """Get available storage in GB"""
        return (self.total_storage_tb * 1024) - self.allocated_storage_gb
    
    @property
    def cpu_utilization(self) -> float:
        """Get CPU utilization ratio"""
        return self.allocated_cpu_cores / self.total_cpu_cores if self.total_cpu_cores > 0 else 0.0
    
    @property
    def memory_utilization(self) -> float:
        """Get memory utilization ratio"""
        return self.allocated_memory_gb / self.total_memory_gb if self.total_memory_gb > 0 else 0.0
    
    @property
    def gpu_utilization(self) -> float:
        """Get GPU utilization ratio"""
        return self.allocated_gpu_count / self.total_gpu_count if self.total_gpu_count > 0 else 0.0

class ResourceAllocator:
    """Manages resource allocation for AI workloads in the datacenter"""
    
    def __init__(self, config: Dict):
        """
        Initialize resource allocator
        
        Args:
            config (Dict): Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize datacenter resources from config
        datacenter_config = config.get('datacenter', {})
        self.datacenter_resources = DatacenterResources(
            total_cpu_cores=datacenter_config.get('total_cpu_cores', 100),
            total_memory_gb=datacenter_config.get('total_memory_gb', 512),
            total_gpu_count=datacenter_config.get('total_gpu_count', 10),
            total_storage_tb=datacenter_config.get('total_storage_tb', 10)
        )
        
        # Track workload allocations
        self.workload_allocations: Dict[str, ResourceRequirements] = {}
        
        self.logger.info(f"ResourceAllocator initialized with {self.datacenter_resources.total_cpu_cores} "
                        f"CPU cores, {self.datacenter_resources.total_memory_gb}GB memory, "
                        f"{self.datacenter_resources.total_gpu_count} GPUs")
    
    def can_allocate_resources(self, requirements: ResourceRequirements) -> bool:
        """
        Check if requested resources can be allocated
        
        Args:
            requirements (ResourceRequirements): Resource requirements to check
            
        Returns:
            bool: True if resources can be allocated
        """
        return (
            requirements.cpu_cores <= self.datacenter_resources.available_cpu_cores and
            requirements.memory_gb <= self.datacenter_resources.available_memory_gb and
            requirements.gpu_count <= self.datacenter_resources.available_gpu_count and
            requirements.storage_gb <= self.datacenter_resources.available_storage_gb
        )
    
    def allocate_resources(self, workload: AIWorkload) -> bool:
        """
        Allocate resources to a workload
        
        Args:
            workload (AIWorkload): Workload requesting resources
            
        Returns:
            bool: True if allocation successful
        """
        if not self.can_allocate_resources(workload.resource_requirements):
            self.logger.warning(f"Cannot allocate resources for workload {workload.id}: "
                              f"Insufficient resources available")
            return False
        
        # Allocate exact requested resources
        allocated_resources = ResourceRequirements(
            cpu_cores=workload.resource_requirements.cpu_cores,
            memory_gb=workload.resource_requirements.memory_gb,
            gpu_count=workload.resource_requirements.gpu_count,
            storage_gb=workload.resource_requirements.storage_gb,
            network_bandwidth_mbps=workload.resource_requirements.network_bandwidth_mbps
        )
        
        # Update datacenter resource allocation
        self.datacenter_resources.allocated_cpu_cores += allocated_resources.cpu_cores
        self.datacenter_resources.allocated_memory_gb += allocated_resources.memory_gb
        self.datacenter_resources.allocated_gpu_count += allocated_resources.gpu_count
        self.datacenter_resources.allocated_storage_gb += allocated_resources.storage_gb
        
        # Track allocation
        self.workload_allocations[workload.id] = allocated_resources
        workload.allocated_resources = allocated_resources
        
        self.logger.info(f"Allocated resources to workload {workload.id}: "
                        f"{allocated_resources.cpu_cores} CPU cores, "
                        f"{allocated_resources.memory_gb}GB memory, "
                        f"{allocated_resources.gpu_count} GPUs")
        
        return True
    
    def deallocate_resources(self, workload_id: str) -> bool:
        """
        Deallocate resources from a completed or cancelled workload
        
        Args:
            workload_id (str): ID of workload to deallocate
            
        Returns:
            bool: True if deallocation successful
        """
        if workload_id not in self.workload_allocations:
            self.logger.warning(f"No allocation found for workload {workload_id}")
            return False
        
        allocated_resources = self.workload_allocations.pop(workload_id)
        
        # Update datacenter resource allocation
        self.datacenter_resources.allocated_cpu_cores -= allocated_resources.cpu_cores
        self.datacenter_resources.allocated_memory_gb -= allocated_resources.memory_gb
        self.datacenter_resources.allocated_gpu_count -= allocated_resources.gpu_count
        self.datacenter_resources.allocated_storage_gb -= allocated_resources.storage_gb
        
        self.logger.info(f"Deallocated resources from workload {workload_id}: "
                        f"{allocated_resources.cpu_cores} CPU cores, "
                        f"{allocated_resources.memory_gb}GB memory, "
                        f"{allocated_resources.gpu_count} GPUs")
        
        return True
    
    def optimize_allocation(self, workload: AIWorkload) -> Optional[ResourceRequirements]:
        """
        Optimize resource allocation based on performance requirements and availability
        
        Args:
            workload (AIWorkload): Workload to optimize allocation for
            
        Returns:
            Optional[ResourceRequirements]: Optimized resource allocation or None if impossible
        """
        # Start with minimum viable allocation
        min_cpu = max(1, workload.resource_requirements.cpu_cores // 2)
        min_memory = max(1.0, workload.resource_requirements.memory_gb * 0.5)
        min_gpu = workload.resource_requirements.gpu_count
        min_storage = max(1.0, workload.resource_requirements.storage_gb * 0.8)
        
        # Try to find optimal allocation within available resources
        optimal_cpu = min(workload.resource_requirements.cpu_cores, 
                         self.datacenter_resources.available_cpu_cores)
        optimal_memory = min(workload.resource_requirements.memory_gb,
                           self.datacenter_resources.available_memory_gb)
        optimal_gpu = min(workload.resource_requirements.gpu_count,
                         self.datacenter_resources.available_gpu_count)
        optimal_storage = min(workload.resource_requirements.storage_gb,
                            self.datacenter_resources.available_storage_gb)
        
        # Check if minimum requirements can be met
        if (min_cpu > self.datacenter_resources.available_cpu_cores or
            min_memory > self.datacenter_resources.available_memory_gb or
            min_gpu > self.datacenter_resources.available_gpu_count or
            min_storage > self.datacenter_resources.available_storage_gb):
            return None
        
        return ResourceRequirements(
            cpu_cores=optimal_cpu,
            memory_gb=optimal_memory,
            gpu_count=optimal_gpu,
            storage_gb=optimal_storage,
            network_bandwidth_mbps=workload.resource_requirements.network_bandwidth_mbps
        )
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """
        Get current resource utilization metrics
        
        Returns:
            Dict[str, float]: Resource utilization percentages
        """
        return {
            'cpu_utilization': self.datacenter_resources.cpu_utilization,
            'memory_utilization': self.datacenter_resources.memory_utilization,
            'gpu_utilization': self.datacenter_resources.gpu_utilization,
            'storage_utilization': (self.datacenter_resources.allocated_storage_gb / 
                                   (self.datacenter_resources.total_storage_tb * 1024))
        }
    
    def get_available_resources(self) -> Dict[str, float]:
        """
        Get current available resources
        
        Returns:
            Dict[str, float]: Available resources
        """
        return {
            'available_cpu_cores': self.datacenter_resources.available_cpu_cores,
            'available_memory_gb': self.datacenter_resources.available_memory_gb,
            'available_gpu_count': self.datacenter_resources.available_gpu_count,
            'available_storage_gb': self.datacenter_resources.available_storage_gb
        }
    
    def allocate_batch_workloads(self, workloads: List[AIWorkload], 
                                strategy: str = "priority") -> Tuple[List[AIWorkload], List[AIWorkload]]:
        """
        Allocate resources to a batch of workloads using specified strategy
        
        Args:
            workloads (List[AIWorkload]): List of workloads to allocate
            strategy (str): Allocation strategy ("priority", "first_fit", "best_fit")
            
        Returns:
            Tuple[List[AIWorkload], List[AIWorkload]]: (allocated_workloads, failed_workloads)
        """
        allocated_workloads = []
        failed_workloads = []
        
        # Sort workloads based on strategy
        if strategy == "priority":
            sorted_workloads = sorted(workloads, key=lambda w: w.priority, reverse=True)
        elif strategy == "first_fit":
            sorted_workloads = workloads
        elif strategy == "best_fit":
            # Sort by total resource requirements (ascending)
            sorted_workloads = sorted(workloads, 
                key=lambda w: (w.resource_requirements.cpu_cores + 
                              w.resource_requirements.memory_gb + 
                              w.resource_requirements.gpu_count))
        else:
            sorted_workloads = workloads
        
        for workload in sorted_workloads:
            if self.allocate_resources(workload):
                allocated_workloads.append(workload)
            else:
                # Try optimized allocation
                optimized_resources = self.optimize_allocation(workload)
                if optimized_resources:
                    workload.resource_requirements = optimized_resources
                    if self.allocate_resources(workload):
                        allocated_workloads.append(workload)
                        self.logger.info(f"Allocated optimized resources to workload {workload.id}")
                    else:
                        failed_workloads.append(workload)
                else:
                    failed_workloads.append(workload)
        
        self.logger.info(f"Batch allocation complete: {len(allocated_workloads)} allocated, "
                        f"{len(failed_workloads)} failed")
        
        return allocated_workloads, failed_workloads