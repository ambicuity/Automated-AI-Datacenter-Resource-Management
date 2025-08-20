"""
Data Visualization for AI Datacenter Resource Management System
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime, timedelta
import logging

# Set plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class DatacenterVisualizer:
    """Creates visualizations for datacenter performance data"""
    
    def __init__(self, output_dir: str = "visualizations"):
        """
        Initialize visualizer
        
        Args:
            output_dir (str): Directory to save visualization files
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Color schemes for different elements
        self.resource_colors = {
            'cpu_utilization': '#FF6B6B',
            'memory_utilization': '#4ECDC4', 
            'gpu_utilization': '#45B7D1',
            'storage_utilization': '#96CEB4'
        }
        
        self.workload_colors = {
            'training': '#FF8C42',
            'inference': '#6BCF7F',
            'data_processing': '#9B59B6'
        }
    
    def create_resource_utilization_dashboard(self, system_metrics: List[Dict]) -> str:
        """
        Create a comprehensive resource utilization dashboard
        
        Args:
            system_metrics (List[Dict]): List of system metrics over time
            
        Returns:
            str: Path to saved dashboard image
        """
        if not system_metrics:
            self.logger.warning("No system metrics provided for visualization")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(system_metrics)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('AI Datacenter Resource Utilization Dashboard', fontsize=16, fontweight='bold')
        
        # Resource utilization over time
        ax1 = axes[0, 0]
        for resource in ['total_cpu_utilization', 'total_memory_utilization', 'total_gpu_utilization']:
            if resource in df.columns:
                display_name = resource.replace('total_', '').replace('_', ' ').title()
                color = self.resource_colors.get(resource.replace('total_', ''), '#333333')
                ax1.plot(df['timestamp'], df[resource] * 100, label=display_name, 
                        linewidth=2, color=color)
        
        ax1.set_title('Resource Utilization Over Time')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Utilization (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # Workload counts over time
        ax2 = axes[0, 1]
        workload_cols = ['active_workloads', 'completed_workloads']
        for col in workload_cols:
            if col in df.columns:
                display_name = col.replace('_', ' ').title()
                ax2.plot(df['timestamp'], df[col], label=display_name, linewidth=2, marker='o')
        
        ax2.set_title('Workload Counts Over Time')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Count')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Performance metrics
        ax3 = axes[1, 0]
        perf_cols = ['average_workload_accuracy', 'average_workload_throughput']
        ax3_twin = ax3.twinx()
        
        if 'average_workload_accuracy' in df.columns:
            ax3.plot(df['timestamp'], df['average_workload_accuracy'] * 100, 
                    color='green', linewidth=2, label='Accuracy (%)')
            ax3.set_ylabel('Accuracy (%)', color='green')
            ax3.tick_params(axis='y', labelcolor='green')
        
        if 'average_workload_throughput' in df.columns:
            ax3_twin.plot(df['timestamp'], df['average_workload_throughput'], 
                         color='orange', linewidth=2, label='Throughput (ops/s)')
            ax3_twin.set_ylabel('Throughput (ops/s)', color='orange')
            ax3_twin.tick_params(axis='y', labelcolor='orange')
        
        ax3.set_title('Performance Metrics Over Time')
        ax3.set_xlabel('Time')
        ax3.grid(True, alpha=0.3)
        
        # Current resource distribution (pie chart)
        ax4 = axes[1, 1]
        if len(df) > 0:
            latest_metrics = df.iloc[-1]
            resource_values = [
                latest_metrics.get('total_cpu_utilization', 0) * 100,
                latest_metrics.get('total_memory_utilization', 0) * 100,
                latest_metrics.get('total_gpu_utilization', 0) * 100
            ]
            resource_labels = ['CPU Utilization', 'Memory Utilization', 'GPU Utilization']
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            ax4.pie(resource_values, labels=resource_labels, colors=colors, autopct='%1.1f%%')
            ax4.set_title('Current Resource Utilization')
        
        plt.tight_layout()
        
        # Save dashboard
        filename = f"resource_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Resource utilization dashboard saved to {filepath}")
        return filepath
    
    def create_workload_performance_chart(self, workload_metrics: List[Dict]) -> str:
        """
        Create workload performance analysis chart
        
        Args:
            workload_metrics (List[Dict]): List of workload performance metrics
            
        Returns:
            str: Path to saved chart
        """
        if not workload_metrics:
            self.logger.warning("No workload metrics provided for visualization")
            return None
        
        df = pd.DataFrame(workload_metrics)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('AI Workload Performance Analysis', fontsize=16, fontweight='bold')
        
        # Performance scores by workload type
        ax1 = axes[0, 0]
        if 'workload_type' in df.columns and 'performance_score' in df.columns:
            workload_perf = df.groupby('workload_type')['performance_score'].mean()
            bars = ax1.bar(workload_perf.index, workload_perf.values, 
                          color=[self.workload_colors.get(wt, '#333333') for wt in workload_perf.index])
            ax1.set_title('Average Performance Score by Workload Type')
            ax1.set_ylabel('Performance Score')
            ax1.set_ylim(0, 100)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}', ha='center', va='bottom')
        
        # Resource efficiency distribution
        ax2 = axes[0, 1]
        if 'resource_efficiency' in df.columns:
            ax2.hist(df['resource_efficiency'], bins=20, color='skyblue', alpha=0.7, edgecolor='black')
            ax2.axvline(df['resource_efficiency'].mean(), color='red', linestyle='--', 
                       label=f'Mean: {df["resource_efficiency"].mean():.2f}')
            ax2.set_title('Resource Efficiency Distribution')
            ax2.set_xlabel('Resource Efficiency')
            ax2.set_ylabel('Frequency')
            ax2.legend()
        
        # Performance trends over time
        ax3 = axes[1, 0]
        if 'performance_score' in df.columns:
            # Group by workload type and plot trends
            for workload_type in df['workload_type'].unique():
                type_data = df[df['workload_type'] == workload_type]
                color = self.workload_colors.get(workload_type, '#333333')
                ax3.plot(type_data['timestamp'], type_data['performance_score'], 
                        label=workload_type.title(), alpha=0.7, color=color)
            
            ax3.set_title('Performance Score Trends by Type')
            ax3.set_xlabel('Time')
            ax3.set_ylabel('Performance Score')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # Accuracy vs Throughput scatter
        ax4 = axes[1, 1]
        if 'accuracy' in df.columns and 'throughput' in df.columns:
            for workload_type in df['workload_type'].unique():
                type_data = df[df['workload_type'] == workload_type]
                color = self.workload_colors.get(workload_type, '#333333')
                ax4.scatter(type_data['accuracy'] * 100, type_data['throughput'], 
                           label=workload_type.title(), alpha=0.7, color=color, s=50)
            
            ax4.set_title('Accuracy vs Throughput')
            ax4.set_xlabel('Accuracy (%)')
            ax4.set_ylabel('Throughput (ops/s)')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        filename = f"workload_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Workload performance chart saved to {filepath}")
        return filepath
    
    def create_optimization_impact_chart(self, optimization_history: List[Dict]) -> str:
        """
        Create chart showing optimization impact over time
        
        Args:
            optimization_history (List[Dict]): List of optimization results
            
        Returns:
            str: Path to saved chart
        """
        if not optimization_history:
            self.logger.warning("No optimization history provided for visualization")
            return None
        
        df = pd.DataFrame(optimization_history)
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Optimization Impact Analysis', fontsize=16, fontweight='bold')
        
        # Performance improvement over time
        ax1 = axes[0, 0]
        if 'performance_improvement' in df.columns:
            ax1.bar(range(len(df)), df['performance_improvement'], 
                   color=['green' if x > 0 else 'red' for x in df['performance_improvement']])
            ax1.set_title('Performance Improvement per Optimization')
            ax1.set_xlabel('Optimization Run')
            ax1.set_ylabel('Performance Change')
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax1.grid(True, alpha=0.3)
        
        # Resource efficiency improvement
        ax2 = axes[0, 1]
        if 'resource_efficiency_improvement' in df.columns:
            ax2.bar(range(len(df)), df['resource_efficiency_improvement'],
                   color=['blue' if x > 0 else 'orange' for x in df['resource_efficiency_improvement']])
            ax2.set_title('Resource Efficiency Improvement')
            ax2.set_xlabel('Optimization Run')
            ax2.set_ylabel('Efficiency Change')
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax2.grid(True, alpha=0.3)
        
        # Optimization strategy distribution
        ax3 = axes[1, 0]
        if 'strategy_used' in df.columns:
            strategy_counts = df['strategy_used'].value_counts()
            ax3.pie(strategy_counts.values, labels=strategy_counts.index, autopct='%1.1f%%')
            ax3.set_title('Optimization Strategies Used')
        
        # Reallocation counts
        ax4 = axes[1, 1]
        if 'reallocation_count' in df.columns:
            ax4.plot(range(len(df)), df['reallocation_count'], 
                    marker='o', linewidth=2, markersize=6)
            ax4.set_title('Resource Reallocations per Run')
            ax4.set_xlabel('Optimization Run')
            ax4.set_ylabel('Number of Reallocations')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        filename = f"optimization_impact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Optimization impact chart saved to {filepath}")
        return filepath
    
    def create_comprehensive_report(self, performance_data: Dict[str, Any]) -> str:
        """
        Create a comprehensive visual report combining multiple charts
        
        Args:
            performance_data (Dict): Complete performance data including system and workload metrics
            
        Returns:
            str: Path to saved comprehensive report
        """
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(20, 12))
        fig.suptitle('AI Datacenter Management - Comprehensive Performance Report', 
                    fontsize=20, fontweight='bold')
        
        # Create grid layout
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Extract data
        system_metrics = performance_data.get('system_metrics', [])
        workload_metrics = performance_data.get('workload_metrics', [])
        optimization_history = performance_data.get('optimization_history', [])
        
        if system_metrics:
            df_system = pd.DataFrame(system_metrics)
            df_system['timestamp'] = pd.to_datetime(df_system['timestamp'], unit='s')
            
            # System resource utilization
            ax1 = fig.add_subplot(gs[0, :2])
            for resource in ['total_cpu_utilization', 'total_memory_utilization', 'total_gpu_utilization']:
                if resource in df_system.columns:
                    display_name = resource.replace('total_', '').replace('_', ' ').title()
                    color = self.resource_colors.get(resource.replace('total_', ''), '#333333')
                    ax1.plot(df_system['timestamp'], df_system[resource] * 100, 
                            label=display_name, linewidth=2, color=color)
            
            ax1.set_title('Resource Utilization Trends')
            ax1.set_ylabel('Utilization (%)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        if workload_metrics:
            df_workload = pd.DataFrame(workload_metrics)
            
            # Workload performance by type
            ax2 = fig.add_subplot(gs[0, 2])
            if 'workload_type' in df_workload.columns and 'performance_score' in df_workload.columns:
                workload_perf = df_workload.groupby('workload_type')['performance_score'].mean()
                bars = ax2.bar(workload_perf.index, workload_perf.values,
                              color=[self.workload_colors.get(wt, '#333333') for wt in workload_perf.index])
                ax2.set_title('Avg Performance by Type')
                ax2.set_ylabel('Score')
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{height:.0f}', ha='center', va='bottom')
        
        # System summary metrics
        ax3 = fig.add_subplot(gs[0, 3])
        summary_data = performance_data.get('summary', {})
        metrics = ['Total Workloads', 'Optimizations', 'Avg CPU %', 'Avg GPU %']
        values = [
            summary_data.get('total_workloads_processed', 0),
            summary_data.get('total_optimizations_run', 0),
            summary_data.get('avg_cpu_utilization', 0) * 100,
            summary_data.get('avg_gpu_utilization', 0) * 100
        ]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        bars = ax3.bar(range(len(metrics)), values, color=colors)
        ax3.set_title('System Summary')
        ax3.set_xticks(range(len(metrics)))
        ax3.set_xticklabels(metrics, rotation=45, ha='right')
        
        # Add value labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                    f'{height:.0f}', ha='center', va='bottom')
        
        # Additional charts in second and third rows
        if workload_metrics and 'resource_efficiency' in df_workload.columns:
            ax4 = fig.add_subplot(gs[1, :2])
            ax4.hist(df_workload['resource_efficiency'], bins=20, color='lightblue', 
                    alpha=0.7, edgecolor='black')
            mean_eff = df_workload['resource_efficiency'].mean()
            ax4.axvline(mean_eff, color='red', linestyle='--', 
                       label=f'Mean: {mean_eff:.2f}')
            ax4.set_title('Resource Efficiency Distribution')
            ax4.set_xlabel('Efficiency Score')
            ax4.set_ylabel('Frequency')
            ax4.legend()
        
        if optimization_history:
            df_opt = pd.DataFrame(optimization_history)
            
            # Optimization effectiveness
            ax5 = fig.add_subplot(gs[1, 2:])
            if 'performance_improvement' in df_opt.columns:
                x_pos = range(len(df_opt))
                ax5.bar(x_pos, df_opt['performance_improvement'],
                       color=['green' if x > 0 else 'red' for x in df_opt['performance_improvement']])
                ax5.set_title('Optimization Performance Impact')
                ax5.set_xlabel('Optimization Run')
                ax5.set_ylabel('Performance Change')
                ax5.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Bottom row - detailed metrics
        if system_metrics and workload_metrics:
            # Correlation heatmap
            ax6 = fig.add_subplot(gs[2, :])
            
            # Create correlation data
            corr_data = []
            if len(df_system) > 0 and len(df_workload) > 0:
                # Combine key metrics for correlation analysis
                combined_metrics = {
                    'CPU Util': df_system['total_cpu_utilization'].mean() if 'total_cpu_utilization' in df_system else 0,
                    'Memory Util': df_system['total_memory_utilization'].mean() if 'total_memory_utilization' in df_system else 0,
                    'GPU Util': df_system['total_gpu_utilization'].mean() if 'total_gpu_utilization' in df_system else 0,
                    'Avg Performance': df_workload['performance_score'].mean() if 'performance_score' in df_workload else 0,
                    'Avg Efficiency': df_workload['resource_efficiency'].mean() if 'resource_efficiency' in df_workload else 0,
                    'Active Workloads': df_system['active_workloads'].mean() if 'active_workloads' in df_system else 0
                }
                
                # Create a simple metrics display
                metrics_text = []
                for metric, value in combined_metrics.items():
                    if 'Util' in metric:
                        metrics_text.append(f"{metric}: {value:.1%}")
                    elif 'Performance' in metric or 'Efficiency' in metric:
                        metrics_text.append(f"{metric}: {value:.2f}")
                    else:
                        metrics_text.append(f"{metric}: {value:.0f}")
                
                ax6.text(0.1, 0.5, '\n'.join(metrics_text), transform=ax6.transAxes,
                        fontsize=12, verticalalignment='center',
                        bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
                ax6.set_title('Key Performance Indicators Summary')
                ax6.axis('off')
        
        # Add timestamp
        fig.text(0.99, 0.01, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                ha='right', va='bottom', fontsize=10, style='italic')
        
        # Save comprehensive report
        filename = f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Comprehensive report saved to {filepath}")
        return filepath
    
    def load_metrics_from_file(self, metrics_file: str) -> Dict[str, List]:
        """
        Load metrics from JSON lines file
        
        Args:
            metrics_file (str): Path to metrics file
            
        Returns:
            Dict[str, List]: Separated system and workload metrics
        """
        system_metrics = []
        workload_metrics = []
        
        try:
            with open(metrics_file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data.get('type') == 'system':
                        system_metrics.append(data)
                    elif data.get('type') == 'workload':
                        workload_metrics.append(data)
        except FileNotFoundError:
            self.logger.warning(f"Metrics file {metrics_file} not found")
        except Exception as e:
            self.logger.error(f"Error loading metrics from {metrics_file}: {e}")
        
        return {
            'system_metrics': system_metrics,
            'workload_metrics': workload_metrics
        }

# Convenience functions for quick visualization
def visualize_simulation_results(results_file: str, output_dir: str = "visualizations") -> List[str]:
    """
    Create visualizations from simulation results
    
    Args:
        results_file (str): Path to simulation results JSON file
        output_dir (str): Output directory for visualizations
        
    Returns:
        List[str]: Paths to created visualization files
    """
    visualizer = DatacenterVisualizer(output_dir)
    created_files = []
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Create comprehensive report
        report_path = visualizer.create_comprehensive_report(results)
        if report_path:
            created_files.append(report_path)
        
        print(f"✅ Visualizations created in {output_dir}/")
        for file_path in created_files:
            print(f"  📊 {os.path.basename(file_path)}")
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
    
    return created_files

if __name__ == "__main__":
    # Example usage
    visualizer = DatacenterVisualizer()
    
    # Check if there are existing metrics to visualize
    metrics_file = "logs/performance_metrics.jsonl"
    if os.path.exists(metrics_file):
        print("📊 Creating visualizations from existing metrics...")
        metrics_data = visualizer.load_metrics_from_file(metrics_file)
        
        if metrics_data['system_metrics']:
            visualizer.create_resource_utilization_dashboard(metrics_data['system_metrics'])
        
        if metrics_data['workload_metrics']:
            visualizer.create_workload_performance_chart(metrics_data['workload_metrics'])
        
        print("✅ Visualizations created!")
    else:
        print("ℹ️  No metrics file found. Run a simulation first to generate data for visualization.")