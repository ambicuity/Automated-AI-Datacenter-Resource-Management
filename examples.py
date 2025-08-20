#!/usr/bin/env python3
"""
Example usage scenarios for AI Datacenter Resource Management System
"""
import time
import json
from datacenter_manager import DatacenterManager
from workload_simulator import WorkloadType, AIWorkload, ResourceRequirements

def scenario_peak_load_handling():
    """
    Scenario 1: Demonstrate peak load handling with intelligent queuing
    """
    print("🌊 SCENARIO 1: Peak Load Handling")
    print("=" * 60)
    
    manager = DatacenterManager()
    manager.start()
    
    try:
        # Create a burst of high-priority training workloads
        print("Creating burst of 15 high-priority training workloads...")
        training_workloads = []
        for i in range(15):
            workload = manager.workload_simulator.generate_workload(WorkloadType.TRAINING)
            workload.priority = 5  # Maximum priority
            workload.name = f"priority_training_{i+1}"
            training_workloads.append(workload)
        
        # Submit all workloads at once
        results = manager.submit_batch_workloads(training_workloads)
        print(f"Submission results: {results}")
        
        # Monitor system for 60 seconds
        print("\n📊 Monitoring system response...")
        for i in range(12):  # 60 seconds / 5 second intervals
            status = manager.get_system_status()
            workloads = status['workloads']
            resources = status['resources']['utilization']
            
            print(f"Time {i*5:2d}s: Active={workloads['active_count']:2d}, "
                  f"Queued={workloads['queued_count']:2d}, "
                  f"CPU={resources['cpu_utilization']:5.1%}, "
                  f"GPU={resources['gpu_utilization']:5.1%}")
            
            time.sleep(5)
        
        # Trigger optimization
        print("\n⚙️ Triggering optimization...")
        opt_result = manager.run_optimization()
        if opt_result['success']:
            result = opt_result['result']
            print(f"Optimization: {result['reallocation_count']} reallocations, "
                  f"{result['performance_improvement']:+.3f} performance gain")
        
        # Final status
        final_status = manager.get_system_status()
        print(f"\n📈 Final Status:")
        print(f"  Total Processed: {final_status['system_info']['total_workloads_processed']}")
        print(f"  Active: {final_status['workloads']['active_count']}")
        print(f"  Queued: {final_status['workloads']['queued_count']}")
        print(f"  Completed: {final_status['workloads']['completed_count']}")
        
    finally:
        manager.stop()
        print("✅ Scenario 1 completed\n")

def scenario_mixed_workload_optimization():
    """
    Scenario 2: Mixed workload types with different performance requirements
    """
    print("🎯 SCENARIO 2: Mixed Workload Optimization")
    print("=" * 60)
    
    manager = DatacenterManager()
    manager.start()
    
    try:
        # Create diverse workload mix
        workloads = []
        
        # High-throughput inference workloads
        for i in range(8):
            workload = manager.workload_simulator.generate_workload(WorkloadType.INFERENCE)
            workload.priority = 4
            workload.min_throughput = 100.0  # High throughput requirement
            workload.max_latency_ms = 50.0   # Low latency requirement
            workload.name = f"realtime_inference_{i+1}"
            workloads.append(workload)
        
        # Long-running training workloads
        for i in range(3):
            workload = manager.workload_simulator.generate_workload(WorkloadType.TRAINING)
            workload.priority = 3
            workload.min_accuracy = 0.98     # High accuracy requirement
            workload.estimated_duration_hours = 12.0
            workload.name = f"model_training_{i+1}"
            workloads.append(workload)
        
        # Batch data processing
        for i in range(5):
            workload = manager.workload_simulator.generate_workload(WorkloadType.DATA_PROCESSING)
            workload.priority = 2
            workload.name = f"batch_processing_{i+1}"
            workloads.append(workload)
        
        # Submit mixed workloads
        print(f"Submitting {len(workloads)} mixed workloads...")
        results = manager.submit_batch_workloads(workloads)
        print(f"Results: {results}")
        
        # Let system run and collect metrics
        print("\n📊 Monitoring mixed workload performance...")
        for i in range(8):  # 40 seconds monitoring
            status = manager.get_system_status()
            
            # Calculate workload type distribution
            active_workloads = status['workloads']['active_workloads']
            type_counts = {}
            avg_performance = 0
            
            for wl in active_workloads:
                wl_type = wl['type']
                type_counts[wl_type] = type_counts.get(wl_type, 0) + 1
                avg_performance += wl['performance_score']
            
            if active_workloads:
                avg_performance /= len(active_workloads)
            
            print(f"Time {i*5:2d}s: Training={type_counts.get('training', 0)}, "
                  f"Inference={type_counts.get('inference', 0)}, "
                  f"DataProc={type_counts.get('data_processing', 0)}, "
                  f"AvgPerf={avg_performance:.1f}")
            
            time.sleep(5)
        
        # Generate performance report
        print("\n📈 Generating performance report...")
        report = manager.generate_performance_report(hours=1)
        
        # Display key metrics
        if 'workload_performance' in report['performance_metrics']:
            wl_perf = report['performance_metrics']['workload_performance']
            print(f"Average Performance Score: {wl_perf.get('average_performance_score', 0):.1f}/100")
            print(f"Average Resource Efficiency: {wl_perf.get('average_resource_efficiency', 0):.2f}")
            print(f"Average Accuracy: {wl_perf.get('average_accuracy', 0):.1%}")
    
    finally:
        manager.stop()
        print("✅ Scenario 2 completed\n")

