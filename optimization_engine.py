"""
Optimization Engine for AI Datacenter Resource Management
"""
import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from workload_simulator import AIWorkload, WorkloadStatus, WorkloadType
from resource_allocator import ResourceAllocator

class OptimizationStrategy(Enum):
    """Available optimization strategies"""
    WEIGHTED_SCORE = "weighted_score"
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    PERFORMANCE_DRIVEN = "performance_driven"
    RESOURCE_BALANCED = "resource_balanced"

@dataclass
class OptimizationResult:
    """Results from an optimization run"""
    strategy_used: str
    workloads_optimized: int
    performance_improvement: float
    resource_efficiency_improvement: float
    reallocation_count: int
    optimization_time_seconds: float
    recommendations: List[str]

class OptimizationEngine:
    """Optimizes resource allocation and system performance"""
    
    def __init__(self, config: Dict):
        """
        Initialize optimization engine
        
        Args:
            config (Dict): Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Optimization configuration
        opt_config = config.get('optimization', {})
        self.strategy = OptimizationStrategy(opt_config.get('algorithm', 'weighted_score'))
        self.reallocation_interval = opt_config.get('reallocation_interval_minutes', 15) * 60
        self.performance_threshold = opt_config.get('performance_threshold', 0.85)
        self.resource_utilization_target = opt_config.get('resource_utilization_target', 0.80)
        self.enable_auto_scaling = opt_config.get('enable_auto_scaling', True)
        
        # Track optimization history
        self.optimization_history: List[OptimizationResult] = []
        self.last_optimization_time = time.time()
        
        self.logger.info(f"OptimizationEngine initialized with strategy: {self.strategy.value}")
    
    def should_optimize(self, current_metrics: Dict[str, Any]) -> bool:
        """
        Determine if optimization should be triggered
        
        Args:
            current_metrics (Dict[str, Any]): Current system metrics
            
        Returns:
            bool: True if optimization should run
        """
        # Time-based trigger
        if time.time() - self.last_optimization_time > self.reallocation_interval:
            return True
        
        # Performance-based trigger
        if 'system_performance' in current_metrics:
            sys_metrics = current_metrics['system_performance']
            
            # Trigger if any resource is over-utilized
            if (sys_metrics.get('average_cpu_utilization', 0) > 0.9 or
                sys_metrics.get('average_memory_utilization', 0) > 0.85 or
                sys_metrics.get('average_gpu_utilization', 0) > 0.95):
                self.logger.info("Optimization triggered due to high resource utilization")
                return True
        
        # Workload performance trigger
        if 'workload_performance' in current_metrics:
            workload_metrics = current_metrics['workload_performance']
            avg_performance = workload_metrics.get('average_performance_score', 100)
            
            if avg_performance < self.performance_threshold * 100:
                self.logger.info(f"Optimization triggered due to low performance: {avg_performance:.1f}")
                return True
        
        return False
    
    def optimize_workload_allocation(self, workloads: List[AIWorkload], 
                                   resource_allocator: ResourceAllocator) -> OptimizationResult:
        """
        Optimize resource allocation for active workloads
        
        Args:
            workloads (List[AIWorkload]): List of active workloads
            resource_allocator (ResourceAllocator): Resource allocator instance
            
        Returns:
            OptimizationResult: Results of optimization
        """
        start_time = time.time()
        self.logger.info(f"Starting optimization for {len(workloads)} workloads using {self.strategy.value}")
        
        # Store initial performance metrics
        initial_performance = self._calculate_system_performance(workloads)
        initial_efficiency = self._calculate_resource_efficiency(workloads, resource_allocator)
        
        recommendations = []
        reallocation_count = 0
        
        if self.strategy == OptimizationStrategy.WEIGHTED_SCORE:
            reallocation_count = self._optimize_weighted_score(workloads, resource_allocator, recommendations)
        elif self.strategy == OptimizationStrategy.PRIORITY_BASED:
            reallocation_count = self._optimize_priority_based(workloads, resource_allocator, recommendations)
        elif self.strategy == OptimizationStrategy.PERFORMANCE_DRIVEN:
            reallocation_count = self._optimize_performance_driven(workloads, resource_allocator, recommendations)
        elif self.strategy == OptimizationStrategy.RESOURCE_BALANCED:
            reallocation_count = self._optimize_resource_balanced(workloads, resource_allocator, recommendations)
        else:
            # Default to weighted score
            reallocation_count = self._optimize_weighted_score(workloads, resource_allocator, recommendations)
        
        # Calculate improvement
        final_performance = self._calculate_system_performance(workloads)
        final_efficiency = self._calculate_resource_efficiency(workloads, resource_allocator)
        
        performance_improvement = final_performance - initial_performance
        efficiency_improvement = final_efficiency - initial_efficiency
        
        optimization_time = time.time() - start_time
        self.last_optimization_time = time.time()
        
        result = OptimizationResult(
            strategy_used=self.strategy.value,
            workloads_optimized=len(workloads),
            performance_improvement=performance_improvement,
            resource_efficiency_improvement=efficiency_improvement,
            reallocation_count=reallocation_count,
            optimization_time_seconds=optimization_time,
            recommendations=recommendations
        )
        
        self.optimization_history.append(result)
        
        self.logger.info(f"Optimization completed: {reallocation_count} reallocations, "
                        f"{performance_improvement:.3f} performance improvement, "
                        f"{efficiency_improvement:.3f} efficiency improvement")
        
        return result
    
    def _optimize_weighted_score(self, workloads: List[AIWorkload], 
                                resource_allocator: ResourceAllocator,
                                recommendations: List[str]) -> int:
        """
        Optimize using weighted performance score approach
        
        Args:
            workloads (List[AIWorkload]): Workloads to optimize
            resource_allocator (ResourceAllocator): Resource allocator
            recommendations (List[str]): List to append recommendations to
            
        Returns:
            int: Number of reallocations performed
        """
        reallocation_count = 0
        
        # Calculate performance scores for all workloads
        workload_scores = []
        for workload in workloads:
            if workload.current_metrics:
                score = self._calculate_workload_score(workload)
                workload_scores.append((workload, score))
        
        # Sort by score (lowest first - these need optimization most)
        workload_scores.sort(key=lambda x: x[1])
        
        # Try to improve low-performing workloads
        available_resources = resource_allocator.get_available_resources()
        
        for workload, score in workload_scores:
            if score < self.performance_threshold:
                # Try to allocate additional resources
                additional_resources = self._calculate_additional_resources_needed(workload, available_resources)
                
                if additional_resources:
                    # Simulate deallocation and reallocation
                    resource_allocator.deallocate_resources(workload.id)
                    
                    # Update resource requirements
                    workload.resource_requirements.cpu_cores += additional_resources.get('cpu', 0)
                    workload.resource_requirements.memory_gb += additional_resources.get('memory', 0)
                    workload.resource_requirements.gpu_count += additional_resources.get('gpu', 0)
                    
                    # Try to reallocate
                    if resource_allocator.allocate_resources(workload):
                        reallocation_count += 1
                        recommendations.append(f"Increased resources for workload {workload.name} to improve performance")
                    else:
                        # Revert changes if allocation failed
                        workload.resource_requirements.cpu_cores -= additional_resources.get('cpu', 0)
                        workload.resource_requirements.memory_gb -= additional_resources.get('memory', 0)
                        workload.resource_requirements.gpu_count -= additional_resources.get('gpu', 0)
                        resource_allocator.allocate_resources(workload)  # Restore original allocation
                        
                        recommendations.append(f"Could not allocate additional resources for workload {workload.name}")
        
        return reallocation_count
    
    def _optimize_priority_based(self, workloads: List[AIWorkload], 
                                resource_allocator: ResourceAllocator,
                                recommendations: List[str]) -> int:
        """
        Optimize based on workload priorities
        
        Args:
            workloads (List[AIWorkload]): Workloads to optimize
            resource_allocator (ResourceAllocator): Resource allocator
            recommendations (List[str]): List to append recommendations to
            
        Returns:
            int: Number of reallocations performed
        """
        reallocation_count = 0
        
        # Sort by priority (highest first)
        sorted_workloads = sorted(workloads, key=lambda w: w.priority, reverse=True)
        
        # Reallocate resources to prioritize high-priority workloads
        for i, workload in enumerate(sorted_workloads):
            if workload.priority >= 4:  # High priority workloads
                # Check if this workload is underperforming
                if workload.current_metrics:
                    score = self._calculate_workload_score(workload)
                    if score < self.performance_threshold:
                        # Try to steal resources from lower priority workloads
                        for j in range(len(sorted_workloads) - 1, i, -1):
                            low_priority_workload = sorted_workloads[j]
                            if low_priority_workload.priority <= 2:
                                # Try to transfer some resources
                                if self._transfer_resources(low_priority_workload, workload, resource_allocator):
                                    reallocation_count += 2  # One deallocation, one allocation
                                    recommendations.append(
                                        f"Transferred resources from {low_priority_workload.name} "
                                        f"to high-priority {workload.name}"
                                    )
                                    break
        
        return reallocation_count
    
    def _optimize_performance_driven(self, workloads: List[AIWorkload], 
                                    resource_allocator: ResourceAllocator,
                                    recommendations: List[str]) -> int:
        """
        Optimize to maximize overall system performance
        
        Args:
            workloads (List[AIWorkload]): Workloads to optimize
            resource_allocator: Resource allocator
            recommendations: List to append recommendations to
            
        Returns:
            int: Number of reallocations performed
        """
        reallocation_count = 0
        
        # Find workloads that would benefit most from additional resources
        performance_gains = []
        
        for workload in workloads:
            if workload.current_metrics:
                current_score = self._calculate_workload_score(workload)
                potential_gain = self._estimate_performance_gain(workload, resource_allocator)
                performance_gains.append((workload, current_score, potential_gain))
        
        # Sort by potential performance gain (highest first)
        performance_gains.sort(key=lambda x: x[2], reverse=True)
        
        # Allocate additional resources to workloads with highest potential gains
        for workload, current_score, potential_gain in performance_gains:
            if potential_gain > 0.1 and current_score < 0.9:  # Significant improvement possible
                if self._try_resource_upgrade(workload, resource_allocator):
                    reallocation_count += 1
                    recommendations.append(
                        f"Upgraded resources for {workload.name} - estimated {potential_gain:.2f} performance gain"
                    )
        
        return reallocation_count
    
    def _optimize_resource_balanced(self, workloads: List[AIWorkload], 
                                   resource_allocator: ResourceAllocator,
                                   recommendations: List[str]) -> int:
        """
        Balance resource utilization across the datacenter
        
        Args:
            workloads: Workloads to optimize
            resource_allocator: Resource allocator
            recommendations: List to append recommendations to
            
        Returns:
            int: Number of reallocations performed
        """
        reallocation_count = 0
        
        utilization = resource_allocator.get_resource_utilization()
        target = self.resource_utilization_target
        
        # If any resource is significantly over or under utilized, rebalance
        if (utilization['cpu_utilization'] > target + 0.1 or 
            utilization['memory_utilization'] > target + 0.1 or
            utilization['gpu_utilization'] > target + 0.1):
            
            # Find workloads that can be downsized
            for workload in workloads:
                if workload.current_metrics:
                    # Check if workload is using more resources than needed for its performance
                    if (workload.current_metrics.cpu_utilization < 0.5 and
                        workload.allocated_resources.cpu_cores > 2):
                        
                        # Try to reduce CPU allocation
                        original_cpu = workload.allocated_resources.cpu_cores
                        reduced_cpu = max(2, int(original_cpu * 0.8))
                        
                        if self._try_resource_reduction(workload, {'cpu_cores': reduced_cpu}, resource_allocator):
                            reallocation_count += 1
                            recommendations.append(
                                f"Reduced CPU allocation for {workload.name} from {original_cpu} to {reduced_cpu} cores"
                            )
        
        return reallocation_count
    
    def _calculate_system_performance(self, workloads: List[AIWorkload]) -> float:
        """Calculate overall system performance score"""
        if not workloads:
            return 0.0
        
        total_score = 0.0
        for workload in workloads:
            if workload.current_metrics:
                score = self._calculate_workload_score(workload)
                total_score += score
        
        return total_score / len(workloads)
    
    def _calculate_resource_efficiency(self, workloads: List[AIWorkload], 
                                     resource_allocator: ResourceAllocator) -> float:
        """Calculate overall resource efficiency"""
        utilization = resource_allocator.get_resource_utilization()
        avg_utilization = (utilization['cpu_utilization'] + 
                          utilization['memory_utilization'] + 
                          utilization['gpu_utilization']) / 3
        
        performance = self._calculate_system_performance(workloads)
        
        if avg_utilization > 0:
            return performance / avg_utilization
        return 0.0
    
    def _calculate_workload_score(self, workload: AIWorkload) -> float:
        """Calculate normalized performance score for a workload"""
        if not workload.current_metrics:
            return 0.0
        
        # Get workload type configuration
        workload_config = self.config.get('workloads', {}).get(workload.workload_type.value, {})
        performance_weight = workload_config.get('performance_weight', 0.7)
        accuracy_weight = workload_config.get('accuracy_weight', 0.3)
        
        # Normalize metrics
        accuracy_score = min(1.0, workload.current_metrics.accuracy / workload.min_accuracy)
        throughput_score = min(1.0, workload.current_metrics.throughput / workload.min_throughput)
        latency_score = min(1.0, workload.max_latency_ms / max(1.0, workload.current_metrics.latency_ms))
        
        performance_score = (throughput_score + latency_score) / 2
        
        return (performance_score * performance_weight) + (accuracy_score * accuracy_weight)
    
    def _calculate_additional_resources_needed(self, workload: AIWorkload, 
                                             available_resources: Dict) -> Optional[Dict]:
        """Calculate additional resources needed to improve performance"""
        if not workload.current_metrics:
            return None
        
        additional = {}
        
        # Check if CPU utilization is high but performance is low
        if (workload.current_metrics.cpu_utilization > 0.8 and
            workload.current_metrics.throughput < workload.min_throughput and
            available_resources['available_cpu_cores'] >= 2):
            additional['cpu'] = min(2, int(available_resources['available_cpu_cores'] * 0.1))
        
        # Check if memory utilization is high
        if (workload.current_metrics.memory_utilization > 0.8 and
            available_resources['available_memory_gb'] >= 4):
            additional['memory'] = min(4, available_resources['available_memory_gb'] * 0.1)
        
        # Check if GPU could help
        if (workload.workload_type == WorkloadType.TRAINING and
            workload.allocated_resources.gpu_count == 0 and
            available_resources['available_gpu_count'] >= 1):
            additional['gpu'] = 1
        
        return additional if additional else None
    
    def _try_resource_upgrade(self, workload: AIWorkload, resource_allocator: ResourceAllocator) -> bool:
        """Try to upgrade resources for a workload"""
        available = resource_allocator.get_available_resources()
        
        # Try to add one more CPU core
        if available['available_cpu_cores'] >= 1:
            resource_allocator.deallocate_resources(workload.id)
            workload.resource_requirements.cpu_cores += 1
            
            if resource_allocator.allocate_resources(workload):
                return True
            else:
                # Revert
                workload.resource_requirements.cpu_cores -= 1
                resource_allocator.allocate_resources(workload)
        
        return False
    
    def _try_resource_reduction(self, workload: AIWorkload, new_requirements: Dict,
                               resource_allocator: ResourceAllocator) -> bool:
        """Try to reduce resources for a workload"""
        original_requirements = {
            'cpu_cores': workload.resource_requirements.cpu_cores,
            'memory_gb': workload.resource_requirements.memory_gb,
            'gpu_count': workload.resource_requirements.gpu_count
        }
        
        resource_allocator.deallocate_resources(workload.id)
        
        # Apply new requirements
        for key, value in new_requirements.items():
            setattr(workload.resource_requirements, key, value)
        
        if resource_allocator.allocate_resources(workload):
            return True
        else:
            # Revert
            for key, value in original_requirements.items():
                setattr(workload.resource_requirements, key, value)
            resource_allocator.allocate_resources(workload)
            return False
    
    def _transfer_resources(self, from_workload: AIWorkload, to_workload: AIWorkload,
                           resource_allocator: ResourceAllocator) -> bool:
        """Transfer resources from one workload to another"""
        # Simple implementation: reduce from_workload CPU by 1, increase to_workload CPU by 1
        if from_workload.allocated_resources.cpu_cores <= 2:
            return False  # Don't reduce below minimum
        
        # Deallocate both
        resource_allocator.deallocate_resources(from_workload.id)
        resource_allocator.deallocate_resources(to_workload.id)
        
        # Modify requirements
        from_workload.resource_requirements.cpu_cores -= 1
        to_workload.resource_requirements.cpu_cores += 1
        
        # Try to reallocate both
        from_success = resource_allocator.allocate_resources(from_workload)
        to_success = resource_allocator.allocate_resources(to_workload)
        
        if from_success and to_success:
            return True
        else:
            # Revert changes
            from_workload.resource_requirements.cpu_cores += 1
            to_workload.resource_requirements.cpu_cores -= 1
            resource_allocator.allocate_resources(from_workload)
            resource_allocator.allocate_resources(to_workload)
            return False
    
    def _estimate_performance_gain(self, workload: AIWorkload, resource_allocator: ResourceAllocator) -> float:
        """Estimate potential performance gain from additional resources"""
        if not workload.current_metrics:
            return 0.0
        
        current_score = self._calculate_workload_score(workload)
        
        # Simple estimation: if resource utilization is high, adding resources should help
        avg_utilization = (workload.current_metrics.cpu_utilization +
                          workload.current_metrics.memory_utilization +
                          workload.current_metrics.gpu_utilization) / 3
        
        if avg_utilization > 0.8:
            return min(0.3, (1.0 - current_score) * 0.5)  # Up to 30% improvement
        
        return 0.0
    
    def get_optimization_history(self, limit: int = 10) -> List[OptimizationResult]:
        """Get recent optimization history"""
        return self.optimization_history[-limit:]