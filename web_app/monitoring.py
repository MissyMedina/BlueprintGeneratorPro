#!/usr/bin/env python3
"""
Monitoring and logging utilities for Guidance Blueprint Kit Pro
"""

import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import psutil
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'active_users': 0
        }
        self.start_time = time.time()
    
    def record_request(self, success: bool, response_time: float):
        """Record a request with its outcome and response time"""
        self.metrics['requests_total'] += 1
        if success:
            self.metrics['requests_success'] += 1
        else:
            self.metrics['requests_failed'] += 1
        
        self.metrics['response_times'].append(response_time)
        
        # Keep only last 1000 response times to prevent memory issues
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def record_system_metrics(self):
        """Record current system metrics"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'].append({
                'timestamp': datetime.now().isoformat(),
                'percent': memory.percent,
                'available_gb': memory.available / (1024**3)
            })
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_usage'].append({
                'timestamp': datetime.now().isoformat(),
                'percent': cpu_percent
            })
            
            # Keep only last 100 system metrics
            if len(self.metrics['memory_usage']) > 100:
                self.metrics['memory_usage'] = self.metrics['memory_usage'][-100:]
            if len(self.metrics['cpu_usage']) > 100:
                self.metrics['cpu_usage'] = self.metrics['cpu_usage'][-100:]
                
        except Exception as e:
            logger.error(f"Error recording system metrics: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        uptime = time.time() - self.start_time
        
        # Calculate response time statistics
        response_times = self.metrics['response_times']
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate success rate
        total_requests = self.metrics['requests_total']
        success_rate = (self.metrics['requests_success'] / total_requests * 100) if total_requests > 0 else 0
        
        # Get current system stats
        try:
            current_memory = psutil.virtual_memory().percent
            current_cpu = psutil.cpu_percent()
        except:
            current_memory = 0
            current_cpu = 0
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
            'requests': {
                'total': total_requests,
                'success': self.metrics['requests_success'],
                'failed': self.metrics['requests_failed'],
                'success_rate': round(success_rate, 2)
            },
            'performance': {
                'avg_response_time_ms': round(avg_response_time * 1000, 2),
                'requests_per_minute': round(total_requests / (uptime / 60), 2) if uptime > 0 else 0
            },
            'system': {
                'memory_usage_percent': current_memory,
                'cpu_usage_percent': current_cpu,
                'active_users': self.metrics['active_users']
            }
        }
    
    def export_metrics(self, filename: Optional[str] = None) -> str:
        """Export metrics to JSON file"""
        if not filename:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        stats = self.get_stats()
        stats['detailed_metrics'] = self.metrics
        
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        return filename

# Global monitor instance
monitor = PerformanceMonitor()

def track_performance(func):
    """Decorator to track function performance"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            logger.error(f"Error in {func.__name__}: {e}")
            raise
        finally:
            response_time = time.time() - start_time
            monitor.record_request(success, response_time)
            
            # Log slow requests
            if response_time > 5.0:  # 5 seconds threshold
                logger.warning(f"Slow request: {func.__name__} took {response_time:.2f}s")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            logger.error(f"Error in {func.__name__}: {e}")
            raise
        finally:
            response_time = time.time() - start_time
            monitor.record_request(success, response_time)
            
            # Log slow requests
            if response_time > 5.0:  # 5 seconds threshold
                logger.warning(f"Slow request: {func.__name__} took {response_time:.2f}s")
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

class HealthChecker:
    """Health check utilities"""
    
    @staticmethod
    def check_system_health() -> Dict[str, Any]:
        """Comprehensive system health check"""
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        try:
            # Memory check
            memory = psutil.virtual_memory()
            memory_healthy = memory.percent < 90
            health['checks']['memory'] = {
                'status': 'healthy' if memory_healthy else 'warning',
                'usage_percent': memory.percent,
                'available_gb': round(memory.available / (1024**3), 2)
            }
            
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_healthy = cpu_percent < 80
            health['checks']['cpu'] = {
                'status': 'healthy' if cpu_healthy else 'warning',
                'usage_percent': cpu_percent
            }
            
            # Disk check
            disk = psutil.disk_usage('/')
            disk_healthy = disk.percent < 90
            health['checks']['disk'] = {
                'status': 'healthy' if disk_healthy else 'warning',
                'usage_percent': disk.percent,
                'free_gb': round(disk.free / (1024**3), 2)
            }
            
            # Overall status
            if not all([memory_healthy, cpu_healthy, disk_healthy]):
                health['status'] = 'warning'
            
        except Exception as e:
            health['status'] = 'error'
            health['error'] = str(e)
        
        return health
    
    @staticmethod
    def check_dependencies() -> Dict[str, Any]:
        """Check external dependencies"""
        dependencies = {
            'status': 'healthy',
            'checks': {}
        }
        
        # Check if required modules can be imported
        required_modules = [
            'fastapi', 'uvicorn', 'pydantic', 'requests', 'psutil'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                dependencies['checks'][module] = {'status': 'healthy'}
            except ImportError:
                dependencies['checks'][module] = {'status': 'error', 'error': 'Module not found'}
                dependencies['status'] = 'error'
        
        return dependencies

# Logging utilities
class StructuredLogger:
    """Structured logging for better observability"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_request(self, method: str, path: str, status_code: int, response_time: float, user_id: Optional[str] = None):
        """Log HTTP request details"""
        self.logger.info(json.dumps({
            'event': 'http_request',
            'method': method,
            'path': path,
            'status_code': status_code,
            'response_time_ms': round(response_time * 1000, 2),
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }))
    
    def log_document_generation(self, doc_type: str, project_name: str, success: bool, generation_time: float):
        """Log document generation events"""
        self.logger.info(json.dumps({
            'event': 'document_generation',
            'doc_type': doc_type,
            'project_name': project_name,
            'success': success,
            'generation_time_ms': round(generation_time * 1000, 2),
            'timestamp': datetime.now().isoformat()
        }))
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with context"""
        self.logger.error(json.dumps({
            'event': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }))

# Global structured logger
structured_logger = StructuredLogger('blueprint_pro')
