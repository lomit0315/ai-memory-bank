import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict, Counter
import config
from logging_config import get_logger

logger = get_logger('analytics')

class AnalyticsManager:
    """Manage analytics data for the AI Memory Bank."""
    
    def __init__(self):
        self.analytics_file = config.MEMORY_DIR / "analytics.json"
        self.session_start = time.time()
        self.ensure_analytics_file()
    
    def ensure_analytics_file(self):
        """Ensure analytics file exists with proper structure."""
        if not self.analytics_file.exists():
            initial_data = {
                "searches": [],
                "uploads": [],
                "api_calls": [],
                "popular_queries": {},
                "user_sessions": [],
                "system_metrics": {
                    "total_searches": 0,
                    "total_uploads": 0,
                    "total_api_calls": 0,
                    "avg_response_time": 0,
                    "first_usage": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat()
                }
            }
            self.save_analytics(initial_data)
    
    def load_analytics(self) -> Dict[str, Any]:
        """Load analytics data from file."""
        try:
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading analytics: {e}")
            self.ensure_analytics_file()
            return self.load_analytics()
    
    def save_analytics(self, data: Dict[str, Any]):
        """Save analytics data to file."""
        try:
            data["system_metrics"]["last_activity"] = datetime.now().isoformat()
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")
    
    def record_search(self, query: str, results_count: int, response_time: float):
        """Record a search query and its metrics."""
        data = self.load_analytics()
        
        search_record = {
            "query": query,
            "results_count": results_count,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        
        data["searches"].append(search_record)
        data["system_metrics"]["total_searches"] += 1
        
        # Update popular queries
        if query in data["popular_queries"]:
            data["popular_queries"][query] += 1
        else:
            data["popular_queries"][query] = 1
        
        # Update average response time
        total_calls = data["system_metrics"]["total_api_calls"] + 1
        current_avg = data["system_metrics"]["avg_response_time"]
        data["system_metrics"]["avg_response_time"] = (
            (current_avg * (total_calls - 1) + response_time) / total_calls
        )
        
        # Keep only last 1000 searches to prevent file bloat
        data["searches"] = data["searches"][-1000:]
        
        self.save_analytics(data)
        logger.info(f"Recorded search: '{query}' -> {results_count} results in {response_time:.3f}s")
    
    def record_upload(self, filename: str, file_type: str, file_size: int, 
                     processing_time: float, chunk_count: int):
        """Record a file upload and its metrics."""
        data = self.load_analytics()
        
        upload_record = {
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "processing_time": processing_time,
            "chunk_count": chunk_count,
            "timestamp": datetime.now().isoformat()
        }
        
        data["uploads"].append(upload_record)
        data["system_metrics"]["total_uploads"] += 1
        
        # Keep only last 500 uploads
        data["uploads"] = data["uploads"][-500:]
        
        self.save_analytics(data)
        logger.info(f"Recorded upload: {filename} ({file_type}) -> {chunk_count} chunks")
    
    def record_api_call(self, endpoint: str, method: str, status_code: int, 
                       response_time: float):
        """Record an API call and its metrics."""
        data = self.load_analytics()
        
        api_record = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        
        data["api_calls"].append(api_record)
        data["system_metrics"]["total_api_calls"] += 1
        
        # Keep only last 1000 API calls
        data["api_calls"] = data["api_calls"][-1000:]
        
        self.save_analytics(data)
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the specified number of days."""
        data = self.load_analytics()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent data
        recent_searches = [
            s for s in data["searches"] 
            if datetime.fromisoformat(s["timestamp"]) > cutoff_date
        ]
        recent_uploads = [
            u for u in data["uploads"] 
            if datetime.fromisoformat(u["timestamp"]) > cutoff_date
        ]
        recent_api_calls = [
            a for a in data["api_calls"] 
            if datetime.fromisoformat(a["timestamp"]) > cutoff_date
        ]
        
        # Calculate statistics
        stats = {
            "period_days": days,
            "total_searches": len(recent_searches),
            "total_uploads": len(recent_uploads),
            "total_api_calls": len(recent_api_calls),
            "avg_search_response_time": sum(s["response_time"] for s in recent_searches) / max(len(recent_searches), 1),
            "avg_upload_processing_time": sum(u["processing_time"] for u in recent_uploads) / max(len(recent_uploads), 1),
            "most_popular_queries": self._get_top_queries(recent_searches, 10),
            "file_type_distribution": self._get_file_type_distribution(recent_uploads),
            "daily_activity": self._get_daily_activity(recent_searches, recent_uploads, days),
            "search_success_rate": self._calculate_search_success_rate(recent_searches),
            "system_metrics": data["system_metrics"]
        }
        
        return stats
    
    def _get_top_queries(self, searches: List[Dict], limit: int = 10) -> List[Dict]:
        """Get most popular search queries."""
        query_counts = Counter(s["query"] for s in searches)
        return [
            {"query": query, "count": count}
            for query, count in query_counts.most_common(limit)
        ]
    
    def _get_file_type_distribution(self, uploads: List[Dict]) -> Dict[str, int]:
        """Get distribution of uploaded file types."""
        return dict(Counter(u["file_type"] for u in uploads))
    
    def _get_daily_activity(self, searches: List[Dict], uploads: List[Dict], 
                           days: int) -> List[Dict]:
        """Get daily activity breakdown."""
        daily_stats = defaultdict(lambda: {"searches": 0, "uploads": 0})
        
        for search in searches:
            date = datetime.fromisoformat(search["timestamp"]).date()
            daily_stats[date.isoformat()]["searches"] += 1
        
        for upload in uploads:
            date = datetime.fromisoformat(upload["timestamp"]).date()
            daily_stats[date.isoformat()]["uploads"] += 1
        
        # Fill in missing days
        result = []
        for i in range(days):
            date = (datetime.now().date() - timedelta(days=i)).isoformat()
            result.append({
                "date": date,
                "searches": daily_stats[date]["searches"],
                "uploads": daily_stats[date]["uploads"]
            })
        
        return sorted(result, key=lambda x: x["date"])
    
    def _calculate_search_success_rate(self, searches: List[Dict]) -> float:
        """Calculate the rate of successful searches (searches that returned results)."""
        if not searches:
            return 0.0
        
        successful_searches = sum(1 for s in searches if s["results_count"] > 0)
        return (successful_searches / len(searches)) * 100

# Global analytics manager instance
analytics = AnalyticsManager() 