def scenario_resource_constraints():
    """
    Scenario 3: Operating under resource constraints with intelligent allocation
    """
    print("⚠️  SCENARIO 3: Resource Constraint Handling")
    print("=" * 60)
    
    # Create constrained configuration
    constrained_config = {
        'datacenter': {
            'total_cpu_cores': 100,
            'total_memory_gb': 256,
            'total_gpu_count': 8,
            'total_storage_tb': 5
        },
        'optimization': {
            'algorithm': 'resource_balanced',
            'reallocation_interval_minutes': 5,
            'resource_utilization_target': 0.95
        }
    }
    
    # Write temporary config
    import yaml
    with open('constrained_config.yaml', 'w') as f:
        yaml.dump(constrained_config, f)
    
    try:
        manager = DatacenterManager('constrained_config.yaml')
        manager.start()
        
        # Create more workloads than resources can handle
        print("Creating 20 workloads for limited resources...")
        workloads = manager.workload_simulator.generate_batch_workloads(20)
        
        # Make some workloads more resource-intensive
        for i, workload in enumerate(workloads[:10]):
            if workload.workload_type == WorkloadType.TRAINING:
                workload.resource_requirements.cpu_cores = 20
                workload.resource_requirements.memory_gb = 64
                workload.resource_requirements.gpu_count = 2
                workload.name = f"intensive_training_{i+1}"
        
        results = manager.submit_batch_workloads(workloads)
        print(f"Submission results: {results}")
        
        # Monitor resource allocation under constraints
        print("\n📊 Monitoring resource allocation under constraints...")
        for i in range(10):  # 50 seconds
            status = manager.get_system_status()
            resources = status['resources']
            
            print(f"Time {i*5:2d}s: Active={status['workloads']['active_count']:2d}, "
                  f"Queued={status['workloads']['queued_count']:2d}, "
                  f"CPU={resources['utilization']['cpu_utilization']:5.1%} "
                  f"({resources['available']['available_cpu_cores']} free), "
                  f"GPU={resources['utilization']['gpu_utilization']:5.1%} "
                  f"({resources['available']['available_gpu_count']} free)")
            
            time.sleep(5)
        
        # Force optimization under constraints
        print("\n⚙️ Running optimization under resource constraints...")
        opt_result = manager.run_optimization()
        if opt_result['success']:
            result = opt_result['result']
            print(f"Constrained optimization: {result['strategy_used']}")
            for rec in result['recommendations']:
                print(f"  • {rec}")
        
        manager.stop()
        
    finally:
        # Cleanup temporary config
        import os
        if os.path.exists('constrained_config.yaml'):
            os.remove('constrained_config.yaml')
        print("✅ Scenario 3 completed\n")

