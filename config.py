"""
Configuration management for AI Datacenter Resource Management System
"""
import yaml
import os
from typing import Dict, Any

class Config:
    """Configuration manager for the datacenter system"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        Initialize configuration from YAML file
        
        Args:
            config_file (str): Path to configuration YAML file
        """
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
        
        with open(self.config_file, 'r') as file:
            config = yaml.safe_load(file)
        
        return config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key_path (str): Dot-separated path to configuration value
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_datacenter_config(self) -> Dict[str, Any]:
        """Get datacenter configuration"""
        return self.get('datacenter', {})
    
    def get_workload_config(self) -> Dict[str, Any]:
        """Get workload configuration"""
        return self.get('workloads', {})
    
    def get_optimization_config(self) -> Dict[str, Any]:
        """Get optimization configuration"""
        return self.get('optimization', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return self.get('monitoring', {})