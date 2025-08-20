#!/usr/bin/env python3
"""
Main entry point for AI Datacenter Resource Management System

This script demonstrates the automated system for managing and optimizing 
resources in a simulated AI datacenter with dynamic allocation based on 
performance and accuracy requirements.
"""
import argparse
import time
import json
import sys
from datacenter_manager import DatacenterManager, run_simulation

def main():
    parser = argparse.ArgumentParser(
        description="AI Datacenter Resource Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run interactive mode
    python main.py --interactive
    
    # Run simulation for 5 minutes with 15 workloads
    python main.py --simulate --duration 5 --workloads 15
    
    # Show system status
    python main.py --status
    
    # Generate performance report
    python main.py --report --hours 24
        """
    )
    
    parser.add_argument('--config', default='config.yaml',
                       help='Configuration file path (default: config.yaml)')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--simulate', action='store_true',
                       help='Run automated simulation')
    parser.add_argument('--duration', type=int, default=10,
                       help='Simulation duration in minutes (default: 10)')
    parser.add_argument('--workloads', type=int, default=15,
                       help='Number of workloads for simulation (default: 15)')
    parser.add_argument('--status', action='store_true',
                       help='Show current system status')
    parser.add_argument('--report', action='store_true',
                       help='Generate performance report')
    parser.add_argument('--hours', type=int, default=24,
                       help='Hours to analyze for report (default: 24)')
    parser.add_argument('--optimize', action='store_true',
                       help='Run manual optimization')
    
    args = parser.parse_args()
    
    if args.simulate:
        print("🚀 Starting AI Datacenter Resource Management Simulation")
        print("=" * 70)
        results = run_simulation(args.duration, args.workloads)
        
        # Save results
        with open('simulation_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📊 Results saved to simulation_results.json")
        
    elif args.interactive:
        run_interactive_mode(args.config)
        
    elif args.status or args.report or args.optimize:
        # Initialize manager for status/report operations
        manager = DatacenterManager(args.config)
        
        if args.status:
            show_status(manager)
        
        if args.report:
            generate_report(manager, args.hours)
        
        if args.optimize:
            run_optimization(manager)
    
    else:
        # Default: run a quick demo
        print("🎯 Running Quick Demo of AI Datacenter Resource Management")
        print("=" * 70)
        print("For more options, use --help")
        print()
        
        # Quick 2-minute demo
        results = run_simulation(duration_minutes=2, workload_count=8)
        print("\n✅ Demo completed! Use --interactive for full control.")

def run_interactive_mode(config_file):
    """Run the system in interactive mode"""
    print("🎛️  AI Datacenter Resource Management - Interactive Mode")
    print("=" * 70)
    
    manager = DatacenterManager(config_file)
    manager.start()
    
    try:
        while True:
            print("\nAvailable commands:")
            print("1. Status - Show system status")
            print("2. Create - Create demo workloads")
            print("3. Optimize - Run optimization")
            print("4. Report - Generate performance report")
            print("5. Monitor - Real-time monitoring (30s)")
            print("6. Quit - Exit system")
            
            choice = input("\nEnter command (1-6): ").strip()
            
            if choice == '1':
                show_status(manager)
            elif choice == '2':
                count = input("Number of workloads to create (default 5): ").strip()
                count = int(count) if count.isdigit() else 5
                workloads = manager.create_demo_workloads(count)
                print(f"✅ Created {len(workloads)} workloads")
            elif choice == '3':
                run_optimization(manager)
            elif choice == '4':
                hours = input("Hours to analyze (default 24): ").strip()
                hours = int(hours) if hours.isdigit() else 24
                generate_report(manager, hours)
            elif choice == '5':
                monitor_system(manager, 30)
            elif choice == '6':
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    
    finally:
        manager.stop()
        print("👋 System stopped. Goodbye!")

def show_status(manager):
    """Display system status"""
    status = manager.get_system_status()
    
    print("\n📊 System Status")
    print("-" * 40)
    
    # System info
    sys_info = status['system_info']
    print(f"Status: {'🟢 Running' if sys_info['is_running'] else '🔴 Stopped'}")
    print(f"Uptime: {sys_info['uptime_hours']:.1f} hours")
    print(f"Workloads processed: {sys_info['total_workloads_processed']}")
    print(f"Optimizations run: {sys_info['total_optimizations_run']}")
    
    # Workloads
    workloads = status['workloads']
    print(f"\nWorkloads:")
    print(f"  Active: {workloads['active_count']}")
    print(f"  Queued: {workloads['queued_count']}")
    print(f"  Completed: {workloads['completed_count']}")
    
    # Resources
    resources = status['resources']
    util = resources['utilization']
    print(f"\nResource Utilization:")
    print(f"  CPU: {util['cpu_utilization']:.1%}")
    print(f"  Memory: {util['memory_utilization']:.1%}")
    print(f"  GPU: {util['gpu_utilization']:.1%}")
    
    available = resources['available']
    print(f"\nAvailable Resources:")
    print(f"  CPU cores: {available['available_cpu_cores']}")
    print(f"  Memory: {available['available_memory_gb']:.1f} GB")
    print(f"  GPUs: {available['available_gpu_count']}")

def generate_report(manager, hours):
    """Generate and display performance report"""
    print(f"\n📈 Generating Performance Report ({hours}h)")
    print("-" * 50)
    
    report = manager.generate_performance_report(hours)
    
    summary = report['summary']
    print(f"Report Period: {hours} hours")
    print(f"Generated: {report['generated_at']}")
    print(f"System Uptime: {summary['system_uptime_hours']:.1f} hours")
    print(f"Total Workloads: {summary['total_workloads_processed']}")
    print(f"Optimizations: {summary['total_optimizations_run']}")
    
    # Performance metrics
    if 'system_performance' in report['performance_metrics']:
        perf = report['performance_metrics']['system_performance']
        print(f"\nSystem Performance:")
        print(f"  Avg CPU Utilization: {perf.get('average_cpu_utilization', 0):.1%}")
        print(f"  Avg Memory Utilization: {perf.get('average_memory_utilization', 0):.1%}")
        print(f"  Avg GPU Utilization: {perf.get('average_gpu_utilization', 0):.1%}")
        print(f"  Completed Workloads: {perf.get('total_workloads_completed', 0)}")
    
    if 'workload_performance' in report['performance_metrics']:
        workload_perf = report['performance_metrics']['workload_performance']
        print(f"\nWorkload Performance:")
        print(f"  Avg Performance Score: {workload_perf.get('average_performance_score', 0):.1f}/100")
        print(f"  Avg Resource Efficiency: {workload_perf.get('average_resource_efficiency', 0):.2f}")
        print(f"  Avg Accuracy: {workload_perf.get('average_accuracy', 0):.1%}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # Save report
    filename = f"performance_report_{int(time.time())}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n💾 Full report saved to {filename}")

def run_optimization(manager):
    """Run manual optimization"""
    print("\n⚙️  Running Optimization...")
    
    result = manager.run_optimization()
    
    if result['success']:
        opt_result = result['result']
        print(f"✅ Optimization completed:")
        print(f"  Strategy: {opt_result['strategy_used']}")
        print(f"  Workloads optimized: {opt_result['workloads_optimized']}")
        print(f"  Performance improvement: {opt_result['performance_improvement']:+.3f}")
        print(f"  Efficiency improvement: {opt_result['resource_efficiency_improvement']:+.3f}")
        print(f"  Reallocations: {opt_result['reallocation_count']}")
        print(f"  Time taken: {opt_result['optimization_time_seconds']:.2f}s")
        
        if opt_result['recommendations']:
            print(f"  Recommendations:")
            for rec in opt_result['recommendations']:
                print(f"    • {rec}")
    else:
        print(f"❌ Optimization failed: {result['message']}")

def monitor_system(manager, duration_seconds):
    """Monitor system in real-time"""
    print(f"\n👁️  Real-time Monitoring ({duration_seconds}s)")
    print("-" * 50)
    
    start_time = time.time()
    end_time = start_time + duration_seconds
    
    try:
        while time.time() < end_time:
            status = manager.get_system_status()
            
            current_time = time.time() - start_time
            workloads = status['workloads']
            util = status['resources']['utilization']
            
            print(f"\r⏱️  {current_time:05.1f}s | "
                  f"Active: {workloads['active_count']:2d} | "
                  f"Queue: {workloads['queued_count']:2d} | "
                  f"Done: {workloads['completed_count']:3d} | "
                  f"CPU: {util['cpu_utilization']:5.1%} | "
                  f"Mem: {util['memory_utilization']:5.1%} | "
                  f"GPU: {util['gpu_utilization']:5.1%}", end='', flush=True)
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        pass
    
    print("\n✅ Monitoring completed")

if __name__ == "__main__":
    main()