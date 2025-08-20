"""
Main Datacenter Manager - Orchestrates AI datacenter resource management
"""
import time
import logging
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import Config
from workload_simulator import WorkloadSimulator, AIWorkload, WorkloadType, WorkloadStatus
from resource_allocator import ResourceAllocator
from performance_monitor import PerformanceMonitor
from optimization_engine import OptimizationEngine, OptimizationStrategy

class DatacenterManager:
    """Main orchestrator for AI datacenter resource management"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        Initialize the datacenter manager
        
        Args:
            config_file (str): Path to configuration file
        """
        # Load configuration
        self.config = Config(config_file)
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.workload_simulator = WorkloadSimulator(self.config.config)
        self.resource_allocator = ResourceAllocator(self.config.config)
        self.performance_monitor = PerformanceMonitor(self.config.config)
        self.optimization_engine = OptimizationEngine(self.config.config)
        
        # Runtime state
        self.is_running = False
        self.management_thread = None
        self.workload_queue: List[AIWorkload] = []
        
        # Statistics
        self.total_workloads_processed = 0
        self.total_optimizations_run = 0
        self.start_time = None
        
        self.logger.info("DatacenterManager initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging_config = self.config.get('logging', {})
        
        # Create logs directory if it doesn't exist
        import os
        os.makedirs('logs', exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, logging_config.get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logging_config.get('file', 'logs/datacenter_management.log')),
                logging.StreamHandler()
            ]
        )
    
    def start(self):
        """Start the datacenter management system"""
        if self.is_running:
            self.logger.warning("DatacenterManager is already running")
            return
        
        self.is_running = True
        self.start_time = time.time()
        
        # Start management thread
        self.management_thread = threading.Thread(target=self._management_loop, daemon=True)
        self.management_thread.start()
        
        self.logger.info("DatacenterManager started")
    
    def stop(self):
        """Stop the datacenter management system"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.management_thread:
            self.management_thread.join(timeout=5.0)
        
        self.logger.info("DatacenterManager stopped")
    
    def submit_workload(self, workload: AIWorkload) -> bool:
        """
        Submit a new workload for processing
        
        Args:
            workload (AIWorkload): Workload to submit
            
        Returns:
            bool: True if workload was accepted
        """
        # Try to allocate resources immediately
        if self.resource_allocator.allocate_resources(workload):
            self.workload_simulator.start_workload(workload)
            self.total_workloads_processed += 1
            self.logger.info(f"Workload {workload.name} started immediately")
            return True
        else:
            # Add to queue for later processing
            self.workload_queue.append(workload)
            self.logger.info(f"Workload {workload.name} queued (insufficient resources)")
            return True  # Accepted but queued
    
    def submit_batch_workloads(self, workloads: List[AIWorkload]) -> Dict[str, int]:
        """
        Submit a batch of workloads
        
        Args:
            workloads (List[AIWorkload]): List of workloads to submit
            
        Returns:
            Dict[str, int]: Statistics about submission results
        """
        started_count = 0
        queued_count = 0
        rejected_count = 0
        
        for workload in workloads:
            if self.submit_workload(workload):
                if workload.status == WorkloadStatus.RUNNING:
                    started_count += 1
                else:
                    queued_count += 1
            else:
                rejected_count += 1
        
        results = {
            'started': started_count,
            'queued': queued_count,
            'rejected': rejected_count,
            'total': len(workloads)
        }
        
        self.logger.info(f"Batch submission results: {results}")
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        
        Returns:
            Dict[str, Any]: System status information
        """
        active_workloads = self.workload_simulator.get_active_workloads()
        resource_utilization = self.resource_allocator.get_resource_utilization()
        available_resources = self.resource_allocator.get_available_resources()
        
        # Collect latest metrics
        if active_workloads:
            system_metrics = self.performance_monitor.collect_system_metrics(
                self.resource_allocator.datacenter_resources,
                self.workload_simulator
            )
        else:
            system_metrics = None
        
        uptime_hours = (time.time() - self.start_time) / 3600 if self.start_time else 0
        
        status = {
            'system_info': {
                'is_running': self.is_running,
                'uptime_hours': uptime_hours,
                'total_workloads_processed': self.total_workloads_processed,
                'total_optimizations_run': self.total_optimizations_run,
                'current_time': datetime.now().isoformat()
            },
            'workloads': {
                'active_count': len(active_workloads),
                'queued_count': len(self.workload_queue),
                'completed_count': len(self.workload_simulator.completed_workloads),
                'active_workloads': [
                    {
                        'id': w.id,
                        'name': w.name,
                        'type': w.workload_type.value,
                        'priority': w.priority,
                        'performance_score': self.optimization_engine._calculate_workload_score(w) * 100
                    } for w in active_workloads[:10]  # Limit to first 10
                ]
            },
            'resources': {
                'utilization': resource_utilization,
                'available': available_resources,
                'total_capacity': {
                    'cpu_cores': self.resource_allocator.datacenter_resources.total_cpu_cores,
                    'memory_gb': self.resource_allocator.datacenter_resources.total_memory_gb,
                    'gpu_count': self.resource_allocator.datacenter_resources.total_gpu_count,
                    'storage_tb': self.resource_allocator.datacenter_resources.total_storage_tb
                }
            },
            'performance': {
                'latest_system_metrics': system_metrics.__dict__ if system_metrics else None,
                'optimization_history': [
                    result.__dict__ for result in self.optimization_engine.get_optimization_history(5)
                ]
            }
        }
        
        return status
    
    def run_optimization(self) -> Dict[str, Any]:
        """
        Manually trigger optimization
        
        Returns:
            Dict[str, Any]: Optimization results
        """
        active_workloads = self.workload_simulator.get_active_workloads()
        
        if not active_workloads:
            return {
                'success': False,
                'message': 'No active workloads to optimize'
            }
        
        # Run optimization
        optimization_result = self.optimization_engine.optimize_workload_allocation(
            active_workloads, self.resource_allocator
        )
        
        self.total_optimizations_run += 1
        
        return {
            'success': True,
            'result': optimization_result.__dict__,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_demo_workloads(self, count: int = 5) -> List[AIWorkload]:
        """
        Create demonstration workloads for testing
        
        Args:
            count (int): Number of workloads to create
            
        Returns:
            List[AIWorkload]: Created workloads
        """
        workloads = self.workload_simulator.generate_batch_workloads(count)
        
        # Submit the workloads
        submission_results = self.submit_batch_workloads(workloads)
        
        self.logger.info(f"Created and submitted {count} demo workloads: {submission_results}")
        
        return workloads
    
    def _management_loop(self):
        """Main management loop running in background thread"""
        self.logger.info("Management loop started")
        
        while self.is_running:
            try:
                # Process queued workloads
                self._process_workload_queue()
                
                # Update workload metrics
                self._update_workload_metrics()
                
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check if optimization is needed
                self._check_and_run_optimization()
                
                # Complete finished workloads
                self._complete_finished_workloads()
                
                # Sleep for monitoring interval
                monitoring_config = self.config.get_monitoring_config()
                sleep_interval = monitoring_config.get('metrics_collection_interval_seconds', 30)
                time.sleep(sleep_interval)
                
            except Exception as e:
                self.logger.error(f"Error in management loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _process_workload_queue(self):
        """Process queued workloads"""
        if not self.workload_queue:
            return
        
        processed_workloads = []
        
        for workload in self.workload_queue[:]:  # Copy list to avoid modification during iteration
            if self.resource_allocator.allocate_resources(workload):
                self.workload_simulator.start_workload(workload)
                processed_workloads.append(workload)
                self.total_workloads_processed += 1
                self.logger.info(f"Started queued workload {workload.name}")
        
        # Remove processed workloads from queue
        for workload in processed_workloads:
            self.workload_queue.remove(workload)
    
    def _update_workload_metrics(self):
        """Update performance metrics for all active workloads"""
        active_workloads = self.workload_simulator.get_active_workloads()
        
        for workload in active_workloads:
            # Update simulation metrics
            self.workload_simulator.update_workload_metrics(workload.id)
            
            # Collect performance metrics
            self.performance_monitor.collect_workload_metrics(workload)
    
    def _collect_system_metrics(self):
        """Collect system-wide metrics"""
        if self.workload_simulator.get_active_workloads():
            self.performance_monitor.collect_system_metrics(
                self.resource_allocator.datacenter_resources,
                self.workload_simulator
            )
    
    def _check_and_run_optimization(self):
        """Check if optimization should run and execute if needed"""
        # Get current performance summary
        performance_summary = self.performance_monitor.get_performance_summary(hours=1)
        
        if self.optimization_engine.should_optimize(performance_summary):
            self.logger.info("Triggering automatic optimization")
            self.run_optimization()
    
    def _complete_finished_workloads(self):
        """Check for and complete finished workloads"""
        active_workloads = self.workload_simulator.get_active_workloads()
        current_time = time.time()
        
        for workload in active_workloads[:]:  # Copy to avoid modification during iteration
            if workload.start_time:
                # Check if workload should be completed (simplified - based on estimated duration)
                runtime_hours = (current_time - workload.start_time) / 3600
                
                # Add some randomness to completion time
                completion_threshold = workload.estimated_duration_hours * (1 + (hash(workload.id) % 20 - 10) / 100)
                
                if runtime_hours >= completion_threshold:
                    # Complete the workload
                    self.workload_simulator.complete_workload(workload.id)
                    self.resource_allocator.deallocate_resources(workload.id)
                    self.logger.info(f"Completed workload {workload.name} after {runtime_hours:.2f} hours")
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            hours (int): Number of hours to analyze
            
        Returns:
            Dict[str, Any]: Performance report
        """
        # Get performance summary from monitor
        performance_summary = self.performance_monitor.get_performance_summary(hours)
        
        # Add datacenter-specific metrics
        system_status = self.get_system_status()
        
        report = {
            'report_period_hours': hours,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_workloads_processed': self.total_workloads_processed,
                'total_optimizations_run': self.total_optimizations_run,
                'current_active_workloads': len(self.workload_simulator.get_active_workloads()),
                'current_queued_workloads': len(self.workload_queue),
                'system_uptime_hours': (time.time() - self.start_time) / 3600 if self.start_time else 0
            },
            'performance_metrics': performance_summary,
            'current_status': {
                'resource_utilization': system_status['resources']['utilization'],
                'resource_availability': system_status['resources']['available']
            },
            'optimization_history': [
                result.__dict__ for result in self.optimization_engine.get_optimization_history()
            ],
            'recommendations': self._generate_recommendations(performance_summary, system_status)
        }
        
        return report
    
    def _generate_recommendations(self, performance_summary: Dict, system_status: Dict) -> List[str]:
        """Generate system recommendations based on current metrics"""
        recommendations = []
        
        if 'system_performance' in performance_summary:
            sys_perf = performance_summary['system_performance']
            
            # Resource utilization recommendations
            if sys_perf.get('average_cpu_utilization', 0) > 0.9:
                recommendations.append("CPU utilization is very high. Consider adding more CPU resources or optimizing workload distribution.")
            
            if sys_perf.get('average_memory_utilization', 0) > 0.85:
                recommendations.append("Memory utilization is high. Monitor for potential memory bottlenecks.")
            
            if sys_perf.get('average_gpu_utilization', 0) > 0.95:
                recommendations.append("GPU utilization is at maximum. Consider adding more GPU resources for better performance.")
        
        # Workload recommendations
        if 'workload_performance' in performance_summary:
            workload_perf = performance_summary['workload_performance']
            avg_performance = workload_perf.get('average_performance_score', 100)
            
            if avg_performance < 70:
                recommendations.append("Average workload performance is below optimal. Consider running optimization or reviewing resource allocation.")
            
            if workload_perf.get('average_resource_efficiency', 1.0) < 0.7:
                recommendations.append("Resource efficiency is low. Review workload resource requirements and allocation strategy.")
        
        # Queue recommendations
        if len(self.workload_queue) > 5:
            recommendations.append(f"High number of queued workloads ({len(self.workload_queue)}). Consider scaling up resources.")
        
        # Optimization recommendations
        if self.total_optimizations_run == 0:
            recommendations.append("No optimizations have been run. Consider enabling automatic optimization or running manual optimization.")
        
        if not recommendations:
            recommendations.append("System is operating within normal parameters.")
        
        return recommendations

# Utility functions for easy CLI usage
def create_demo_system(workload_count: int = 10) -> DatacenterManager:
    """
    Create a demo datacenter system with sample workloads
    
    Args:
        workload_count (int): Number of demo workloads to create
        
    Returns:
        DatacenterManager: Configured and running datacenter manager
    """
    # Initialize system
    manager = DatacenterManager()
    manager.start()
    
    # Create demo workloads
    manager.create_demo_workloads(workload_count)
    
    return manager

def run_simulation(duration_minutes: int = 10, workload_count: int = 15) -> Dict[str, Any]:
    """
    Run a complete simulation for demonstration purposes
    
    Args:
        duration_minutes (int): How long to run the simulation
        workload_count (int): Number of workloads to process
        
    Returns:
        Dict[str, Any]: Simulation results
    """
    print(f"Starting AI Datacenter Resource Management Simulation")
    print(f"Duration: {duration_minutes} minutes, Workloads: {workload_count}")
    print("-" * 60)
    
    # Create and start system
    manager = create_demo_system(workload_count)
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    try:
        # Let system run
        while time.time() < end_time:
            # Print status periodically
            status = manager.get_system_status()
            print(f"Time: {time.time() - start_time:.1f}s | "
                  f"Active: {status['workloads']['active_count']} | "
                  f"Queued: {status['workloads']['queued_count']} | "
                  f"Completed: {status['workloads']['completed_count']} | "
                  f"CPU: {status['resources']['utilization']['cpu_utilization']:.1%}")
            
            time.sleep(30)  # Print every 30 seconds
        
        # Generate final report
        final_report = manager.generate_performance_report(hours=24)
        
        print("\n" + "=" * 60)
        print("SIMULATION COMPLETED")
        print("=" * 60)
        print(f"Total workloads processed: {final_report['summary']['total_workloads_processed']}")
        print(f"Total optimizations run: {final_report['summary']['total_optimizations_run']}")
        print(f"Final active workloads: {final_report['summary']['current_active_workloads']}")
        
        return final_report
    
    finally:
        manager.stop()
        print("System stopped.")

if __name__ == "__main__":
    # Run a demo simulation
    run_simulation(duration_minutes=5, workload_count=10)