def scenario_performance_degradation_recovery():
    """
    Scenario 4: Automatic recovery from performance degradation
    """
    print("🔧 SCENARIO 4: Performance Degradation Recovery")
    print("=" * 60)
    
    manager = DatacenterManager()
    manager.start()
    
    try:
        # Create workloads with strict performance requirements
        print("Creating performance-critical workloads...")
        critical_workloads = []
        
        for i in range(6):
            workload = manager.workload_simulator.generate_workload(WorkloadType.INFERENCE)
            workload.priority = 5
            workload.min_throughput = 80.0
            workload.max_latency_ms = 30.0
            workload.min_accuracy = 0.98
            workload.name = f"critical_service_{i+1}"
            critical_workloads.append(workload)
        
        # Submit critical workloads
        manager.submit_batch_workloads(critical_workloads)
        
        # Let them run for a bit
        time.sleep(10)
        
        # Simulate system stress by adding resource-intensive workloads
        print("\n⚠️  Simulating system stress with resource-intensive workloads...")
        stress_workloads = []
        for i in range(12):
            workload = manager.workload_simulator.generate_workload(WorkloadType.TRAINING)
            workload.priority = 1  # Low priority
            workload.resource_requirements.cpu_cores = 25
            workload.resource_requirements.memory_gb = 128
            workload.resource_requirements.gpu_count = 3
            workload.name = f"stress_workload_{i+1}"
            stress_workloads.append(workload)
        
        manager.submit_batch_workloads(stress_workloads)
        
        # Monitor system under stress
        print("\n📊 Monitoring system under stress...")
        stress_start_time = time.time()
        
        for i in range(12):  # 60 seconds under stress
            status = manager.get_system_status()
            
            # Calculate average performance of critical workloads
            critical_performance = 0
            critical_count = 0
            
            for wl in status['workloads']['active_workloads']:
                if 'critical_service' in wl['name']:
                    critical_performance += wl['performance_score']
                    critical_count += 1
            
            if critical_count > 0:
                critical_performance /= critical_count
            
            resources = status['resources']['utilization']
            
            print(f"Stress +{i*5:2d}s: Active={status['workloads']['active_count']:2d}, "
                  f"Queued={status['workloads']['queued_count']:2d}, "
                  f"CriticalPerf={critical_performance:.1f}, "
                  f"CPU={resources['cpu_utilization']:5.1%}, "
                  f"GPU={resources['gpu_utilization']:5.1%}")
            
            # Trigger optimization if performance drops
            if critical_performance < 70 and i > 3:
                print("    🚨 Performance degradation detected - triggering optimization!")
                opt_result = manager.run_optimization()
                if opt_result['success']:
                    print(f"    ⚙️  Optimization applied: {opt_result['result']['reallocation_count']} changes")
            
            time.sleep(5)
        
        # Final performance check
        final_status = manager.get_system_status()
        final_critical_performance = 0
        critical_count = 0
        
        for wl in final_status['workloads']['active_workloads']:
            if 'critical_service' in wl['name']:
                final_critical_performance += wl['performance_score']
                critical_count += 1
        
        if critical_count > 0:
            final_critical_performance /= critical_count
        
        print(f"\n📈 Recovery Results:")
        print(f"  Final critical workload performance: {final_critical_performance:.1f}/100")
        print(f"  Total optimizations: {final_status['system_info']['total_optimizations_run']}")
        print(f"  System successfully {'maintained' if final_critical_performance > 80 else 'struggled with'} performance under stress")
        
    finally:
        manager.stop()
        print("✅ Scenario 4 completed\n")

def main():
    """Run all demonstration scenarios"""
    print("🚀 AI Datacenter Resource Management - Advanced Scenarios")
    print("=" * 70)
    print("Demonstrating advanced capabilities of the automated resource management system")
    print()
    
    scenarios = [
        scenario_peak_load_handling,
        scenario_mixed_workload_optimization,
        scenario_resource_constraints,
        scenario_performance_degradation_recovery
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"RUNNING SCENARIO {i} OF {len(scenarios)}")
        print(f"{'='*70}")
        
        try:
            scenario()
        except KeyboardInterrupt:
            print(f"\n🛑 Scenario {i} interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Scenario {i} failed: {e}")
            continue
        
        if i < len(scenarios):
            print("Press Enter to continue to next scenario (or Ctrl+C to exit)...")
            try:
                input()
            except KeyboardInterrupt:
                break
    
    print("\n🎯 All scenarios completed!")
    print("The system has demonstrated:")
    print("  ✅ Intelligent peak load handling with queueing")
    print("  ✅ Mixed workload optimization with different requirements")
    print("  ✅ Resource-constrained operation with smart allocation")
    print("  ✅ Automatic performance degradation recovery")
    print("\nThis showcases the end-to-end performance impact modeling")
    print("and cross-functional team capabilities of the system.")

if __name__ == "__main__":
    main()